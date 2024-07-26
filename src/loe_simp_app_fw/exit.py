import atexit
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
        Logger._finish()
