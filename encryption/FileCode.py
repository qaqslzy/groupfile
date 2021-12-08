import numpy
from AES import AES, getK
import struct
from SHA512 import sha512

class FileCode:

    def encodeFile(self, filepath, K):
        aes = AES()
        with open(filepath, "rb") as f:
           block_list = []
           while True:
              block = list(f.read(16))
              if not block:
                 break
              yu = len(block) % 16
              if yu != 0:
                 bu = [0 for i in range(16 - yu)]
                 block = block + bu
              block = numpy.array(block).reshape(4, -1)
              # print("block", block)
              block = aes.encode(block, K).tolist()
              block_list.append(block)
           block_list = numpy.array(block_list).reshape(1, -1)[0]
           # print("block_list", block_list)
           return block_list

    def decodeFile(self, filepath, K, code_list):
        aes = AES()
        with open(filepath, "wb") as f:
            block_num = int(code_list.shape[0] / 16)
            for i in range(block_num):
                block = code_list[i * 16:i * 16 + 16].reshape(4, 4)
                block = aes.decode(block, K)
                # print("decode block", block)
                block = block.reshape(1, -1)[0]
                for x in block:
                    f.write(struct.pack('B', x))

    def sha512File(self, filepath):
        """
        将文件以二进制读出，并进行信息摘要
        :param filepath: 文件地址
        :return: 摘要
        """
        with open(filepath, "rb") as f:
            content = list(f.read())
            digest = sha512(content)
            return digest


if __name__ == '__main__':

    K = getK()   # 随机获取K用于AES加密

    print(K)
    filecode = FileCode()

    digest = filecode.sha512File("log.txt")     # 对文件进行摘要
    print(digest)

    code = filecode.encodeFile("log.txt", K)    # 文件AES加密  生成加密后的序列
    # print("code", code)

    filecode.decodeFile("log1.txt", K, code)     # 文件解密  生成解密后的文件










