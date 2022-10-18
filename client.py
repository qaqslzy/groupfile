import json
import socket
import struct
from encryption.RSA import RSA, encodeKey
from encryption.FileCode import encrypt_file, decrypt_file
from encryption.AES import strToKey

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


def AddFile():
    """
    readme.md 对于 8001
    dsssssda.md 对应 8002
    ppp.md 对应 8002
    """
    rsa = RSA()
    aes_key = "abcd"
    mm = encodeKey(aes_key, rsa.e, rsa.n)  # 对m加密
    b_aes = bytes(json.dumps(mm), 'utf-8')

    # print("code", code)

    f = open("./readme.md", 'rb')
    data = f.read()
    f.close()
    HOST, PORT = "127.0.0.1:8001".split(':')
    with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as sock:
        # 发送信息到other peer去获取信息
        sock.connect((HOST, int(PORT)))
        data = encrypt_file((aes_key*4).encode('utf-8'), data)
        msg = b'ADD;AES=' + b_aes + b';GROUP=fileGroup;KEY=77777.md;DAT=' + data
        send_msg(sock, msg)

        received = recv_msg(sock)
        print(received)


def GetFile():
    rsa = RSA()
    aes_key = "abcd"
    mm = encodeKey(aes_key, rsa.e, rsa.n)  # 对m加密
    b_aes = bytes(json.dumps(mm), 'utf-8')

    HOST, PORT = "127.0.0.1:8001".split(':')
    # key = "readme.md"
    # key = "dsssssda.md"
    key = "77777.md"
    with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as sock:
        # 发送信息到other peer去获取信息
        sock.connect((HOST, int(PORT)))
        msg = b'GET;AES=' + b_aes + b';GROUP=fileGroup;KEY=' + bytes(key, 'utf-8')
        send_msg(sock, msg)
        data = recv_msg(sock)[4:]
        data = decrypt_file((aes_key*4).encode('utf-8'), data)
        f = open('./{}'.format(key), 'wb')
        f.write(data)
        f.close()


if __name__ == '__main__':
    AddFile()
    # GetFile()
