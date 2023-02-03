
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from base64 import b64decode


class Decrypt:
    def __init__(self, message):
        self.message = message
        self.result = decode(message)


def decode(message):
    rsa_key = RSA.importKey(open('key.txt', "rb").read())
    cipher = PKCS1_v1_5.new(rsa_key)

    # divide the data in to chunks
    ciphertext = b''
    for i in range(0, len(message) // 256):
        ciphertext += cipher.decrypt(
            message[i * 256:(i + 1)*256], sentinel="error").decode('utf-8')
    return b64decode(ciphertext).decode('ascii')
