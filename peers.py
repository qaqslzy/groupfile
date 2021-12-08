__author__ = 'liuweiyi'
__time__ = '2021/11/9'

from abc import ABCMeta, abstractmethod


portPicker = None


class ProtoGetter(metaclass=ABCMeta):
    @abstractmethod
    def Get(self, ctx, req, resp):
        pass


class PeerPicker(metaclass=ABCMeta):
    @abstractmethod
    def PickPeer(self, key):
        pass


class NoPeers(metaclass=PeerPicker):
    def PickPeer(self, key):
        return None, None




def RegisterPeerPicker(fn):
    global portPicker
    if portPicker:
        # TODO rasie error rigister called more than once
        pass
    portPicker = fn


def getPeers(groupName):
    global portPicker
    if not portPicker:
        return NoPeers()
    pk = portPicker(groupName)
    if not pk:
        pk = NoPeers()
    return
