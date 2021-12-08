import groupfile
import tcp


def FileGetter(ctx, key, dest):
    with open("./{}/{}".format(ctx['peer'], key), "rb") as f:
        f.read()


    pass


def FileAdder():
    with open("./{}/{}".format(ctx['peer'], key), "rb") as f:
        f.write()



def FileDeleter():
    pass


if __name__ == '__main__':
    peers_addrs = ["127.0.0.1:8001", "127.0.0.1:8002"]
    peers, server = tcp.NewTCPPool('127.0.0.1:8001')
    peers.Set(*peers_addrs)

    groupfile.NewGroup(
        name="fileGroup",
        cacheBytes=64 << 20,
        getter=FileGetter,
        adder=FileAdder,
        deleter=FileDeleter
    )

    server.serve_forever()
