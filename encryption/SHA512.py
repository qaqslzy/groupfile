class SHA512:
    DIGEST_SIZE = 64  # 512 / 8
    SHA384_512_BLOCK_SIZE = 128   # (1024 / 8)

    def __init__(self):
        self.sha512_k = [0x428a2f98d728ae22, 0x7137449123ef65cd,
                     0xb5c0fbcfec4d3b2f, 0xe9b5dba58189dbbc,
                     0x3956c25bf348b538, 0x59f111f1b605d019,
                     0x923f82a4af194f9b, 0xab1c5ed5da6d8118,
                     0xd807aa98a3030242, 0x12835b0145706fbe,
                     0x243185be4ee4b28c, 0x550c7dc3d5ffb4e2,
                     0x72be5d74f27b896f, 0x80deb1fe3b1696b1,
                     0x9bdc06a725c71235, 0xc19bf174cf692694,
                     0xe49b69c19ef14ad2, 0xefbe4786384f25e3,
                     0x0fc19dc68b8cd5b5, 0x240ca1cc77ac9c65,
                     0x2de92c6f592b0275, 0x4a7484aa6ea6e483,
                     0x5cb0a9dcbd41fbd4, 0x76f988da831153b5,
                     0x983e5152ee66dfab, 0xa831c66d2db43210,
                     0xb00327c898fb213f, 0xbf597fc7beef0ee4,
                     0xc6e00bf33da88fc2, 0xd5a79147930aa725,
                     0x06ca6351e003826f, 0x142929670a0e6e70,
                     0x27b70a8546d22ffc, 0x2e1b21385c26c926,
                     0x4d2c6dfc5ac42aed, 0x53380d139d95b3df,
                     0x650a73548baf63de, 0x766a0abb3c77b2a8,
                     0x81c2c92e47edaee6, 0x92722c851482353b,
                     0xa2bfe8a14cf10364, 0xa81a664bbc423001,
                     0xc24b8b70d0f89791, 0xc76c51a30654be30,
                     0xd192e819d6ef5218, 0xd69906245565a910,
                     0xf40e35855771202a, 0x106aa07032bbd1b8,
                     0x19a4c116b8d2d0c8, 0x1e376c085141ab53,
                     0x2748774cdf8eeb99, 0x34b0bcb5e19b48a8,
                     0x391c0cb3c5c95a63, 0x4ed8aa4ae3418acb,
                     0x5b9cca4f7763e373, 0x682e6ff3d6b2b8a3,
                     0x748f82ee5defb2fc, 0x78a5636f43172f60,
                     0x84c87814a1f0ab72, 0x8cc702081a6439ec,
                     0x90befffa23631e28, 0xa4506cebde82bde9,
                     0xbef9a3f7b2c67915, 0xc67178f2e372532b,
                     0xca273eceea26619c, 0xd186b8c721c0c207,
                     0xeada7dd6cde0eb1e, 0xf57d4f7fee6ed178,
                     0x06f067aa72176fba, 0x0a637dc5a2c898a6,
                     0x113f9804bef90dae, 0x1b710b35131c471b,
                     0x28db77f523047d84, 0x32caab7b40c72493,
                     0x3c9ebe0a15c9bebc, 0x431d67c49c100d4c,
                     0x4cc5d4becb3e42b6, 0x597f299cfc657e2a,
                     0x5fcb6fab3ad6faec, 0x6c44198c4a475817]
        self.m_h = [
                0x6a09e667f3bcc908,
                0xbb67ae8584caa73b,
                0x3c6ef372fe94f82b,
                0xa54ff53a5f1d36f1,
                0x510e527fade682d1,
                0x9b05688c2b3e6c1f,
                0x1f83d9abfb41bd6b,
                0x5be0cd19137e2179
        ]
        self.m_len = 0
        self.m_tot_len = 0
        self.m_block = [0 for i in range(2 * SHA512.SHA384_512_BLOCK_SIZE)]

    def memcpy(self, dest, dest_begin_index, src, length):
        for i in range(length):
            dest[dest_begin_index + i] = src[i]
        return dest

    def memset(self, input, shift_num, value, length):
        for i in range(length):
            input[shift_num + i] = value
        return input

    def SHA2_SHFR(self, x, n):
        return (x >> n) & ((1 << 64) - 1)     # & ((1 << 64) - 1) 64位防止溢出

    def SHA2_ROTR(self, x, n):
        return ((x >> n) | (x << ((8 << 3) - n))) & ((1 << 64) - 1)

    def SHA2_ROTL(self, x, n):
        return ((x << n) | (x >> ((8 << 3) - n))) & ((1 << 64) - 1)

    def SHA2_CH(self, x, y, z):
        return ((x & y) ^ (~x & z)) & ((1 << 64) - 1)

    def SHA2_MAJ(self, x, y, z):
        return ((x & y) ^ (x & z) ^ (y & z)) & ((1 << 64) - 1)

    def SHA512_F1(self, x):
        return (self.SHA2_ROTR(x, 28) ^ self.SHA2_ROTR(x, 34) ^ self.SHA2_ROTR(x, 39)) & ((1 << 64) - 1)

    def SHA512_F2(self, x):
        return (self.SHA2_ROTR(x, 14) ^ self.SHA2_ROTR(x, 18) ^ self.SHA2_ROTR(x, 41)) & ((1 << 64) - 1)

    def SHA512_F3(self, x):
        return (self.SHA2_ROTR(x, 1) ^ self.SHA2_ROTR(x, 8) ^ self.SHA2_SHFR(x, 7)) & ((1 << 64) - 1)

    def SHA512_F4(self, x):
        return (self.SHA2_ROTR(x, 19) ^ self.SHA2_ROTR(x, 61) ^ self.SHA2_SHFR(x, 6)) & ((1 << 64) - 1)

    def SHA2_UNPACK32(self, x, str, shift_num):
        str[shift_num + 3] = ((x & 255))
        str[shift_num + 2] = ((x >> 8) & 255)
        str[shift_num + 1] = ((x >> 16) & 255)
        str[shift_num + 0] = ((x >> 24) & 255)
        return str

    def SHA2_UNPACK64(self, x, str, shift_num):
        str[shift_num + 7] = (int((x) & 255))
        str[shift_num + 6] = (int((x >> 8) & 255))
        str[shift_num + 5] = (int((x >> 16) & 255))
        str[shift_num + 4] = (int((x >> 24) & 255))
        str[shift_num + 3] = (int((x >> 32) & 255))
        str[shift_num + 2] = (int((x >> 40) & 255))
        str[shift_num + 1] = (int((x >> 48) & 255))
        str[shift_num + 0] = (int((x >> 56) & 255))
        return str

    def SHA2_PACK64(self, str):
        res = (str[7]) | ((str[6]) << 8) | ((str[5]) << 16) | ((str[4]) << 24) | ((str[3]) << 32) \
              | ((str[2]) << 40) | ((str[1]) << 48) | ((str[0]) << 56)
        return res

    def transform(self, message, shift_num, block_nb):
        message_shift = message[shift_num:]
        w = [0 for i in range(80)]
        wv = [0 for i in range(8)]
        for i in range(block_nb):
            sub_block = message_shift[i << 7:]
            for j in range(16):
                w[j] = self.SHA2_PACK64(sub_block[j << 3:])
            for j in range(16, 80):
                w[j] = (self.SHA512_F4(w[j - 2]) + w[j - 7] + self.SHA512_F3(w[j - 15]) + w[j - 16]) & ((1 << 64) - 1)
            for j in range(8):
                wv[j] = self.m_h[j]
            for j in range(80):
                t1 = (wv[7] + self.SHA512_F2(wv[4]) + self.SHA2_CH(wv[4], wv[5], wv[6]) + self.sha512_k[j] + w[j]) & ((1 << 64) - 1)
                t2 = (self.SHA512_F1(wv[0]) + self.SHA2_MAJ(wv[0], wv[1], wv[2])) & ((1 << 64) - 1)
                wv[7] = wv[6]
                wv[6] = wv[5]
                wv[5] = wv[4]
                wv[4] = (wv[3] + t1) & ((1 << 64) - 1)
                wv[3] = wv[2]
                wv[2] = wv[1]
                wv[1] = wv[0]
                wv[0] = (t1 + t2) & ((1 << 64) - 1)
            for j in range(8):
                self.m_h[j] = (wv[j] + self.m_h[j]) & ((1 << 64) - 1)

    def update(self, message):
        Len = len(message)
        tmp_len = SHA512.SHA384_512_BLOCK_SIZE - self.m_len
        if Len < tmp_len:
           rem_len = Len
        else:
           rem_len = tmp_len
        self.m_block = self.memcpy(self.m_block, self.m_len, message, rem_len)
        if self.m_len + Len < SHA512.SHA384_512_BLOCK_SIZE:
            self.m_len += Len
            return
        new_len = Len - rem_len
        block_nb = int(new_len / SHA512.SHA384_512_BLOCK_SIZE)
        shifted_num = rem_len  # 移动位数
        self.transform(self.m_block, 0, 1)
        self.transform(message, shifted_num, block_nb)
        rem_len = new_len % SHA512.SHA384_512_BLOCK_SIZE
        shift_mess = message[block_nb << 7:]
        self.m_block = self.memcpy(self.m_block, 0, shift_mess, rem_len)
        self.m_len = rem_len
        self.m_tot_len += (block_nb + 1) << 7

    def final(self, digest):
        block_nb = 1 + ((SHA512.SHA384_512_BLOCK_SIZE - 17) < (self.m_len % SHA512.SHA384_512_BLOCK_SIZE))
        len_b = (self.m_tot_len + self.m_len) << 3
        pm_len = block_nb << 7
        self.m_block = self.memset(self.m_block, self.m_len, 0, pm_len - self.m_len)
        self.m_block[self.m_len] = 0x80
        self.m_block = self.SHA2_UNPACK32(len_b, self.m_block, pm_len-4)
        self.transform(self.m_block, 0, block_nb)
        for i in range(8):
            digest = self.SHA2_UNPACK64(self.m_h[i], digest, i << 3)
        return digest

def sha512(input):
    digest = ['' for i in range(SHA512.DIGEST_SIZE)]
    sha = SHA512()
    sha.update(input)
    digest = sha.final(digest)
    for i in range(len(digest)):
        digest[i] = hex(digest[i])
    return digest





if __name__ == '__main__':
    input = []
    for i in range(200):
        if i < 128:
            input.append(i)
        else:
            input.append(i % 128)
    digest = sha512(input)
    print(digest)
