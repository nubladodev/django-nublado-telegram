from asgiref.sync import sync_to_async


def async_call(func, *args, **kwargs):
    return sync_to_async(func)(*args, **kwargs)