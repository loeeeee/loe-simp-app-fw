class CacheMiss(Exception):
    pass

class CacheCorrupt(Exception):
    pass

class CacheNotFound(Exception):
    pass

class CacheExpired(Exception):
    pass
