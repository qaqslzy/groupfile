
class entry:
    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value


class Cache:
    def __init__(self, MaxEntries=0, OnEvicted=None):
        self.MaxEntries = MaxEntries
        self.OnEvicted = OnEvicted
        self.ll = []
        self.cache = {}  # map[key]entry

    def Add(self, key, value):
        ee = None
        if key in self.cache:
            ee = self.cache[key]
        if ee:
            self.llMoveToFront(ee)
            ee.value = value
            return
        ele = entry(key, value)
        self.ll.insert(0, ele)
        self.cache[key] = ele
        if self.MaxEntries != 0 and len(self.ll) > self.MaxEntries:
            self.RemoveOldest()

    def llMoveToFront(self, ele):
        self.ll.insert(0, self.ll.pop(self.ll.index(ele)))

    def Get(self, key):
        ele = None
        if key in self.cache:
            ele = self.cache[key]
        if ele:
            self.llMoveToFront(ele)
            return ele.value, True
        return None, False

    def Remove(self, key):
        ele = None
        if key in self.cache:
            ele = self.cache[key]
        if ele:
            self.removeElement(ele)

    def RemoveOldest(self):
        if len(self.ll) > 0:
            ele = self.ll[-1]
            self.removeElement(ele)

    def removeElement(self, ele):
        self.ll.remove(ele)
        kv = ele
        del self.cache[ele.key]
        if self.OnEvicted:
            self.OnEvicted(kv.key, kv.value)

    def Len(self):
        return len(self.ll)

    def __len__(self):
        return self.Len()

    def Clear(self):
        if self.OnEvicted:
            for e in self.cache.values():
                kv = e
                self.OnEvicted(kv.key, kv.value)

        self.ll = []
        self.cache = {}
