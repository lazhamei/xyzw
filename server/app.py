import os
import json
import uuid
import base64
import asyncio
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from models import Account, ScheduledTask, TaskExecutionLog
from scheduler import TaskScheduler, sync_tasks_to_scheduler
from tasks import TaskExecutor

app = Flask(__name__)
CORS(app)

scheduler = TaskScheduler()

def validate_cron_expression(cron_expr: str) -> tuple:
    parts = cron_expr.split()
    if len(parts) != 5:
        return False, 'Cron表达式需要5个字段: 分 时 日 月 周'
    return True, ''

def validate_daily_time(time_str: str) -> tuple:
    try:
        parts = time_str.split(':')
        if len(parts) != 2:
            return False, '时间格式应为 HH:MM'
        hour = int(parts[0])
        minute = int(parts[1])
        if hour < 0 or hour > 23:
            return False, '小时应在0-23之间'
        if minute < 0 or minute > 59:
            return False, '分钟应在0-59之间'
        return True, ''
    except ValueError:
        return False, '时间格式错误'

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

@app.route('/accounts', methods=['GET'])
def get_accounts():
    accounts = Account.get_all()
    return jsonify({
        'success': True,
        'data': [acc.to_dict() for acc in accounts]
    })

@app.route('/accounts/<account_id>', methods=['GET'])
def get_account(account_id):
    account = Account.get(account_id)
    if not account:
        return jsonify({'success': False, 'error': '账号不存在'}), 404
    return jsonify({'success': True, 'data': account.to_dict()})

@app.route('/accounts', methods=['POST'])
def create_account():
    data = request.get_json() or {}

    name = data.get('name', '')
    import_method = data.get('importMethod', 'manual')
    server = data.get('server', '')
    ws_url = data.get('wsUrl', '')
    role_id = data.get('roleId', '')
    role_index = data.get('roleIndex', 0)
    bin_data = data.get('binData', '')
    metadata = data.get('metadata', {})

    if not name:
        return jsonify({'success': False, 'error': '名称不能为空'}), 400

    account_id = str(uuid.uuid4())
    account = Account(
        id=account_id,
        name=name,
        import_method=import_method,
        server=server,
        ws_url=ws_url,
        role_id=role_id,
        role_index=role_index,
        bin_data=bin_data,
        metadata=metadata
    )
    account.save()

    return jsonify({
        'success': True,
        'data': account.to_dict()
    })

@app.route('/accounts/<account_id>', methods=['PUT'])
def update_account(account_id):
    account = Account.get(account_id)
    if not account:
        return jsonify({'success': False, 'error': '账号不存在'}), 404

    data = request.get_json() or {}

    if 'name' in data:
        account.name = data['name']
    if 'server' in data:
        account.server = data['server']
    if 'wsUrl' in data:
        account.ws_url = data['wsUrl']
    if 'roleId' in data:
        account.role_id = data['roleId']
    if 'binData' in data:
        account.bin_data = data['binData']
    if 'metadata' in data:
        account.metadata = data['metadata']

    account.save()

    return jsonify({
        'success': True,
        'data': account.to_dict()
    })

@app.route('/accounts/<account_id>', methods=['DELETE'])
def delete_account(account_id):
    account = Account.get(account_id)
    if not account:
        return jsonify({'success': False, 'error': '账号不存在'}), 404

    Account.delete(account_id)

    return jsonify({'success': True})

@app.route('/accounts/import', methods=['POST'])
def import_accounts():
    if 'file' in request.files:
        file = request.files['file']
        filename = secure_filename(file.filename)

        try:
            content = file.read().decode('utf-8')
            data = json.loads(content)
        except Exception as e:
            return jsonify({'success': False, 'error': f'文件解析失败: {str(e)}'}), 400

        if 'gameTokens' in data:
            tokens = data['gameTokens']
        elif 'accounts' in data:
            tokens = data['accounts']
        elif isinstance(data, list):
            tokens = data
        else:
            tokens = [data]

    else:
        data = request.get_json() or {}

        if 'gameTokens' in data:
            tokens = data['gameTokens']
        elif 'accounts' in data:
            tokens = data['accounts']
        elif 'tokens' in data:
            tokens = data['tokens']
        else:
            tokens = [data]

    imported = []
    errors = []

    for idx, token_data in enumerate(tokens):
        try:
            name = token_data.get('name', f'账号_{idx+1}')
            import_method = token_data.get('importMethod') or token_data.get('import_method', 'manual')
            server = token_data.get('server', '')
            ws_url = token_data.get('wsUrl') or token_data.get('ws_url', '')
            role_id = token_data.get('roleId') or token_data.get('role_id', '')
            role_index = token_data.get('roleIndex') or token_data.get('role_index', 0)

            bin_data = token_data.get('binData') or token_data.get('bin_data', '')
            if not bin_data and 'token' in token_data:
                bin_data = token_data['token']
            if not bin_data and 'gameToken' in token_data:
                bin_data = token_data['gameToken']

            metadata = token_data.get('metadata', {})

            account_id = str(uuid.uuid4())
            account = Account(
                id=account_id,
                name=name,
                import_method=import_method,
                server=server,
                ws_url=ws_url,
                role_id=role_id,
                role_index=role_index,
                bin_data=bin_data,
                metadata=metadata
            )
            account.save()
            imported.append(account.to_dict())

        except Exception as e:
            errors.append(f'导入第{idx+1}条失败: {str(e)}')

    return jsonify({
        'success': True,
        'imported': len(imported),
        'errors': errors,
        'data': imported
    })

@app.route('/accounts/export', methods=['GET'])
def export_accounts():
    accounts = Account.get_all()
    export_data = {
        'exportedAt': datetime.now().isoformat(),
        'accounts': [acc.to_dict() for acc in accounts]
    }
    return jsonify(export_data)

@app.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = ScheduledTask.get_all()
    return jsonify({
        'success': True,
        'data': [task.to_dict() for task in tasks]
    })

@app.route('/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    task = ScheduledTask.get(task_id)
    if not task:
        return jsonify({'success': False, 'error': '任务不存在'}), 404
    return jsonify({'success': True, 'data': task.to_dict()})

@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json() or {}

    name = data.get('name', '')
    account_ids = data.get('accountIds', [])
    task_type = data.get('taskType', 'daily')
    run_type = data.get('runType', 'daily')
    run_time = data.get('runTime', '')
    cron_expression = data.get('cronExpression', '')
    enabled = data.get('enabled', True)
    task_config = data.get('taskConfig', {})

    if not name:
        return jsonify({'success': False, 'error': '任务名称不能为空'}), 400

    if not account_ids:
        return jsonify({'success': False, 'error': '请选择至少一个账号'}), 400

    if run_type == 'daily':
        valid, msg = validate_daily_time(run_time)
        if not valid:
            return jsonify({'success': False, 'error': msg}), 400
    elif run_type == 'cron':
        valid, msg = validate_cron_expression(cron_expression)
        if not valid:
            return jsonify({'success': False, 'error': msg}), 400

    task_id = str(uuid.uuid4())
    task = ScheduledTask(
        id=task_id,
        name=name,
        account_ids=account_ids,
        task_type=task_type,
        run_type=run_type,
        run_time=run_time,
        cron_expression=cron_expression,
        enabled=enabled,
        task_config=task_config
    )
    task.save()

    if enabled:
        if run_type == 'cron':
            scheduler.add_cron_job(task_id, cron_expression, execute_scheduled_task_wrapper, task)
        elif run_type == 'daily':
            scheduler.add_daily_job(task_id, run_time, execute_scheduled_task_wrapper, task)

    return jsonify({
        'success': True,
        'data': task.to_dict()
    })

@app.route('/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    task = ScheduledTask.get(task_id)
    if not task:
        return jsonify({'success': False, 'error': '任务不存在'}), 404

    data = request.get_json() or {}

    if 'name' in data:
        task.name = data['name']
    if 'accountIds' in data:
        task.account_ids = data['accountIds']
    if 'taskType' in data:
        task.task_type = data['taskType']
    if 'runType' in data:
        task.run_type = data['runType']
    if 'runTime' in data:
        valid, msg = validate_daily_time(data['runTime'])
        if not valid:
            return jsonify({'success': False, 'error': msg}), 400
        task.run_time = data['runTime']
    if 'cronExpression' in data:
        valid, msg = validate_cron_expression(data['cronExpression'])
        if not valid:
            return jsonify({'success': False, 'error': msg}), 400
        task.cron_expression = data['cronExpression']
    if 'enabled' in data:
        task.enabled = data['enabled']
    if 'taskConfig' in data:
        task.task_config = data['taskConfig']

    scheduler.remove_job(task_id)

    if task.enabled:
        if task.run_type == 'cron':
            scheduler.add_cron_job(task_id, task.cron_expression, execute_scheduled_task_wrapper, task)
        elif task.run_type == 'daily':
            scheduler.add_daily_job(task_id, task.run_time, execute_scheduled_task_wrapper, task)

    task.save()

    return jsonify({
        'success': True,
        'data': task.to_dict()
    })

@app.route('/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = ScheduledTask.get(task_id)
    if not task:
        return jsonify({'success': False, 'error': '任务不存在'}), 404

    scheduler.remove_job(task_id)
    ScheduledTask.delete(task_id)

    return jsonify({'success': True})

@app.route('/tasks/<task_id>/run', methods=['POST'])
def run_task_now(task_id):
    task = ScheduledTask.get(task_id)
    if not task:
        return jsonify({'success': False, 'error': '任务不存在'}), 404

    asyncio.create_task(execute_scheduled_task_wrapper(task))

    return jsonify({
        'success': True,
        'message': '任务已开始执行'
    })

@app.route('/tasks/<task_id>/toggle', methods=['POST'])
def toggle_task(task_id):
    task = ScheduledTask.get(task_id)
    if not task:
        return jsonify({'success': False, 'error': '任务不存在'}), 404

    task.enabled = not task.enabled

    if task.enabled:
        if task.run_type == 'cron':
            scheduler.add_cron_job(task_id, task.cron_expression, execute_scheduled_task_wrapper, task)
        elif task.run_type == 'daily':
            scheduler.add_daily_job(task_id, task.run_time, execute_scheduled_task_wrapper, task)
    else:
        scheduler.remove_job(task_id)

    task.save()

    return jsonify({
        'success': True,
        'data': task.to_dict()
    })

async def execute_scheduled_task_wrapper(task: ScheduledTask):
    from scheduler import execute_scheduled_task
    await execute_scheduled_task(task)

@app.route('/logs', methods=['GET'])
def get_logs():
    limit = request.args.get('limit', 100, type=int)
    task_id = request.args.get('taskId')

    if task_id:
        logs = TaskExecutionLog.get_by_task(task_id, limit)
    else:
        logs = TaskExecutionLog.get_recent(limit)

    return jsonify({
        'success': True,
        'data': [log.to_dict() for log in logs]
    })

@app.route('/logs/<log_id>', methods=['GET'])
def get_log(log_id):
    log = TaskExecutionLog.get(log_id)
    if not log:
        return jsonify({'success': False, 'error': '日志不存在'}), 404
    return jsonify({'success': True, 'data': log.to_dict()})

@app.route('/scheduler/status', methods=['GET'])
def scheduler_status():
    jobs = scheduler.get_jobs()
    return jsonify({
        'success': True,
        'running': scheduler._scheduler.running if scheduler._scheduler else False,
        'jobs': jobs
    })

@app.route('/scheduler/sync', methods=['POST'])
def sync_scheduler():
    scheduler.shutdown()
    scheduler._initialize()
    scheduler.start()
    sync_tasks_to_scheduler()
    return jsonify({
        'success': True,
        'message': '调度器已同步'
    })

@app.route('/validate/cron', methods=['POST'])
def validate_cron():
    data = request.get_json() or {}
    cron_expr = data.get('expression', '')

    valid, msg = validate_cron_expression(cron_expr)
    return jsonify({
        'valid': valid,
        'message': msg if not valid else 'Cron表达式格式正确'
    })

@app.route('/validate/time', methods=['POST'])
def validate_time():
    data = request.get_json() or {}
    time_str = data.get('time', '')

    valid, msg = validate_daily_time(time_str)
    return jsonify({
        'valid': valid,
        'message': msg if not valid else '时间格式正确'
    })

if __name__ == '__main__':
    scheduler.start()
    sync_tasks_to_scheduler()
    app.run(host='0.0.0.0', port=5000, debug=True)
