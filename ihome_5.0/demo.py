import functools

def login_required(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        pass
    return wrapper()

def itcast():
    """itcast python"""
    pass

print(itcast.__name__)
print(itcast.__doc__)