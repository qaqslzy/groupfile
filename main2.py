__author__ = 'liuweiyi'
__time__ = '2021/12/23'
import groupfile
from byteview import ByteView
from sinks import ByteViewSink
import os
import tcp


def FileGetter(ctx, key, dest):
    with open("./{}/{}".format(ctx['peer'], key), "rb") as f:
        data = f.read()
        dest.SetBytes(data)


def FileAdder(ctx, key, dest, data):
    with open("./{}/{}".format(ctx['peer'], key), "wb") as f:
        f.write(data)


def FileDeleter(ctx, key):
    os.remove("./{}/{}".format(ctx['peer'], key))



if __name__ == '__main__':
    peers_addrs = ["127.0.0.1:8001", "127.0.0.1:8002"]
    peers, server = tcp.NewTCPPool('127.0.0.1:8002')
    peers.Set(*peers_addrs)

    groupfile.NewGroup(
        name="fileGroup",
        cacheBytes=64 << 20,
        getter=FileGetter,
        adder=FileAdder,
        deleter=FileDeleter
    )

    try:
        server.serve_forever()
    except:
        server.server_close()