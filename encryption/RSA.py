import numpy
import random


class RSA:
    def __init__(self):
        self.P = [2003, 2011, 2017, 2027, 2029, 2039, 2053, 2063, 2069, 2081, 2083, 2087, 2089, 2099, 2111, 2113, 2129,
                  2131, 2137, 2141, 2143, 2153, 2161, 2179, 2203, 2207, 2213, 2221, 2237, 2239, 2243, 2251, 2267, 2269,
                  2273, 2281, 2287, 2293, 2297, 2309, 2311, 2333, 2339, 2341, 2347, 2351, 2357, 2371, 2377, 2381, 2383,
                  2389, 2393, 2399, 2411, 2417, 2423, 2437, 2441, 2447, 2459, 2467, 2473, 2477, 2503, 2521, 2531, 2539,
                  2543, 2549, 2551, 2557, 2579, 2591, 2593, 2609, 2617, 2621, 2633, 2647, 2657, 2659, 2663, 2671, 2677,
                  2683, 2687, 2689, 2693, 2699, 2707, 2711, 2713, 2719, 2729, 2731, 2741, 2749, 2753, 2767, 2777, 2789,
                  2791, 2797, 2801, 2803, 2819, 2833, 2837, 2843, 2851, 2857, 2861, 2879, 2887, 2897, 2903, 2909, 2917,
                  2927, 2939, 2953, 2957, 2963, 2969, 2971, 2999]
        self.e, self.d, self.n = self.getEDN()

    def getE(self, begin):
        for i in range(begin, 4000):
            for j in range(2, i):
                if (i % j) == 0:
                    break
            else:
                return i

    def getD(self, fn, e):
        k = 1
        while True:
            s = k * fn + 1
            if s % e == 0:
                return int(s / e)
            else:
                k = k + 1

    def getEDN(self):
        # pq = random.sample(list(self.P), 2)
        # p = int(pq[0])
        # q = int(pq[1])
        pq = [2347, 2423]
        p = int(pq[0])
        q = int(pq[1])
        print("p:", p, ";q:", q)

        n = p * q
        fn = (p - 1) * (q - 1)
        max_pq = max(pq)
        # e = self.getE(max_pq + 1)
        e = 2731
        d = self.getD(fn, e)
        return e, d, n

    def E(self, m):
        mm = 1
        for i in range(self.e):
            mm = (mm * m) % self.n
        return mm

    @staticmethod
    def E_with_e_n(m, e, n):
        mm = 1
        for i in range(e):
            mm = (mm * m) % n
        return mm

    def D(self, c):
        cc = 1
        for i in range(self.d):
            cc = (cc * c) % self.n
        return cc

    @staticmethod
    def D_with_d_n(c, d, n):
        cc = 1
        for i in range(d):
            cc = (cc * c) % n
        return cc


def encodeKey(K, e, n):
    result = []
    for i in K:
        result.append(RSA.E_with_e_n(ord(i), e, n))
    return result


def decodeKey(K, d, n):
    result = []
    for i in K:
        result.append(RSA.E_with_e_n(i, d, n))
    return result


if __name__ == '__main__':
    rsa = RSA()  # 初始化生成e,d,n
    m = "abcd"
    print(rsa.e)
    print(rsa.d)
    print(rsa.n)
    # rsa.e = 2731 res.n = 5686781
    mm = encodeKey(m, rsa.e, rsa.n)  # 对m加密
    print(mm)
    m = decodeKey(mm, rsa.d, rsa.n)  # 对mm解密
    print("".join(map(chr, m)))
