__author__ = 'liuweiyi'
__time__ = '2021/11/9'

import bisect


def New(replicas, hfn):
    m = Map()
    m.replicas = replicas
    m.hash = hfn
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
    def Add(self, *keys):
        for key in keys:
            for i in range(self.replicas):
                hashc = int(self.hash(i + key))
                bisect.insort(self.keys, hashc)
                self.hashMap[hashc] = key

    # Gets the closest item in the hash to the provided key
    def Get(self, key):
        if self.IsEmpty(): return ""

        hashc = int(self.hash(key))
        idx = bisect.bisect(self.keys, hashc)

        if idx == len(self.keys):
            idx = 0

        return self.hashMap[self.keys[idx]]
