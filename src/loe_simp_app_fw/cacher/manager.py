from typing import Optional, TypeAlias, ClassVar, Tuple, Dict
from datetime import timedelta, date

from .model import Cached, HashKey, Identifier
from ..logger import Logger

AbsolutePath: TypeAlias = str
RelativePath: TypeAlias = str

class CacheManager:

    # Settings
    _cache_folder: ClassVar[AbsolutePath]
    _time_to_live: ClassVar[timedelta]

    # Override
    _neverExpire: ClassVar[bool]
    _readOnly: ClassVar[bool]
    _disable: ClassVar[bool]

    # Variables
    _cache_map: ClassVar[Dict[HashKey, Tuple[date, RelativePath]]] = {}
    _isSetup: ClassVar[bool] = False

    # Constant
    _meta_file_name: str = "meta.json"

    # ---------------------------- API ----------------------------

    @classmethod
    def get(cls, identifier: Identifier) -> Cached:
        return

    @classmethod
    def save(
        cls, 
        identifier: Identifier, 
        content: str, 
        *args, 
        extension_name: str = "txt", 
        time_to_live: Optional[int] = None, 
        **kwargs
        ) -> None:
        return

    @classmethod
    def setup(
        cls, 
        cache_folder: AbsolutePath, 
        days_to_expire: int, 
        *args, 
        neverExpire: bool = False, 
        readOnly: bool = False, 
        disable: bool = False, 
        **kwargs
        ) -> None:
        # Store settings
        cls._cache_folder = cache_folder
        cls._days_to_expire = timedelta(days=days_to_expire)
        cls._neverExpire = neverExpire
        cls._readOnly = readOnly
        cls._disable = disable
        ## Sanity check
        if disable and (readOnly or neverExpire):
            Logger.warning(f"Ignore cache and (read only, never expire) are incompatible parameters. Only ignore cache will be respected")
        
        # Setup Cacher
        cls._resume()

        # Flag it
        cls._isSetup = True

    # ---------------------------- Internal Methods ----------------------------

    @classmethod
    def _resume(cls) -> None:
        return

    @classmethod
    def _suspend(cls) -> None:
        return

    @classmethod
    def _get_unhandled(cls, identifier: Identifier) -> None:
        return

    @classmethod
    def _save_unhandled(
        cls,
        identifier: Identifier, 
        content: str, 
        extension_name: str, 
        time_to_live: Optional[int],
        ) -> None:
        return