import atexit
from typing import ClassVar

from .logger import Logger
from .cacher import CacheManager
from .prometheus import Prometheus


class Register:
    isRegistered: ClassVar[bool] = False

    @classmethod
    def register(cls) -> None:
        Logger.debug(f"isRegister starts with value {cls.isRegistered}")
        if cls.isRegistered:
            Logger.warning("Trying to register the exit function multiple times")
            return
        Logger.debug("Registering write_log_buffer to execute at exit")
        atexit.register(cls.write_log_buffer)
        Logger.debug("Registering save_to_disk to execute at exit")
        atexit.register(cls.save_cache_to_disk)
        Logger.debug("Registering write_monitoring_result to execute at exit")
        atexit.register(cls.write_monitoring_result)

        cls.isRegistered = True
        Logger.debug(f"isRegister is set to {cls.isRegistered}")
        return

    @staticmethod
    def save_cache_to_disk():
        Logger.debug("Save cache to disk")
        CacheManager.core.save()
        Logger.debug("Finished")

    @staticmethod
    def write_monitoring_result():
        Prometheus.summary()
        return

    @staticmethod
    def write_log_buffer():
        # Clean up logger buffer when crashing
        Logger.info("Prepare to shutdown logger in middleware")
        Logger._middleware.shutdown()
    