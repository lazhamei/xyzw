import json
import asyncio
import requests
import base64
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from models import Account, TaskExecutionLog

DEFAULT_WS_URL = 'wss://xxz-ws.hortorgames.com/'

class GameClient:
    def __init__(self, account: Account, ws_url: str = None):
        self.account = account
        self.ws_url = ws_url or account.ws_url or DEFAULT_WS_URL
        self.token = None
        self._ws = None
        self._connected = False
        self._message_id = 0
        self._pending_requests: Dict[int, asyncio.Future] = {}
        self._log_callback: Optional[Callable] = None

    def set_log_callback(self, callback: Callable[[str, str], None]):
        self._log_callback = callback

    def _log(self, message: str, level: str = 'info'):
        if self._log_callback:
            self._log_callback(message, level)
        print(f'[{level}] {message}')

    async def connect(self) -> bool:
        self._log(f'正在连接 {self.account.name}...')
        try:
            token_data = self._parse_token()
            if not token_data:
                self._log(f'Token解析失败', 'error')
                return False

            self.token = token_data.get('token') or token_data.get('gameToken')
            if not self.token:
                self._log(f'Token为空', 'error')
                return False

            ws_url = f'{self.ws_url}?token={self.token}'
            self._ws = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None,
                    self._create_websocket_sync,
                    ws_url
                ),
                timeout=15
            )
            self._connected = True
            self._log(f'连接成功', 'success')
            return True
        except Exception as e:
            self._log(f'连接失败: {str(e)}', 'error')
            return False

    def _create_websocket_sync(self, url: str):
        import websocket
        ws = websocket.WebSocketApp(
            url,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
            on_open=self._on_open
        )
        ws.run_forever(ping_interval=30)
        return ws

    def _on_message(self, ws, message):
        try:
            data = json.loads(message)
            seq = data.get('seq')
            if seq and seq in self._pending_requests:
                future = self._pending_requests.pop(seq)
                future.set_result(data)
        except Exception as e:
            print(f'WebSocket消息处理错误: {e}')

    def _on_error(self, ws, error):
        self._log(f'WebSocket错误: {error}', 'error')

    def _on_close(self, ws, close_status_code, close_msg):
        self._log(f'WebSocket连接关闭', 'info')
        self._connected = False

    def _on_open(self, ws):
        self._log('WebSocket连接打开', 'info')

    def _parse_token(self) -> Optional[Dict[str, Any]]:
        try:
            bin_data = self.account.bin_data
            if not bin_data:
                return None

            if bin_data.startswith('data:'):
                bin_data = bin_data.split(',')[1]

            decoded = base64.b64decode(bin_data)
            token_json = decoded.decode('utf-8') if isinstance(decoded, bytes) else decoded
            return json.loads(token_json)
        except Exception as e:
            self._log(f'Token解析错误: {e}', 'error')
            return None

    def _get_next_seq(self) -> int:
        self._message_id += 1
        return self._message_id

    async def send_command(self, cmd: str, params: Dict[str, Any] = None, timeout: float = 8.0) -> Dict[str, Any]:
        if not self._connected or not self._ws:
            if not await self.connect():
                raise Exception('WebSocket未连接')

        seq = self._get_next_seq()
        message = {
            'cmd': cmd,
            'params': params or {},
            'seq': seq
        }

        future = asyncio.Future()
        self._pending_requests[seq] = future

        try:
            self._ws.send(json.dumps(message))
            result = await asyncio.wait_for(future, timeout=timeout)
            return result
        except asyncio.TimeoutError:
            self._pending_requests.pop(seq, None)
            raise Exception(f'命令 {cmd} 超时')
        except Exception as e:
            self._pending_requests.pop(seq, None)
            raise Exception(f'命令 {cmd} 执行失败: {str(e)}')

    async def close(self):
        if self._ws:
            try:
                self._ws.close()
            except Exception:
                pass
        self._connected = False

class TaskRunner:
    def __init__(self, account: Account, task_config: Dict[str, Any] = None):
        self.account = account
        self.task_config = task_config or {}
        self.client: Optional[GameClient] = None
        self._logs: List[Dict[str, str]] = []

    def add_log(self, message: str, level: str = 'info'):
        log_entry = {
            'time': datetime.now().strftime('%H:%M:%S'),
            'message': message,
            'type': level
        }
        self._logs.append(log_entry)

    def get_logs(self) -> List[Dict[str, str]]:
        return self._logs.copy()

    async def run_daily_tasks(self):
        self.add_log(f'开始执行每日任务: {self.account.name}')
        execution_id = f'{self.account.id}_{datetime.now().strftime("%Y%m%d%H%M%S")}'
        log_entry = TaskExecutionLog(
            id=execution_id,
            task_id='',
            task_name='每日任务',
            account_id=self.account.id,
            account_name=self.account.name,
            status='running',
            started_at=datetime.now().isoformat()
        )
        log_entry.save()

        try:
            self.client = GameClient(self.account)
            self.client.set_log_callback(lambda msg, lvl: self.add_log(msg, lvl))

            if not await self.client.connect():
                raise Exception('无法连接游戏服务器')

            role_info = await self.client.send_command('role_getinfo', {})
            if not role_info.get('role'):
                raise Exception('获取角色信息失败')

            role_data = role_info['role']
            completed_tasks = role_data.get('dailyTask', {}).get('complete', {})
            is_task_completed = lambda tid: completed_tasks.get(str(tid)) == -1

            task_list = []

            if not is_task_completed(2):
                task_list.append(('分享游戏', 'system_mysharecallback', {'isSkipShareCard': True, 'type': 2}))

            if not is_task_completed(3):
                task_list.append(('赠送好友金币', 'friend_batch', {}))

            if not is_task_completed(4):
                task_list.append(('免费招募', 'hero_recruit', {'recruitType': 3, 'recruitNumber': 1}))
                if self.task_config.get('payRecruit', True):
                    task_list.append(('付费招募', 'hero_recruit', {'recruitType': 1, 'recruitNumber': 1}))

            if not is_task_completed(5):
                task_list.append(('领取挂机奖励', 'system_claimhangupreward', {}))
                for i in range(4):
                    task_list.append((f'挂机加钟 {i+1}', 'system_mysharecallback', {'isSkipShareCard': True, 'type': 2}))

            if not is_task_completed(7):
                task_list.append(('开启木质宝箱', 'item_openbox', {'itemId': 2001, 'number': 10}))

            task_list.append(('停止盐罐计时', 'bottlehelper_stop', {}))
            task_list.append(('开始盐罐计时', 'bottlehelper_start', {}))

            if not is_task_completed(14):
                task_list.append(('领取盐罐奖励', 'bottlehelper_claim', {}))

            if not is_task_completed(13):
                hour = datetime.now().hour
                if 6 <= hour <= 22:
                    task_list.append(('竞技场战斗', 'arena_startarea', {}))
                    for i in range(3):
                        task_list.append((f'竞技场战斗{i+1}', 'arena_getareatarget', {}))

            task_list.extend([
                ('福利签到', 'system_signinreward', {}),
                ('俱乐部签到', 'legion_signin', {}),
                ('领取每日礼包', 'discount_claimreward', {}),
                ('领取每日免费奖励', 'collection_claimfreereward', {}),
                ('领取免费礼包', 'card_claimreward', {}),
                ('领取永久卡礼包', 'card_claimreward', {'cardId': 4003}),
                ('领取邮件奖励', 'mail_claimallattachment', {}),
                ('珍宝阁列表', 'collection_goodslist', {}),
                ('珍宝阁免费礼包', 'collection_claimfreereward', {}),
            ])

            for task_id in range(1, 11):
                task_list.append((f'领取任务奖励{task_id}', 'task_claimdailypoint', {'taskId': task_id}))

            task_list.extend([
                ('领取日常任务奖励', 'task_claimdailyreward', {}),
                ('领取周常任务奖励', 'task_claimweekreward', {}),
                ('领取通行证奖励', 'activity_recyclewarorderrewardclaim', {'actId': 1}),
            ])

            total_tasks = len(task_list)
            self.add_log(f'共 {total_tasks} 个任务待执行')

            for idx, (name, cmd, params) in enumerate(task_list):
                try:
                    await self.client.send_command(cmd, params)
                    self.add_log(f'✓ {name}', 'success')
                except Exception as e:
                    self.add_log(f'✗ {name}: {str(e)}', 'error')

                await asyncio.sleep(0.5)

            self.add_log('所有任务执行完成', 'success')
            log_entry.status = 'success'
            log_entry.message = '执行完成'

        except Exception as e:
            self.add_log(f'执行失败: {str(e)}', 'error')
            log_entry.status = 'failed'
            log_entry.message = str(e)
        finally:
            log_entry.finished_at = datetime.now().isoformat()
            log_entry.details = {'logs': self._logs}
            log_entry.save()

            if self.client:
                await self.client.close()

        return {
            'execution_id': execution_id,
            'logs': self._logs,
            'status': log_entry.status
        }

class TaskExecutor:
    @staticmethod
    async def execute_task(account: Account, task_type: str = 'daily', task_config: Dict[str, Any] = None) -> Dict[str, Any]:
        runner = TaskRunner(account, task_config)

        if task_type == 'daily':
            result = await runner.run_daily_tasks()
        else:
            raise ValueError(f'未知任务类型: {task_type}')

        return result

    @staticmethod
    async def execute_batch(accounts: List[Account], task_type: str = 'daily', task_config: Dict[str, Any] = None, concurrency: int = 3) -> List[Dict[str, Any]]:
        semaphore = asyncio.Semaphore(concurrency)

        async def run_with_semaphore(account: Account):
            async with semaphore:
                return await TaskExecutor.execute_task(account, task_type, task_config)

        tasks = [run_with_semaphore(acc) for acc in accounts]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        return results
