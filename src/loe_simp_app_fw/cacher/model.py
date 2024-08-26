from dataclasses import dataclass, field
import datetime
from functools import partial
from typing import Self, TypeAlias, Dict, ClassVar
import hashlib
import os

from .exception import CacheCorrupted, CacheNotFound, EmptyIdentifier, NotYetSetup
from ..logger import Logger

# Typings
AbsolutePath: TypeAlias = str
Identifier: TypeAlias = str
HashKey: TypeAlias = str

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


@dataclass
class CachedEntry:
    # Settings
    _default_time_to_live: ClassVar[int]
    _cache_folder: ClassVar[str]
    _isSetup: ClassVar[bool] = False

    # Auto things
    _primary_key: str = field(default="", kw_only=True)
    _birthday: str = field(default_factory=partial(lambda _: str(datetime.date.today), ""), kw_only=True)
    _content_hash: str = field(default="", kw_only=True)

    # User things
    identifier: Identifier = field(default="")
    file_extension: str = field(default="", kw_only=True)
    time_to_live: int|None = field(default=None, kw_only=True)
    """
    Time to live:
        - None
            - Default value of the config
        - Positive integer
            - A custom day of expire date
        - Negative integer
            - Never expire
        - Zero
            - Never save
    """

    @classmethod
    def setup(
        cls, 
        default_time_to_live: int,
        cache_folder: str,
        ) -> None:
        """
        Config the default values for new instance of the class
        """
        cls._default_time_to_live = default_time_to_live
        cls._cache_folder = cache_folder

        cls._isSetup = True

    def __post_init__(self) -> None:
        if not self._isSetup:
            Logger.error(f"The Cached Entry not yet has its default configured")
            raise NotYetSetup
        return

    def _to_json(self) -> Dict:
        return vars(self)

    def _reborn(self) -> None:
        """
        Update the birthday of the current cache instance to today
        """
        self._birthday = str(datetime.date.today())

    def __str__(self) -> str:
        return f"{self.identifier} {self.time_to_live}"

    @property
    def primary_key(self) -> HashKey:
        """
        Generate primary key on the fly

        Raises:
            EmptyIdentifier: When identifier is not present generation will fail

        Returns:
            HashKey: The Primary Key
        """
        if not self.identifier:
            Logger.error(f"Cannot generate primary key for empty identifier")
            raise EmptyIdentifier

        if not self._primary_key:
            # Generate primary key
            self._primary_key = generate_hash(self.identifier)
        return self._primary_key

    @property
    def _time_to_live(self) -> int:
        """
        Guarantee the return of an integer

        Returns:
            int: Number of days to live for the cache
        """
        if self.time_to_live == None:
            return self._default_time_to_live
        else:
            return self.time_to_live
    
    @property
    def isExpired(self) -> bool:
        if self._time_to_live >= 0:
            remaining_life = datetime.date.fromisoformat(self._birthday) + datetime.timedelta(days=self._time_to_live) - datetime.date.today()
            isExpired = (remaining_life <= datetime.timedelta(days=0))
            if isExpired:
                Logger.info(f"Cache expired by {remaining_life}")
            else:
                Logger.debug(f"Remaining life is {remaining_life}")
            
            return isExpired
        else:
            # Never expire
            return False

    @classmethod
    def from_json(cls, source: Dict) -> Self:
        new = cls()
        for key, value in source.items():
            setattr(new, key, value)
        return new


@dataclass
class Cached(CachedEntry):
    content: str = field(default="")

    @classmethod
    def _load_content(cls, entry: CachedEntry) -> Self:
        new = cls()
        new.__dict__ = entry.__dict__.copy()

        # Read in the actual content
        path: AbsolutePath = os.path.join(cls._cache_folder, f"{entry.primary_key}.{entry.file_extension}")
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                new.content = f.read()
        else:
            # In the case of goofy situation
            Logger.warning(f"Encounter corrupted cache file, {path}")
            raise CacheNotFound
        
        if new.content == "":
            raise CacheCorrupted

        return new

    @property
    def content_hash(self) -> str:
        if self._content_hash == "":
            self._content_hash = generate_hash(self.content)
        return self._content_hash

    def _save(self) -> CachedEntry:
        # Save to file system
        path: AbsolutePath = os.path.join(self._cache_folder, f"{self.primary_key}.{self.file_extension}")
        if os.path.isfile(path) and self.time_to_live != 0:
            # Skip saving when ttl is 0
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.content)
        else:
            # In the case of goofy situation
            Logger.warning(f"Encounter corrupted cache file, {path}")
            raise CacheCorrupted

        # Generate new entry
        entry: CachedEntry = CachedEntry()
        for key, value in vars(self).items():
            if key == "content":
                continue
            setattr(entry, key, value)

        return entry

