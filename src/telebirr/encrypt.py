
import base64
from ctypes import sizeof
import json
import re


from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA


class Encrypt:
    def __init__(self, public_key="MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvOQhP9CgRFKV4D8mIJJkgSFwmhomk7vQ6Cwg5uAea+efmZDOYPvNzk363pFrfaHgqWaHOqN2OMsGZJmv/7+2TIyAsVfeGOjqCJWoK5XNgQaoqLBlstd7Zzl4IAxUadCeNV28HhjrRZSg3i3BzxdiGGDiV3MmWEbOSGdFSXYAR9+2rdQgGSZdfXl+53YkEomMlnf+zNazL6zx4BkKljehWYgUzdbLVCdfaf1xMzurCcOQeeq4BuFvT4s4yFk9J3tq5Lpl+eo13zvdy2Va3vPMAKrRNvewA5OiBvc08wJUrj2zZbYNErhOrhIFNZKyoXczXPzneAO/7cxZmjS4zQddNwIDAQAB"):

        # decrypt the response to telebirr api using the public key from telebirr

        self.public_key = public_key

        ussd = {
            "code": 0,
            "msg": 'success',
            "data":
            {
                "outTradeNo": 'T0533111222S001114129',
                "tradeNo": 'R334E456TF65H7',
            }
        }

        self.result = self.__encrypt_response(ussd=ussd, public_key=public_key)

    @staticmethod
    def __encrypt_response(ussd, public_key):
        """
        this is static function used ,
        to sign the request using RSA algorithm
        """
        public_key = re.sub("(.{64})", "\\1\n",
                            public_key.replace("\n", ""), 0, re.DOTALL)
        public_key = '-----BEGIN CERTIFICATE-----\n{}\n-----END CERTIFICATE-----'.format(
            public_key)
        ussd_json = json.dumps(ussd)
        encrypt = Encrypt.encrypt(public_key=public_key, msg=ussd_json)
        return encrypt

    @staticmethod
    def encrypt(public_key, msg):
        rsa = RSA.importKey(public_key)
        cipher = PKCS1_v1_5.new(rsa)
        ciphertext = b''
        for i in range(0, len(msg) // 117):
            ciphertext += cipher.encrypt(msg[i *
                                         117:(i + 1) * 117].encode('utf8'))
        ciphertext += cipher.encrypt(msg[(len(msg) // 117)
                                     * 117: len(msg)].encode('utf8'))
        return base64.b64encode(ciphertext).decode('ascii')


mug = Encrypt()
