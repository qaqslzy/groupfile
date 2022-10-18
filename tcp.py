import json
import struct
import threading
import socketserver
import consistenthash.consistenthash as consistenthash
import peers
from peers import RegisterPeerPicker
from groupfile import GetGroup
from sinks import ByteViewSink
from encryption.RSA import RSA, decodeKey
from encryption.FileCode import encrypt_file, decrypt_file
import socket

DEFAULT_REPLICAS = 50

'''
每次消息都有RSA加密后的AES的key
因性能受限AES的key只用RSA加密前四位，16位的AES密钥使用这4位数字不断重复
文件内容使用AES进行加密
'''

rsa = RSA()


def send_msg(sock, msg):
    # Prefix each message with a 4-byte length (network byte order)
    msg = struct.pack('>q', len(msg)) + msg
    sock.sendall(msg)


def recv_msg(sock):
    # Read message length and unpack it into an integer
    raw_msglen = recvall(sock, 8)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>q', raw_msglen)[0]
    # Read the message data
    return recvall(sock, msglen)


def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data


def deRSA(msg):
    mm = json.loads(msg)
    m = decodeKey(mm, rsa.d, rsa.n)  # 对mm解密
    return "".join(map(chr, m))


class TCPHandler(socketserver.BaseRequestHandler):
    """
    构建自己的消息结构体
    首先是Head，消息的前8个字节的为整个消息的长度
    其次是Body，前三个字节代表消息类型
    请求值：
    GET，获取
    ADD，添加
    DEL，删除
    返回值：
    DAT，返回的数据
    SUC，成功
    ERR，失败
    消息类型后紧跟;号
    剩下的消息内容则为Key-Value形式，以=分割key和value，以;分割多个键值对
    消息类型例如：
    GET;KEY=hello.txt;AES=123,43223,321,321;GROUP=hello
    ADD;KEY=new.txt;DAT=12345676\n

    DAT;12345679
    """

    def handle(self) -> None:

        data = recv_msg(self.request)
        ctx = {'o_msg': data}
        method = data[:4].decode()
        data = data[4:]

        # TODO 传输密钥， 加解密， 获取文件等

        # TODO 对内容使用非对称加密中的解密，

        #  判断需要执行的操作
        if method == "GET;":
            req = {}
            tmp = data.decode().split(';')
            for i in tmp:
                if '=' in i:
                    key, value = i.split('=')
                    req[key] = value

            groupName = req['GROUP']
            key = req['KEY']
            aes = deRSA(req['AES'])
            ctx['AES'] = aes

            group = GetGroup(groupName)
            if not group:
                send_msg(self.request, bytes('ERR;NOGROUP', 'utf-8'))
                return

            group.Stats.ServerRequests.Add(1)
            value = ByteViewSink()
            err = group.Get(ctx, key, value)
            if err != None:
                pass

            body, err = value.view()
            b = encrypt_file((aes * 4).encode('utf-8'), body.b)
            send_msg(self.request, bytes('DAT;', 'utf-8') + b)

        elif method == "ADD;":
            semicolon = bytes(';', 'utf-8')
            req = {}
            while True:
                try:
                    # 检测是否到达数据段
                    if chr(data[0]) == 'D' and chr(data[1]) == 'A' and chr(data[2]) == 'T' and chr(data[3]) == '=':
                        data = data[4:]
                        break
                    # 依然是数据前的字符串，开始分割
                    idx = data.index(semicolon)

                    item = data[:idx]
                    item = item.decode()
                    key, value = item.split('=')
                    req[key] = value

                    data = data[idx + 1:]

                except ValueError:
                    break
                except IndexError:
                    break

            # TODO 检测是否有这两个参数
            groupName = req['GROUP']
            key = req['KEY']
            aes = deRSA(req['AES'])
            ctx['AES'] = aes

            data = decrypt_file((aes * 4).encode('utf-8'), data)
            group = GetGroup(groupName)
            if not group:
                send_msg(self.request, bytes('ERR;NOGROUP', 'utf-8'))
                return

            group.Stats.ServerRequests.Add(1)
            value = ByteViewSink()
            err = group.Add(ctx, key, data, value)
            if err:
                send_msg(self.request, bytes('ERR;NOTADD', 'utf-8'))
                return
            body, err = value.view()

            send_msg(self.request, bytes('SUC;OK', 'utf-8'))

        elif method == "DEL;":
            # TODO DEL action
            pass
        elif method == "RSA;":  # 请求RSA公钥
            # TODO RSA action
            pass


# TODO 建立长链接，不要每次都关闭socket
class tcpPeers:
    def __init__(self, base=''):
        self.base = base

    def forwarding(self, ctx, req, resp):
        # group, key = req['group'], req['key']
        HOST, PORT = self.base.split(':')
        with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as sock:
            # 发送信息到other peer去获取信息
            sock.connect((HOST, int(PORT)))
            send_msg(sock, ctx['o_msg'])

            data = recv_msg(sock)
            if chr(data[0]) == 'D' and chr(data[1]) == 'A' and chr(data[2]) == 'T' and chr(data[3]) == ';':
                data = data[4:]
                data = decrypt_file((ctx['AES'] * 4).encode('utf-8'), data)
            resp['value'] = data

    def Get(self, ctx, req, resp):
        self.forwarding(ctx, req, resp)

    def Delete(self, ctx, req, resp):
        self.forwarding(ctx, req, resp)

    def Add(self, ctx, req, resp):
        self.forwarding(ctx, req, resp)


class TCPPoolOptions:
    def __init__(self, replicas=DEFAULT_REPLICAS, fn=None):
        self.Replicas = replicas
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

tcppeer = None


def NewHTTPPoolOpts(s, o):
    # 检测是否已经开启了pool
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

    # peers.portPicker = picker
    RegisterPeerPicker(p)
    return p


def NewTCPPool(s):
    p = NewHTTPPoolOpts(s, TCPPoolOptions())
    HOST, PORT = s.split(':')
    server = socketserver.TCPServer((HOST, int(PORT)), TCPHandler)
    return p, server
