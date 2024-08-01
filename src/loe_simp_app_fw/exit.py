import atexit
import sys
import signal
from typing import ClassVar

from .cacher import GlobalCacheManager
from .logger import Logger


class Register:
    isRegistered: ClassVar[bool] = False

    @classmethod
    def register(cls) -> None:
        Logger.info(f"isRegister starts with value {cls.isRegistered}")
        if cls.isRegistered:
            Logger.warning("Trying to register the exit function multiple times")
            return
        Logger.info("Registering save_to_disk to execute at exit")
        atexit.register(cls.save_to_disk)
        Logger.info("Registering write_log_buffer to execute at exit")
        atexit.register(cls.write_log_buffer)
        Logger.info("Registering signal handler for CTRL+C")
        signal.signal(signal.SIGINT, cls.signal_handler_sigint)

        cls.isRegistered = True
        Logger.info(f"isRegister is set to {cls.isRegistered}")
        return

    @staticmethod
    def save_to_disk():
        Logger.debug("Cacher detects exit")
        if GlobalCacheManager._isSetup:
            GlobalCacheManager._suspend()
        else:
            Logger.warning("Cacher is never setup")

    @staticmethod
    def write_log_buffer():
        # Clean up logger buffer when crashing
        Logger.info("Prepare to shutdown logger in middleware")
        Logger._middleware.shutdown()

    @staticmethod
    def signal_handler_sigint(signal, frame) -> None:
        Logger.info("SIGINT received in all process")
        sys.exit() # This will run all the registered cleanup code
