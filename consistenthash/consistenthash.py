import bisect
import hashlib


def defaultHashFunc(text):
    sha1 = hashlib.sha1()
    sha1.update(text.encode('utf-8'))
    return sha1.hexdigest()


def New(replicas, hfn=defaultHashFunc):
    m = Map()
    m.replicas = replicas
    if not hfn:
        m.hash = defaultHashFunc
    return m


class Map:
    def __init__(self):
        self.hash = None
        self.replicas = 0
        self.keys = []  # []int
        self.hashMap = {}  # map[int]string

    # Return true if there are no items available
    def IsEmpty(self):
        return len(self.keys) == 0

    # Adds some keys to the hash
    def Add(self, keys):
        for key in keys:
            for i in range(self.replicas):
                hashc = int(self.hash(str(i) + key), 16)
                bisect.insort(self.keys, hashc)
                self.hashMap[hashc] = key

    # Gets the closest item         in the hash to the provided key
    def Get(self, key):
        if self.IsEmpty(): return ""

        hashc = int(self.hash(key), 16)
        idx = bisect.bisect(self.keys, hashc)

        if idx == len(self.keys):
            idx = 0

        return self.hashMap[self.keys[idx]]
