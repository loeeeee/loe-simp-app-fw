class CacheMiss(Exception):
    pass

class CacheCorrupted(Exception):
    pass

class CacheNotFound(Exception):
    pass

class NotYetSetup(Exception):
    pass

class EmptyIdentifier(Exception):
    pass