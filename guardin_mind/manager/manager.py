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
        'description',
        'authors'
    ]
    # Optional config fields
    optional_fields = [
        'long_description',
        'author_email',
        'url',
        'license',
        'python_requires',
        'mind_requires',
        'install_requires'
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

        # Assigning the required fields
        for field in ConfigRead.required_fields:
            if field in config:
                setattr(self.target, field, config[field])
            else:
                raise ValueError(f"Missing required field: {field}")

        # Processing optional fields
        for field in ConfigRead.optional_fields:
            if field in config:
                setattr(self.target, field, config[field])


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
