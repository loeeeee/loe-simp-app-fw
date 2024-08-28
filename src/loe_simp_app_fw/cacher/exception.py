class CacheMiss(Exception):
    pass

class CacheCorrupted(CacheMiss):
    pass

class CacheNotFound(CacheMiss):
    pass

class NotYetSetup(Exception):
    pass

class EmptyIdentifier(Exception):
    pass