import datetime
from typing import Dict, ClassVar
import os
import json

from .model import AbsolutePath, Cached, HashKey, _CachedCore, Identifier, generate_hash
from .exception import CacheMiss
from ..logger import Logger
from ..prometheus import Prometheus

cache_monitor = Prometheus().get("CacheManager")

class CacheMap:
    # Settings
    _cache_folder: ClassVar[AbsolutePath]
    _days_to_expire: ClassVar[datetime.timedelta]

    # Override
    _neverExpire: ClassVar[bool]
    _readOnly: ClassVar[bool]
    _disable: ClassVar[bool]

    # Variables
    _map: ClassVar[Dict[HashKey, _CachedCore]] = {}
    _isSetup: ClassVar[bool] = False
    
    # Constant
    _meta_file_name: ClassVar[str] = "meta.json"

    @classmethod
    def setup(
        cls, 
        cache_folder: AbsolutePath, 
        time_to_live: int, 
        *args, 
        neverExpire: bool = False, 
        readOnly: bool = False, 
        disable: bool = False, 
        **kwargs
        ) -> None:
        # Store settings
        cls._cache_folder = cache_folder
        cls._days_to_expire = datetime.timedelta(days=time_to_live)

        # Setup Cached and CachedEntry
        _CachedCore.setup(
            default_time_to_live=time_to_live,
            cache_folder=cache_folder,
        )

        cls._neverExpire = neverExpire # NotImplement
        cls._readOnly = readOnly    # NotImplement
        cls._disable = disable  # NotImplement

        # Load previous saves
        cls.load()

        # Flag it
        cls._isSetup = True

    # --------------------------------------- Major API ---------------------------------------

    @classmethod
    def append(cls, cached: Cached, /) -> None:
        # Extract core
        core = cached.core

        # Add downloaded content to cache storage
        ## If an old one exists, check if content updates
        ### If updates an old one, save the updated content
        try:
            old_cache = cls._map[core.primary_key]
        except KeyError:
            # No old cache found
            Logger.debug(f"No old cache found for {core}")
            cls._map[core.primary_key] = core
            core._save()
        else:
            # Old cache found
            if core._content_hash != old_cache._content_hash:
                # Update cache
                core._save()
                cls._map[core.primary_key] = core
            else:
                Logger.debug("Cache is not updated")

            # Update birthday of the cached
            cls._map[core.primary_key]._reborn()

    @classmethod
    def __getitem__(cls, key: Identifier, /) -> Cached:
        key = generate_hash(key)
        try:
            candidate: _CachedCore = cls._map[key]
        except KeyError:
            Logger.debug(f"Cannot find cache {key}")
            cache_monitor.failure("Get")
            raise CacheMiss
        else:
            cache_monitor.success("Get")
            return Cached.from_core(candidate)

    # --------------------------------------- Minor API ---------------------------------------

    @classmethod
    def __delitem__(cls, key: Identifier, /) -> None:
        key = generate_hash(key)
        del cls._map[key]

    @classmethod
    def __len__(cls) -> int:
        return len(cls._map)

    @classmethod
    def evacuate_cached(cls) -> None:
        """
        Remove all the cached from the cache map and replace with only entry

        Raises:
            NotImplemented: It is not implemented though
        """
        raise NotImplemented

    # --------------------------------------- Internal Management ---------------------------------------

    @classmethod
    def load(cls) -> None:
        meta_file_path: AbsolutePath = os.path.join(cls._cache_folder, cls._meta_file_name)
        Logger.debug(f"Load meta file from {meta_file_path}")
        try:
            with open(meta_file_path, "r", encoding="utf-8") as f:
                composed_json = json.load(f)
        except FileNotFoundError:
            Logger.warning(f"Cannot find meta file at {meta_file_path}")
        else:
            for entry in composed_json:
                cls._map[entry["_primary_key"]] = _CachedCore.from_json(entry)

            Logger.debug(f"Loaded cache meta from file")
        return

    @classmethod
    def save(cls) -> None:
        if not cls._isSetup:
            Logger.warning("CacheMap was never setup, skipping saving")
            return
    
        composed_json = []
        for entry in cls._map.values():
            composed_json.append(entry._to_record())
        Logger.info("Finish compose cache map meta")

        meta_file_path: AbsolutePath = os.path.join(cls._cache_folder, cls._meta_file_name)
        with open(meta_file_path, "w", encoding="utf-8") as f:
            json.dump(composed_json, f, indent=2)
        Logger.info(f"Saved cache meta to file in {meta_file_path}")
        return


class CacheManager:
    core: ClassVar[CacheMap] = CacheMap()

    @classmethod
    def setup(
        cls, 
        cache_folder: AbsolutePath, 
        time_to_live: int, 
        *args, 
        neverExpire: bool = False, 
        readOnly: bool = False, 
        disable: bool = False, 
        **kwargs
        ) -> None:
        cls.core.setup(
            cache_folder, 
            time_to_live, 
            neverExpire = neverExpire, 
            readOnly = readOnly, 
            disable = disable
        )

    def append(self, cache: Cached, /) -> None:
        return self.core.append(cache)

    def __getitem__(self, key: Identifier, /) -> Cached:
        return self.core[key]

    def __len__(self) -> int:
        return len(self.core)
