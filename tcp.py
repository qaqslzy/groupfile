__author__ = 'liuweiyi'
__time__ = '2021/11/11'

import threading
import socketserver
import consistenthash.consistenthash as consistenthash
from peers import RegisterPeerPicker
from groupfile import GetGroup
from sinks import ByteViewSink
import socket

DEFAULT_REPLICAS = 50

class TCPHandler(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        # TODO 判断需要执行的操作
        # 传输密钥， 加解密， 获取文件等
        groupName = ''
        key = ''

        group = GetGroup(groupName)
        if not group:
            # TODO return error
            pass

        group.Stats.ServerRequests.Add(1)
        value = ByteViewSink()
        err = group.Get({}, key, value)
        if err:
            pass
        body, err = value.view()
        # TODO return data
        pass

class tcpPeers:
    def __init__(self, base=''):
        self.base = base

    def Get(self, ctx, req, resp):
        group, key = req['group'], req['key']
        HOST, PORT = self.base.split(':')
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to server and send data
            sock.connect((HOST, PORT))
            # TODO
            sock.sendall(bytes(data + "\n", "utf-8"))

            # Receive data from the server and shut down
            received = str(sock.recv(1024), "utf-8")

    def Delete(self):
        pass

    def Add(self):
        pass

class TCPPoolOptions:
    def __init__(self, replicas=DEFAULT_REPLICAS, fn=None):
        self.Replicas = self
        self.HashFn = fn


class TCPPool:
    def __init__(self, base='', ):
        self.self = base
        self.opts = None
        self.mu = threading.Lock()
        self.peers = None
        self.tcpPeers = {}

    def Set(self, *peers):
        self.mu.acquire()
        self.peers = consistenthash.New(self.opts.Replicas, self.opts.HashFn)
        self.peers.Add(peers)
        self.tcpPeers = {}
        for peer in peers:
            # TCP Peers
            self.tcpPeers[peer] = tcpPeers(base=peer)

        self.mu.release()

    def PickPeer(self, key):
        self.mu.acquire()
        if self.peers.IsEmpty():
            self.mu.release()
            return None, False
        peer = self.peers.Get(key)
        if peer != self.self:
            self.mu.release()
            return self.tcpPeers[peer], True
        self.mu.release()
        return None, False




tcpPoolMade = False


def NewHTTPPoolOpts(s, o):
    global tcpPoolMade
    if tcpPoolMade:
        raise
    tcpPoolMade = True

    p = TCPPool(base=s)

    if o:
        p.opts = o
    if p.opts.Replicas == 0:
        p.opts.Replicas = DEFAULT_REPLICAS
    p.peers = consistenthash.New(p.opts.Replicas, p.opts.HashFn)

    RegisterPeerPicker(lambda groupname: p)
    return p


def NewTCPPool(s):
    p = NewHTTPPoolOpts(s, None)
    HOST, PORT = s.split(':')
    server = socketserver.TCPServer((HOST, PORT), TCPHandler)
    return p, server
