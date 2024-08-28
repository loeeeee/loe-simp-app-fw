from dataclasses import dataclass, field
import datetime
from functools import cached_property, partial
from typing import Self, TypeAlias, Dict, ClassVar, Optional, Literal
import hashlib
import os

from .exception import CacheCorrupted, CacheNotFound, EmptyIdentifier, NotYetSetup
from ..logger import Logger

# Typings
AbsolutePath: TypeAlias = str
Identifier: TypeAlias = str
HashKey: TypeAlias = str

def generate_hash(source: str|bytes) -> HashKey:
    """Generate primary key using a given string

    Args:
        source (str): a string would not be changed during different scraping

    Returns:
        str: a 48-digit hexdigest string
    """ 
    # Create a hash object
    hash_obj = hashlib.blake2b(digest_size=8)
    # Update the hash object with the source bytes
    if isinstance(source, str):
        hash_obj.update(source.encode('utf-8'))
    elif isinstance(source, bytes):
        hash_obj.update(source)
    # Return the hexadecimal digest of the hash
    return hash_obj.hexdigest()


@dataclass
class _CachedCore:
    # Settings
    _default_time_to_live: ClassVar[int]
    _cache_folder: ClassVar[str]
    _isSetup: ClassVar[bool] = False

    # Constant
    _bytes_extension_name: ClassVar[Literal["bytes"]] = "bytes"

    # Compulsory when init
    identifier: Identifier

    # Optional when init
    _content: bytes|str|None = field(default=None, kw_only=True) # Served as a cache
    _time_to_live: int|None = field(default=None, kw_only=True)
    file_extension: str = field(default="", kw_only=True)

    # Auto things
    _primary_key: str = field(default="", kw_only=True)
    _content_hash: str|None = field(default=None, kw_only=True)
    _birthday: str = field(default_factory=partial(lambda _: str(datetime.date.today()), ""), kw_only=True)
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
        Logger.info("Cache Core setup complete")

    def __post_init__(self) -> None:
        if not type(self)._isSetup:
            Logger.error(f"The Cached Entry not yet has its default configured")
            raise NotYetSetup
        return

    def _to_record(self) -> Dict:
        """
        Convert Cached to json record with content omitted

        Returns:
            Dict: The result json
        """
        composed_json = {}
        for key, value in vars(self).items():
            if key == "_content":
                continue

            composed_json[key] = value
        return composed_json

    def _reborn(self) -> None:
        """
        Update the birthday of the current cache instance to today
        """
        self._birthday = str(datetime.date.today())

    def __str__(self) -> str:
        return f"{self.identifier} {self._birthday}"

    def _save(self) -> None:
        # Force generate content hash
        _ = self.content_hash
        # Save to file system
        path = self.cache_path
        
        if self.file_extension == self._bytes_extension_name:
            to_write = self.content_bytes
        else:
            to_write = self.content_str.encode("utf-8")

        with open(path, "wb") as f:
            f.write(to_write)

    def _get_raw_content(self) -> bytes:
        if os.path.isfile(self.cache_path):
            with open(self.cache_path, "rb") as f:
                raw = f.read()

            # Double check
            if raw == "":
                raise CacheCorrupted

            return raw
        else:
            Logger.warning(f"Cannot find cache file at {self.cache_path}")
            raise CacheNotFound
    
    def _load_content(self) -> None:
        content = self._get_raw_content()
        if self.file_extension == self._bytes_extension_name:
            self._content = content
        else:
            self._content = content.decode(encoding="utf-8")
        Logger.debug(f"Finish loading the content")
        return

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
            Logger.debug(f"Generated primary key, {self._primary_key}")
        return self._primary_key

    @property
    def content_str(self) -> str:
        if self._content == None:
            self._load_content()

        if not isinstance(self._content, str):
            Logger.error(f"Unexpected type for content, {type(self._content)}")
            raise TypeError
        
        return self._content

    @property
    def content_bytes(self) -> bytes:
        if self._content == None:
            self._content = self._get_raw_content()
        elif isinstance(self._content, bytes):
            pass
        else:
            Logger.error(f"Unexpected type for content, {type(self._content)}")
            raise TypeError
        return self._content

    @property
    def content(self) -> str|bytes:
        if self.file_extension == self._bytes_extension_name:
            return self.content_bytes
        else:
            return self.content_str

    @cached_property
    def cache_path(self) -> AbsolutePath:
        path: AbsolutePath = os.path.join(self._cache_folder, f"{self.primary_key}.{self.file_extension}")
        return path

    @property
    def content_hash(self) -> str:
        if self._content_hash == None:
            # Generate hash
            self._content_hash = generate_hash(self.content)
            Logger.debug(f"Generated content hash, {self._content_hash}")

        return self._content_hash

    @property
    def time_to_live(self) -> int:
        """
        Guarantee the return of an integer

        Returns:
            int: Number of days to live for the cache
        """
        if self._time_to_live == None:
            return self._default_time_to_live
        else:
            return self._time_to_live

    @classmethod
    def from_json(cls, source: Dict) -> Self:
        new = cls(
            "" # THE PLACEHOLDER
        )
        for key, value in source.items():
            setattr(new, key, value)
        return new


@dataclass
class Cached:
    core: _CachedCore

    @classmethod
    def from_content(
        cls,
        identifier: Identifier,
        content: str|bytes,
        file_extension: str = "",
        time_to_live: Optional[int] = None,
        ) -> Self:
        """
        Build a cached object for store in the cache system

        Args:
            identifier (Identifier): The ID for later retrieval
            content (str): Content that the ID refers to
            file_extension (str, optional): The format of the content, e.g., txt, json, HTML, etc. Defaults to "".
            time_to_live (Optional[int], optional): The number of days before the cache expire. Defaults to None.

        Returns:
            Self: A new cached content for storage
        """
        if isinstance(content, str):
            core = _CachedCore(
                identifier=identifier,
                _content=content,
                file_extension=file_extension,
                _time_to_live=time_to_live,
            )
        elif isinstance(content, bytes):
            if file_extension != _CachedCore._bytes_extension_name:
                Logger.warning(f"File extension should be 'bytes' for bytes input")
            core = _CachedCore(
                identifier=identifier,
                _content=content,
                file_extension=_CachedCore._bytes_extension_name,
                _time_to_live=time_to_live,
            )
        else:
            Logger.warning(f"Content type, {type(content)}, was not expected")
            raise TypeError
        return cls(core)

    @property
    def identifier(self) -> Identifier:
        return self.core.identifier

    @property
    def content_str(self) -> str:
        return self.core.content_str

    @property
    def content_bytes(self) -> bytes:
        return self.core.content_bytes

    @property
    def isExpired(self) -> bool:
        if self.core.time_to_live >= 0:
            remaining_life = datetime.date.fromisoformat(self.core._birthday) + datetime.timedelta(days=self.core.time_to_live) - datetime.date.today()
            isExpired = (remaining_life <= datetime.timedelta(days=0))
            if isExpired:
                Logger.info(f"Cache expired by {remaining_life}")
            else:
                Logger.debug(f"Remaining life is {remaining_life}")
            
            return isExpired
        else:
            # Never expire
            return False

        