import threading
from functools import wraps
import os
import tomllib
import inspect
import asyncio

class ConfigRead:
    """
    Reads the minder config and writes them to the given target object (like Template)
    """

    # Required config fields
    required_fields = [
        'name',
        'version',
    ]

    # Optional config fields
    optional_fields = [
        'description',
        'authors',
        'readme',
        'urls',
        'license',
        'python',  # Required python version
        'mind',    # Required mind version
        'install-requires',  # List of required libraries
        'requires-minders'   # List of required minders
    ]

    def __init__(self, target):
        self.target = target

        self.import_dir = os.path.dirname(inspect.stack()[1].filename).replace("\\", "/")
        self.config_path = f'{self.import_dir}/minder_config.toml'

        self.read_config()

    def read_config(self):
        try:
            with open(self.config_path, 'rb') as f:
                config = tomllib.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found at: {self.config_path}")
        except tomllib.TOMLDecodeError as e:
            raise ValueError(f"Invalid TOML format: {e}")

        # Получаем вложенную секцию minder
        minder_config = config.get('minder')
        if minder_config is None:
            raise ValueError("Missing [minder] section in config")

        # Assigning required fields
        for field in ConfigRead.required_fields:
            if field in minder_config:
                setattr(self.target, field.replace('-', '_'), minder_config[field])
            else:
                raise ValueError(f"Missing required field: {field}")

        # Assigning optional fields
        for field in ConfigRead.optional_fields:
            if field in minder_config:
                setattr(self.target, field.replace('-', '_'), minder_config[field])

def limit_concurrency(max_concurrent: int):
    # Семофор для синхронных вызовов
    sync_semaphore = threading.Semaphore(max_concurrent)
    # Семофор для асинхронных вызовов
    async_semaphore = asyncio.Semaphore(max_concurrent)

    def decorator(func):
        if inspect.iscoroutinefunction(func):
            # Асинхронная функция
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                async with async_semaphore:
                    return await func(*args, **kwargs)
            return async_wrapper
        else:
            # Синхронная функция
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                with sync_semaphore:
                    return func(*args, **kwargs)
            return sync_wrapper

    return decorator
