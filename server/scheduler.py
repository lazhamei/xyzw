import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from models import ScheduledTask, Account, TaskExecutionLog

class TaskScheduler:
    _instance = None
    _scheduler: Optional[AsyncIOScheduler] = None
    _running_jobs: Dict[str, asyncio.Task] = {}
    _webhook_callback: Optional[Callable] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        jobstores = {
            'default': MemoryJobStore()
        }
        self._scheduler = AsyncIOScheduler(jobstores=jobstores)
        self._scheduler.add_listener(
            self._job_listener,
            EVENT_JOB_EXECUTED | EVENT_JOB_ERROR | EVENT_JOB_MISSED
        )

    def set_webhook_callback(self, callback: Callable):
        self._webhook_callback = callback

    async def _job_listener(self, event):
        if event.exception:
            print(f'任务执行错误: {event.exception}')
        elif event.retval is not None:
            print(f'任务执行完成: {event.retval}')

    def start(self):
        if not self._scheduler.running:
            self._scheduler.start()
            print('定时任务调度器已启动')

    def shutdown(self):
        if self._scheduler.running:
            self._scheduler.shutdown()
            print('定时任务调度器已关闭')

    def add_cron_job(self, task_id: str, cron_expression: str, func, *args, **kwargs):
        try:
            parts = cron_expression.split()
            if len(parts) != 5:
                raise ValueError('Cron表达式需要5个字段')

            trigger = CronTrigger(
                minute=parts[0],
                hour=parts[1],
                day=parts[2],
                month=parts[3],
                day_of_week=parts[4]
            )

            job = self._scheduler.add_job(
                func,
                trigger=trigger,
                id=task_id,
                replace_existing=True,
                *args,
                **kwargs
            )
            print(f'添加Cron任务: {task_id}, 表达式: {cron_expression}')
            return job
        except Exception as e:
            print(f'添加Cron任务失败: {e}')
            raise

    def add_daily_job(self, task_id: str, run_time: str, func, *args, **kwargs):
        try:
            parts = run_time.split(':')
            if len(parts) != 2:
                raise ValueError('时间格式应为 HH:MM')

            hour = int(parts[0])
            minute = int(parts[1])

            trigger = CronTrigger(hour=hour, minute=minute)

            job = self._scheduler.add_job(
                func,
                trigger=trigger,
                id=task_id,
                replace_existing=True,
                *args,
                **kwargs
            )
            print(f'添加每日任务: {task_id}, 时间: {run_time}')
            return job
        except Exception as e:
            print(f'添加每日任务失败: {e}')
            raise

    def remove_job(self, task_id: str):
        try:
            self._scheduler.remove_job(task_id)
            print(f'移除任务: {task_id}')
        except Exception as e:
            print(f'移除任务失败: {e}')

    def get_jobs(self) -> List[Dict[str, Any]]:
        jobs = []
        for job in self._scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run_time': str(job.next_run_time) if job.next_run_time else None,
                'trigger': str(job.trigger)
            })
        return jobs

    def pause_job(self, task_id: str):
        self._scheduler.pause_job(task_id)

    def resume_job(self, task_id: str):
        self._scheduler.resume_job(task_id)

    def run_job_now(self, task_id: str):
        job = self._scheduler.get_job(task_id)
        if job:
            job.modify(next_run_time=datetime.now())
        else:
            print(f'任务不存在: {task_id}')

def parse_cron_expression(cron_expr: str) -> Dict[str, Any]:
    parts = cron_expr.split()
    if len(parts) != 5:
        raise ValueError('Cron表达式需要5个字段: 分 时 日 月 周')

    return {
        'minute': parts[0],
        'hour': parts[1],
        'day': parts[2],
        'month': parts[3],
        'day_of_week': parts[4]
    }

async def execute_scheduled_task(task: ScheduledTask):
    from tasks import TaskExecutor

    print(f'开始执行定时任务: {task.name}')

    execution_id = f'{task.id}_{datetime.now().strftime("%Y%m%d%H%M%S")}'
    log_entry = TaskExecutionLog(
        id=execution_id,
        task_id=task.id,
        task_name=task.name,
        account_id='',
        account_name='',
        status='running',
        started_at=datetime.now().isoformat()
    )
    log_entry.save()

    accounts = []
    for account_id in task.account_ids:
        account = Account.get(account_id)
        if account:
            accounts.append(account)

    if not accounts:
        log_entry.status = 'failed'
        log_entry.message = '没有找到关联的账号'
        log_entry.save()
        print(f'任务 {task.name} 没有关联账号')
        return

    log_entry.account_id = ','.join([str(acc.id) for acc in accounts])
    log_entry.save()

    try:
        results = await TaskExecutor.execute_batch(
            accounts,
            task_type=task.task_type,
            task_config=task.task_config,
            concurrency=3
        )

        success_count = sum(1 for r in results if isinstance(r, dict) and r.get('status') == 'success')
        failed_count = len(results) - success_count

        log_entry.status = 'success' if failed_count == 0 else 'partial'
        log_entry.message = f'完成: 成功 {success_count}, 失败 {failed_count}'
        log_entry.details = {
            'results': [
                {'account_id': acc.id, 'status': r.get('status') if isinstance(r, dict) else 'error'}
                for acc, r in zip(accounts, results)
            ]
        }
    except Exception as e:
        log_entry.status = 'failed'
        log_entry.message = str(e)
    finally:
        log_entry.finished_at = datetime.now().isoformat()
        log_entry.save()

    print(f'定时任务 {task.name} 执行完成: {log_entry.status}')

def sync_tasks_to_scheduler():
    scheduler = TaskScheduler()
    tasks = ScheduledTask.get_enabled()

    for task in tasks:
        if task.run_type == 'cron':
            scheduler.add_cron_job(
                task.id,
                task.cron_expression,
                execute_scheduled_task,
                task
            )
        elif task.run_type == 'daily':
            scheduler.add_daily_job(
                task.id,
                task.run_time,
                execute_scheduled_task,
                task
            )

    print(f'同步 {len(tasks)} 个任务到调度器')
