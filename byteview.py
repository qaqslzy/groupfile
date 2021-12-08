__author__ = 'liuweiyi'
__time__ = '2021/11/11'


class ByteView:
    def __init__(self, b=[], s=''):
        self.b = b
        self.s = s

    def Len(self):
        if self.b:
            return len(self.b)
        return len(self.s)

    def __len__(self):
        return self.Len()

    def ByteSlice(self):
        if self.b:
            return self.b[:]
        return list(self.s)

    def String(self):
        if self.b:
            return str(self.b)
        return self.s

    def At(self, i):
        if self.b:
            return self.b[i]
        return self.s[i]

    def Slice(self, f, t):
        if self.b:
            return ByteView(self.b[f:t])
        return ByteView(s=self.s[f:t])

    def SliceFrom(self, f):
        if self.b:
            return ByteView(self.b[f:])
        return ByteView(s=self.s[f:])

    def Copy(self, dest):
        if self.b:
            dest.extend(self.b)
        dest.extend(list(self.s))

    def Equal(self, b2):
        if not b2.b: return self.EqualString(b2.s)
        return self.EqualBytes(b2.b)

    def EqualString(self, s):
        if not self.b:
            return self.s == s
        l = self.Len()
        if len(s) != l:
            return False
        return ''.join(map(str, self.b)) == s

    def EqualBytes(self, b2):
        if self.b:
            return ''.join(map(str, self.b)) == ''.join(map(str, b2))
        l = self.Len()
        if len(b2) != l:
            return False
        return self.s == ''.join(map(str, b2))
