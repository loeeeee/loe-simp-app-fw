import atexit
import sys
import signal

from .cacher import GlobalCacheManager
from .logger import Logger


class Register:
    @classmethod
    def register(cls, ) -> None:
        atexit.register(cls.save_to_disk)
        atexit.register(cls.write_log_buffer)
        signal.signal(signal.SIGINT, cls.signal_handler_sigint)
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
        Logger._middleware.shutdown()

    @staticmethod
    def signal_handler_sigint(signal, frame) -> None:
        Logger.info("SIGINT received in all process")
        sys.exit() # This will run all the registered cleanup code
