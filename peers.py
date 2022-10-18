port = None

def portPicker(g):
    global port
    return port

class ProtoGetter():
    def Get(self, ctx, req, resp):
        pass


class PeerPicker():
    def PickPeer(self, key):
        pass


class NoPeers:
    def PickPeer(self, key):
        return None, None


def RegisterPeerPicker(p):
    global port
    global portPicker
    port = p
    # if portPicker:
    #     # TODO rasie error rigister called more than once
    #     pass
    # portPicker = lambda g: port


def getPeers(groupName):
    global portPicker
    if not portPicker:
        return NoPeers()
    pk = portPicker(groupName)
    if not pk:
        pk = NoPeers()
    return pk
