from django.core.cache import cache


def incrKey(key, value, timeout=None):
    return cache.incr(key, delta=value)


def setKey(key, value, timeout=None):
    return cache.set(key, value, timeout=timeout)


def addKey(key, value, timeout=None):
    return cache.add(key, value, timeout=timeout)


def getKey(key):
    return cache.get(key)


def deleteKey(key):
    return cache.delete(key)


def getAllKey(pattern):
    return cache.keys(pattern)
