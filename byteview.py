
class ByteView:
    def __init__(self, b=bytes(), s=''):
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
        return bytes(self.s, 'utf-8')

    def String(self):
        if self.b:
            return bytes.decode(self.b)
        return self.s

    def At(self, i):
        if self.b:
            return self.b[i]
        return self.s[i]

    def Slice(self, f, t):
        if self.b:
            return ByteView(b=self.b[f:t])
        return ByteView(s=self.s[f:t])

    def SliceFrom(self, f):
        if self.b:
            return ByteView(b=self.b[f:])
        return ByteView(s=self.s[f:])

    def Equal(self, b2):
        if not b2.b: return self.EqualString(b2.s)
        return self.EqualBytes(b2.b)

    def EqualString(self, s):
        if not self.b:
            return self.s == s
        l = self.Len()
        if len(s) != l:
            return False
        return self.b.decode() == s

    def EqualBytes(self, b2):
        if self.b:
            return self.b.decode() == b2.decode()
        l = self.Len()
        if len(b2) != l:
            return False
        return self.s == b2.decode()
