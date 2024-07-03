from typing import ClassVar, Dict, Optional, Tuple, TypeAlias
from datetime import date, timedelta
from .logger import Logger
import hashlib
import os
import atexit
import json

# Typings
AbsolutePath: TypeAlias = str
RelativePath: TypeAlias = str
Identifier: TypeAlias = str
HashKey: TypeAlias = str


class CacheMiss(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class CacheCorrupt(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class CacheNotFound(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class CacheExpired(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class GlobalCacheManager:

    # Settings
    _cache_folder: ClassVar[AbsolutePath]
    _days_to_expire: ClassVar[timedelta]

    # Override
    _neverExpire: ClassVar[bool]
    _readOnly: ClassVar[bool]
    _disable: ClassVar[bool]

    # Variables
    _cache_map: ClassVar[Dict[HashKey, Tuple[date, RelativePath]]] = {}
    _today: date = date.today()
    _isSetup: ClassVar[bool] = False

    # Constant
    _meta_file_name: str = "meta.json"

    @classmethod
    def setup(cls, cache_folder: AbsolutePath, days_to_expire: int, neverExpire: bool = False, readOnly: bool = False, disable: bool = False) -> None:
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

    @classmethod
    def get(cls, identifier: Identifier) -> Optional[str]:
        if cls._disable:
            return

        try:
            cached = cls._get_unhandled(identifier)
        except CacheMiss:
            pass
        except CacheExpired:
            pass
        except CacheNotFound:
            pass
        except CacheCorrupt:
            pass
        else:
            return cached

    @classmethod
    def save(cls, content: str, identifier: Identifier, extension_name: str) -> None:
        if cls._readOnly or cls._disable:
            return
        else:
            cls._save_unhandled(
                identifier=identifier,
                to_be_cached=content,
                extension=extension_name
                )
        return

    @classmethod
    def _get_unhandled(cls, identifier: Identifier) -> str:
        Logger.debug("Trying cache")
        hash_key = cls.generate_hash(identifier)
        try:
            cached = cls._cache_map[hash_key]
        except KeyError:
            Logger.debug(f"Cache miss.")
            raise CacheMiss

        if cls._neverExpire:
            # Ignore expire date
            pass
        elif (expired_days := cls._today - cached[0]) > cls._days_to_expire:
            # Enforce expire date
            Logger.info(f"Cache expired by {expired_days} days")
            raise CacheExpired

        if cls._cache_folder:
            file_path = os.path.join(cls._cache_folder, f"{cached[1]}")
        else:
            Logger.error(f"Cache System is used when no cache folder is set.")
            raise CacheNotFound

        if os.path.isfile(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                Logger.debug(f"Load {identifier} from cache {cached[1]}.")
                content = f.read()

                if not content:
                    Logger.warning(f"Empty cached file. Cache is seemingly corrupted.")
                    raise CacheCorrupt
        else:
            Logger.warning("Cache not found in the expected location.")
            raise CacheNotFound
        
        Logger.debug(f"Cache hit")
        return content

    @classmethod
    def _save_unhandled(cls, identifier: Identifier, to_be_cached: str, extension: str) -> None:
        Logger.debug("Save to cache system.")
        hash_key = cls.generate_hash(identifier)
        file_name = f"{hash_key}{extension}"
        cls._cache_map[hash_key] = (date.today(), file_name)

        file_path = os.path.join(cls._cache_folder, file_name)
        Logger.debug(f"Save to {file_path}.")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(to_be_cached)

    @classmethod
    def _resume(cls) -> None:
        """Load meta file from the disk
        """
        file_path = os.path.join(cls._cache_folder, cls._meta_file_name)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                deactivated_map = json.load(f)
            cls._cache_map = {
                hash_key: (date.fromisoformat(cached[0]), cached[1]) for hash_key, cached in deactivated_map.items()
            }
        except FileNotFoundError:
            Logger.warning(f"Cannot find {file_path}")
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines("")
        except json.decoder.JSONDecodeError:
            Logger.warning(f"Meta data corrupted")
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines("")
        Logger.debug(f"Load cache map from {file_path}")
        return

    @classmethod
    def _suspend(cls) -> None:
        """Save meta file to the disk
        """
        file_path = os.path.join(cls._cache_folder, cls._meta_file_name)
        dumpable = {
            hash_key: (str(cached[0]), cached[1]) for hash_key, cached in cls._cache_map.items()
        }
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(dumpable, f, ensure_ascii=False, indent=2)
        Logger.debug(f"Save cache map to {file_path}")
        return

    @staticmethod
    def generate_hash(source: Identifier) -> HashKey:
        """Generate primary key using a given string

        Args:
            source (str): a string would not be changed during different scraping

        Returns:
            str: a 48-digit hexdigest string
        """ 
        # Create a hash object
        hash_obj = hashlib.blake2b(digest_size=8)
        # Update the hash object with the source bytes
        hash_obj.update(source.encode('utf-8'))
        # Return the hexadecimal digest of the hash
        return hash_obj.hexdigest()

@atexit.register
def save_to_disk():
    Logger.debug("Cacher detects exit")
    if GlobalCacheManager._isSetup:
        GlobalCacheManager._suspend()
    else:
        Logger.warning("Cacher is never setup")