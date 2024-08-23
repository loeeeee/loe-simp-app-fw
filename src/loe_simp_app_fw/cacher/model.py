from dataclasses import dataclass, field
import datetime
from functools import partial
from typing import Self, TypeAlias, Dict
import hashlib

from ..config import FrameworkConfig

# Typings
Identifier: TypeAlias = str
HashKey: TypeAlias = str


@dataclass
class Cached:
    # Auto things
    _primary_key: str = field(default="", kw_only=True)
    _birthday: str = field(default_factory=partial(lambda _: str(datetime.date.today), ""), kw_only=True)

    # User things
    identifier: Identifier = field(default="")
    content: str = field(default="")
    file_extension: str = field(default="", kw_only=True)
    time_to_live: int = field(default=FrameworkConfig.cache_time_to_live, kw_only=True)

    def __post_init__(self) -> None:
        self._primary_key = self.generate_hash(self.identifier)
        return

    def to_json(self) -> Dict:
        return vars(self)

    @classmethod
    def from_json(cls, source: Dict) -> Self:
        new = cls()
        for key, value in source.items():
            setattr(new, key, value)
        return new

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