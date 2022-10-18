import os

import numpy
# from AES import AES as myAES, getK, strToKey, keyToStr
import struct
# from SHA512 import sha512

import os, random, struct
from Crypto.Cipher import AES

try:
    from Crypto.Util.Padding import pad, unpad
except ImportError:
    from Crypto.Util.py3compat import bchr, bord


    def pad(data_to_pad, block_size):
        padding_len = block_size - len(data_to_pad) % block_size
        padding = bchr(padding_len) * padding_len
        return data_to_pad + padding


    def unpad(padded_data, block_size):
        pdata_len = len(padded_data)
        if pdata_len % block_size:
            raise ValueError("Input data is not padded")
        padding_len = bord(padded_data[-1])
        if padding_len < 1 or padding_len > min(block_size, pdata_len):
            raise ValueError("Padding is incorrect.")
        if padded_data[-padding_len:] != bchr(padding_len) * padding_len:
            raise ValueError("PKCS#7 padding is incorrect.")
        return padded_data[:-padding_len]


def encrypt_file(key, data, chunksize=64 * 1024):
    iv = os.urandom(16)
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    filesize = len(data)
    out = bytes()
    out += struct.pack('<Q', filesize)
    out += iv
    pos = 0
    while pos < filesize:
        if pos + chunksize < len(data):
            chunk = data[pos:chunksize]
        else:
            chunk = data[pos:]
            chunk = pad(chunk, AES.block_size)
        pos += len(chunk)
        out += encryptor.encrypt(chunk)
    return out


def decrypt_file(key, data, chunksize=64 * 1024):
    filesize = struct.unpack('<Q', data[:8])[0]
    iv = data[8:24]
    data = data[24:]
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    encrypted_filesize = len(data)
    out = bytes()
    pos = 0
    while pos < encrypted_filesize:
        if pos + chunksize < len(data):
            chunk = data[pos:chunksize]
            pos += len(chunk)
            chunk = encryptor.decrypt(chunk)
        else:
            chunk = data[pos:]
            pos += len(chunk)
            chunk = encryptor.decrypt(chunk)
            chunk = unpad(chunk, AES.block_size)
        out +=chunk
    return out

