__author__ = 'liuweiyi'
__time__ = '2021/11/10'
from functools import wraps

class Once:
    def __init__(self):
        self.has_run = False

    def run_once(self, f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not self.has_run:
                self.has_run = True
                return f(*args, **kwargs)

        return wrapper