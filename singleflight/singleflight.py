__author__ = 'liuweiyi'
__time__ = '2021/11/12'

from threading import Condition, Lock


class Caller(object):
    def __init__(self):
        self._cond = Condition()
        self.val = None
        self.err = None
        self.done = False

    def result(self):
        with self._cond:
            while not self.done:
                self._cond.wait()

        if self.err:
            raise self.err

        return self.val

    def notify(self):
        with self._cond:
            self.done = True
            self._cond.notify_all()

class Group(object):
    def __init__(self):
        self.map = {}
        self.lock = Lock()

    def Do(self, key, fn, *args, **kwargs):
        self.lock.acquire()
        if key in self.map:
            # Process the same key request when the key is already exists
            caller = self.map[key]
            self.lock.release()
            return caller.result()

        caller = Caller()
        self.map[key] = caller
        self.lock.release()

        # do the real get function
        try:
            caller.val = fn(*args, **kwargs)
        except Exception as e:
            caller.err = e
        finally:
            caller.notify()  # notify the threads

        # all done del the key
        self.lock.acquire()
        del self.map[key]
        self.lock.release()

        # return the result
        return caller.result()
