import hashlib
import pickle

from django.core.cache import caches


def cache_for(seconds, cache_name='default', key_prefix=None, ignore_self=False):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            cache = caches[cache_name]
            if ignore_self:
                key = generate_cache_key(key_prefix, fn.__name__, *args[1:], **kwargs)
            else:
                key = generate_cache_key(key_prefix, fn.__name__, *args, **kwargs)
            result = cache.get(key=key)
            if result is None:
                result = fn(*args, **kwargs)
                if result:
                    cache.set(key, pickle.dumps(result), seconds)
            else:
                result = pickle.loads(result)
            return result

        return wrapper

    return decorator


def generate_cache_key(key_prefix, *args, **kwargs) -> str:
    serialise = []
    for arg in args:
        serialise.append(str(arg))
    for key, arg in kwargs.items():
        serialise.append(str(key))
        serialise.append(str(arg))
    key = hashlib.md5(",".join(serialise).encode('utf-8')).hexdigest()

    if key_prefix:
        return f'{key_prefix}:{key}'
    else:
        return key
