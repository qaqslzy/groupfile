import peers
from inspect import isfunction
import singleflight.singleflight as singleflight
import threading
from byteview import ByteView
from once import Once
from lru.lru import Cache as lruCache
import random
from sinks import setSinkView

mu = threading.RLock()
groups = {}
initPeerServerOnce = Once()
initPeerServer = None

newGroupHook = None


def NewGroup(name, cacheBytes, getter, adder, deleter):
    newGroup(name, cacheBytes, getter, None, adder, deleter)


def newGroup(name, cacheBytes, getter, peers, adder, deleter):
    global groups, newGroupHook
    if not getter:
        raise  # TODO error nil Getter
    mu.acquire()
    # initPeerServerOnce.run_once(print)()  # TODO callInitPeerServer
    if name in groups:
        raise  # TODO duplicate registration of group name
    g = Group(name=name, getter=getter, adder=adder, deleter=deleter, peers=peers,
              lodaGroup=singleflight.Group())  # singleflight
    if isfunction(newGroupHook):
        newGroupHook(g)
    groups[name] = g
    mu.release()
    return g


def GetGroup(name):
    global groups
    mu.acquire()
    g = groups[name]
    mu.release()
    return g


class Stats:
    def __init__(self):
        self.Gets = AtomicInt()
        self.CacheHits = AtomicInt()
        self.PeerLoads = AtomicInt()
        self.PeerErrors = AtomicInt()
        self.Loads = AtomicInt()
        self.LoadsDeduped = AtomicInt()
        self.LocalLoads = AtomicInt()
        self.LocalLoadErrs = AtomicInt()
        self.ServerRequests = AtomicInt()


class Group:
    def __init__(self, name='', getter=None, adder=None, deleter=None, peers=None, lodaGroup=None):
        self.once = Once()
        self.name = name
        self.getter = getter
        self.adder = adder
        self.deleter = deleter
        self.peers = peers  # PeerPicker
        self.mainCache = cache()
        self.hotCache = cache()
        self.loadGroup = lodaGroup  # flightGroup
        self.Stats = Stats()

    def Name(self):
        return self.name

    def initPeers(self):
        @self.once.run_once
        def do():
            if not self.peers:
                self.peers = peers.getPeers(self.name)

        do()

    def Delete(self, ctx, key):
        self.initPeers()
        if isinstance(ctx, dict):
            ctx['peer'] = self.peers.self
        else:
            ctx = {'peer': self.peers.self}

        peer, ok = self.peers.PickPeer(key)
        if ok:
            self.deleteFromPeer(ctx, peer, key)
        else:
            self.deleteCache(key)
            self.deleteLocally(ctx, key)

    def Add(self, ctx, key, data, dest):
        self.initPeers()
        if isinstance(ctx, dict):
            ctx['peer'] = self.peers.self
        else:
            ctx = {'peer': self.peers.self}

        peer, ok = self.peers.PickPeer(key)
        if ok:
            self.addFromPeer(ctx, peer, key, data)
        else:
            value, err = self.addLocally(ctx, key, dest, data)
            if err:
                self.Stats.LocalLoadErrs.Add(1)
            self.Stats.LocalLoads.Add(1)

    def Get(self, ctx, key, dest):
        self.initPeers()
        self.Stats.Gets.Add(1)
        if isinstance(ctx, dict):
            ctx['peer'] = self.peers.self
        else:
            ctx = {'peer': self.peers.self}

        if not dest:
            return
            # TODO raise nil dest sink
            pass
        value, cacheHit = self.lookupCache(key)

        if cacheHit:
            self.Stats.CacheHits.Add(1)
            # setSinkView
            setSinkView(dest, value)
            return None
        value, destPopulated, err = self.load(ctx, key, dest)
        if err is not None:
            return err
        if destPopulated:
            return None
        return setSinkView(dest, value)

    def lookupCache(self, key):
        value, ok = self.mainCache.get(key)
        if ok:
            return value, ok
        value, ok = self.hotCache.get(key)
        if ok:
            return value, ok
        return None, False

    def deleteCache(self, key):
        self.mainCache.delete(key)
        self.hotCache.delete(key)

    def load(self, ctx, key, dest):
        self.Stats.Loads.Add(1)
        destPopulate = [False]

        def func():
            value, cacheHit = self.lookupCache(key)
            if cacheHit:
                self.Stats.CacheHits.Add(1)
                return value, None
            self.Stats.LoadsDeduped.Add(1)
            peer, ok = self.peers.PickPeer(key)
            if ok:
                value, err = self.getFromPeer(ctx, peer, key)
                if not err:
                    self.Stats.PeerLoads.Add(1)
                    return value, None
                self.Stats.PeerErrors.Add(1)
            value, err = self.getLocally(ctx, key, dest)
            if err:
                self.Stats.LocalLoadErrs.Add(1)
                return None, err
            self.Stats.LocalLoads.Add(1)
            destPopulate[0] = True
            self.populateCache(key, value, self.mainCache)
            return value, None

        viewi, err = self.loadGroup.Do(key, func)
        if err is None:
            return viewi, destPopulate[0], None
        return None, destPopulate[0], err

    def addFromPeer(self, ctx, peer, key, data):
        resp = {}
        err = peer.Add(ctx, None, resp)
        if not err:
            return ByteView(), err
        value = ByteView(b=resp['value'])
        return value, None

    def deleteFromPeer(self, ctx, peer, key):
        resp = {}
        err = peer.Delete(ctx, None, resp)
        if not err:
            return ByteView(), err
        value = ByteView(b=resp['value'])
        return value, None

    def getFromPeer(self, ctx, peer, key):
        req = {'group': self.name, 'key': key}
        resp = {}
        err = peer.Get(ctx, req, resp)  # TODO return resp
        if err is not None:
            return ByteView(), err
        value = ByteView(b=resp['value'])
        if random.randint(0, 9) == 0:
            self.populateCache(key, value, self.hotCache)
        return value, None

    def deleteLocally(self, ctx, key):
        err = self.deleter(ctx, key)
        if not err:
            return err
        return None

    def addLocally(self, ctx, key, dest, data):
        err = self.adder(ctx, key, dest, data)
        if not err:
            return ByteView(), err
        return dest.view(), None

    def getLocally(self, ctx, key, dest):
        err = self.getter(ctx, key, dest)
        if err is not None:
            return ByteView(), err
        return dest.view()

    def populateCache(self, key, value, cache):
        cache.add(key, value)


class AtomicInt:
    def __init__(self, value=0):
        self.lock = threading.RLock()
        self.value = value

    def Add(self, n):
        self.lock.acquire()
        self.value += n
        self.lock.release()

    def Get(self):
        self.lock.acquire()
        value = self.value
        self.lock.release()
        return value

    def __str__(self):
        return str(self.Get())


class cache:
    def __init__(self):
        self.mu = threading.RLock()
        self.nbytes = 0
        self.lru = None
        self.nhit = 0
        self.nget = 0
        self.nevict = 0

    def stats(self):
        self.mu.acquire()
        stats = {
            'Bytes': self.nbytes,
            'Items': self.itemsLocked(),
            'Gets': self.nget,
            'Hits': self.nhit,
            'Evicitions': self.nevict
        }
        self.mu.release()
        return stats

    def add(self, key, value):
        def cacheOnEvicted(k, v):
            self.nbytes -= len(k) + len(v.Len())
            self.nevict += 1

        self.mu.acquire()
        if not self.lru:
            self.lru = lruCache(OnEvicted=cacheOnEvicted)
        self.lru.Add(key, value)
        self.nbytes += len(key) + len(value)
        self.mu.release()

    def delete(self, key):
        self.mu.acquire()
        if not self.lru:
            self.lru.Remove(key)
        self.mu.release()

    def get(self, key):
        self.mu.acquire()
        self.nget += 1
        if not self.lru:
            return None, False
        vi, ok = self.lru.Get(key)
        if not ok:
            return None, False
        self.nhit += 1
        self.mu.release()
        return vi, True

    def removeOldest(self):
        self.mu.acquire()
        if not self.lru:
            self.lru.RemoveOldest()
        self.mu.release()

    def bytes(self):
        self.mu.acquire()
        n = self.nbytes
        self.mu.release()
        return n

    def items(self):
        self.mu.acquire()
        l = self.itemsLocked()
        self.mu.release()
        return l

    def itemsLocked(self):
        if not self.lru:
            return 0
        return self.lru.Len()
