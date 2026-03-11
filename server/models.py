import json
import os
from datetime import datetime
from typing import Optional, Dict, Any, List
from cryptography.fernet import Fernet

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

class JSONFileDB:
    def __init__(self, filename: str):
        self.filepath = os.path.join(DATA_DIR, filename)
        self._data: Dict[str, Any] = {}
        self._load()

    def _load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    self._data = json.load(f)
            except Exception:
                self._data = {}

    def _save(self):
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    def get(self, key: str, default=None):
        return self._data.get(key, default)

    def set(self, key: str, value: Any):
        self._data[key] = value
        self._save()

    def delete(self, key: str):
        if key in self._data:
            del self._data[key]
            self._save()

    def get_all(self) -> Dict[str, Any]:
        return self._data.copy()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()

    def __len__(self):
        return len(self._data)

class EncryptedTokenDB:
    def __init__(self, filename: str, key: bytes = None):
        self.filepath = os.path.join(DATA_DIR, filename)
        if key is None:
            key_file = os.path.join(DATA_DIR, '.key')
            if os.path.exists(key_file):
                with open(key_file, 'rb') as f:
                    self.key = f.read()
            else:
                self.key = Fernet.generate_key()
                with open(key_file, 'wb') as f:
                    f.write(self.key)
        else:
            self.key = key
        self.cipher = Fernet(self.key)
        self._data: Dict[str, str] = {}
        self._load()

    def _load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'rb') as f:
                    encrypted_data = f.read()
                    if encrypted_data:
                        decrypted = self.cipher.decrypt(encrypted_data)
                        self._data = json.loads(decrypted)
            except Exception:
                self._data = {}

    def _save(self):
        encrypted = self.cipher.encrypt(json.dumps(self._data).encode())
        with open(self.filepath, 'wb') as f:
            f.write(encrypted)

    def get(self, key: str, default=None) -> Optional[str]:
        return self._data.get(key, default)

    def set(self, key: str, value: str):
        self._data[key] = value
        self._save()

    def delete(self, key: str):
        if key in self._data:
            del self._data[key]
            self._save()

    def get_all(self) -> Dict[str, str]:
        return self._data.copy()

class Account:
    _db = JSONFileDB('accounts.json')

    def __init__(
        self,
        id: str,
        name: str,
        import_method: str,
        server: str = '',
        ws_url: str = '',
        role_id: str = '',
        role_index: int = 0,
        bin_data: str = '',
        metadata: Dict[str, Any] = None,
        created_at: str = None,
        last_used: str = None
    ):
        self.id = id
        self.name = name
        self.import_method = import_method
        self.server = server
        self.ws_url = ws_url
        self.role_id = role_id
        self.role_index = role_index
        self.bin_data = bin_data
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.now().isoformat()
        self.last_used = last_used or datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'import_method': self.import_method,
            'server': self.server,
            'ws_url': self.ws_url,
            'role_id': self.role_id,
            'role_index': self.role_index,
            'bin_data': self.bin_data,
            'metadata': self.metadata,
            'created_at': self.created_at,
            'last_used': self.last_used
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Account':
        return Account(
            id=data.get('id', ''),
            name=data.get('name', ''),
            import_method=data.get('import_method', 'manual'),
            server=data.get('server', ''),
            ws_url=data.get('ws_url', ''),
            role_id=data.get('role_id', ''),
            role_index=data.get('role_index', 0),
            bin_data=data.get('bin_data', ''),
            metadata=data.get('metadata', {}),
            created_at=data.get('created_at'),
            last_used=data.get('last_used')
        )

    def save(self):
        Account._db.set(self.id, self.to_dict())

    @staticmethod
    def get(account_id: str) -> Optional['Account']:
        data = Account._db.get(account_id)
        if data:
            return Account.from_dict(data)
        return None

    @staticmethod
    def get_all() -> List['Account']:
        return [Account.from_dict(v) for v in Account._db.values()]

    @staticmethod
    def delete(account_id: str):
        Account._db.delete(account_id)

    def update_last_used(self):
        self.last_used = datetime.now().isoformat()
        self.save()

class ScheduledTask:
    _db = JSONFileDB('scheduled_tasks.json')

    def __init__(
        self,
        id: str,
        name: str,
        account_ids: List[str],
        task_type: str,
        run_type: str,
        run_time: str = '',
        cron_expression: str = '',
        enabled: bool = True,
        task_config: Dict[str, Any] = None,
        created_at: str = None,
        updated_at: str = None
    ):
        self.id = id
        self.name = name
        self.account_ids = account_ids
        self.task_type = task_type
        self.run_type = run_type
        self.run_time = run_time
        self.cron_expression = cron_expression
        self.enabled = enabled
        self.task_config = task_config or {}
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'account_ids': self.account_ids,
            'task_type': self.task_type,
            'run_type': self.run_type,
            'run_time': self.run_time,
            'cron_expression': self.cron_expression,
            'enabled': self.enabled,
            'task_config': self.task_config,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ScheduledTask':
        return ScheduledTask(
            id=data.get('id', ''),
            name=data.get('name', ''),
            account_ids=data.get('account_ids', []),
            task_type=data.get('task_type', 'daily'),
            run_type=data.get('run_type', 'daily'),
            run_time=data.get('run_time', ''),
            cron_expression=data.get('cron_expression', ''),
            enabled=data.get('enabled', True),
            task_config=data.get('task_config', {}),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    def save(self):
        self.updated_at = datetime.now().isoformat()
        ScheduledTask._db.set(self.id, self.to_dict())

    @staticmethod
    def get(task_id: str) -> Optional['ScheduledTask']:
        data = ScheduledTask._db.get(task_id)
        if data:
            return ScheduledTask.from_dict(data)
        return None

    @staticmethod
    def get_all() -> List['ScheduledTask']:
        return [ScheduledTask.from_dict(v) for v in ScheduledTask._db.values()]

    @staticmethod
    def get_enabled() -> List['ScheduledTask']:
        return [ScheduledTask.from_dict(v) for v in ScheduledTask._db.values() if v.get('enabled', True)]

    @staticmethod
    def delete(task_id: str):
        ScheduledTask._db.delete(task_id)

class TaskExecutionLog:
    _db = JSONFileDB('task_execution_logs.json')

    def __init__(
        self,
        id: str,
        task_id: str,
        task_name: str,
        account_id: str,
        account_name: str,
        status: str,
        message: str = '',
        started_at: str = None,
        finished_at: str = None,
        details: Dict[str, Any] = None
    ):
        self.id = id
        self.task_id = task_id
        self.task_name = task_name
        self.account_id = account_id
        self.account_name = account_name
        self.status = status
        self.message = message
        self.started_at = started_at or datetime.now().isoformat()
        self.finished_at = finished_at
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'task_id': self.task_id,
            'task_name': self.task_name,
            'account_id': self.account_id,
            'account_name': self.account_name,
            'status': self.status,
            'message': self.message,
            'started_at': self.started_at,
            'finished_at': self.finished_at,
            'details': self.details
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'TaskExecutionLog':
        return TaskExecutionLog(
            id=data.get('id', ''),
            task_id=data.get('task_id', ''),
            task_name=data.get('task_name', ''),
            account_id=data.get('account_id', ''),
            account_name=data.get('account_name', ''),
            status=data.get('status', 'pending'),
            message=data.get('message', ''),
            started_at=data.get('started_at'),
            finished_at=data.get('finished_at'),
            details=data.get('details', {})
        )

    def save(self):
        TaskExecutionLog._db.set(self.id, self.to_dict())

    @staticmethod
    def get(log_id: str) -> Optional['TaskExecutionLog']:
        data = TaskExecutionLog._db.get(log_id)
        if data:
            return TaskExecutionLog.from_dict(data)
        return None

    @staticmethod
    def get_by_task(task_id: str, limit: int = 50) -> List['TaskExecutionLog']:
        all_logs = [TaskExecutionLog.from_dict(v) for v in TaskExecutionLog._db.values()]
        return [log for log in all_logs if log.task_id == task_id][-limit:]

    @staticmethod
    def get_recent(limit: int = 100) -> List['TaskExecutionLog']:
        all_logs = [TaskExecutionLog.from_dict(v) for v in TaskExecutionLog._db.values()]
        all_logs.sort(key=lambda x: x.started_at, reverse=True)
        return all_logs[:limit]

    @staticmethod
    def delete(log_id: str):
        TaskExecutionLog._db.delete(log_id)

    @staticmethod
    def clear_old(days: int = 7):
        from datetime import timedelta
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        for log_id, data in list(TaskExecutionLog._db.items()):
            if data.get('started_at', '') < cutoff:
                TaskExecutionLog._db.delete(log_id)
