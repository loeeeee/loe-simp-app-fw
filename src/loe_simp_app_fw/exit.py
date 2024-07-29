import atexit
import sys
import signal

from .cacher import GlobalCacheManager
from .logger import Logger

def register() -> None:
    @atexit.register
    def save_to_disk():
        Logger.debug("Cacher detects exit")
        if GlobalCacheManager._isSetup:
            GlobalCacheManager._suspend()
        else:
            Logger.warning("Cacher is never setup")

    @atexit.register
    def write_log_buffer():
        # Clean up logger buffer when crashing
        Logger._middleware.switch_backend_s_to_backend_m()
        Logger._middleware.shutdown()

    def signal_handler_sigint(signal, frame) -> None:
        Logger.info("SIGINT received in all process")
        sys.exit() # This will run all the registered cleanup code

    # Handle keyboard interrupt and exit gracefully instead of raising KeyBoardInterrupt everywhere
    signal.signal(signal.SIGINT, signal_handler_sigint)
