__author__ = 'liuweiyi'
__time__ = '2021/11/11'

from byteview import ByteView


def cloneBytes(b):
    return b[:]


def setSinkView(s, v):
    if hasattr(s, 'setView'):
        return s.setView(v)
    if v.b:
        return s.SetBytes(v.b)
    return s.SetString(v.s)


class StringSink:
    def __init__(self, sp='', v=None):
        self.sp = sp
        self.v = v

    def view(self):
        return self.v

    def SetString(self, v):
        self.v.b = []
        self.v.s = v
        self.sp = v

    def SetBytes(self, v):
        self.SetString(''.join(map(str, v)))


class ByteViewSink:
    def __init__(self):
        self.dst = ByteView()

    def SetString(self, s):
        self.dst = ByteView(s=s)
        return None

    def SetBytes(self, v):
        self.dst = ByteView(b=cloneBytes(v))
        return None

    def setView(self, v):
        self.dst = v
        return None

    def view(self):
        return self.dst, None
