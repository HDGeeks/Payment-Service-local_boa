import random
import uuid
import re
import time
import base64
import json
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pss
from base64 import b64decode, b64encode
from Crypto.Cipher import PKCS1_v1_5
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_der_public_key
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
import string
import environ

env = environ.Env()
environ.Env.read_env(DEBUG=(bool, False))


def sign(request):
    privateKey = env("private_key")
    exclude_fields = ["sign", "sign_type", "header",
                      "refund_info", "openType", "raw_request"]
    join = []
    for key in request:
        if key in exclude_fields:
            continue
        if key == "biz_content":
            biz_content = request["biz_content"]
            for k in biz_content:
                join.append(k+"="+biz_content[k])
        else:
            join.append(key+"="+request[key])
    join.sort()
    separator = '&'
    inputString = str(separator.join(join))
    return SignWithRSA(inputString, privateKey, "SHA256withRSA")


def SignWithRSA(data, key, sign_type="SHA256withRSA"):
    if sign_type == "SHA256withRSA":
        key_bytes = b64decode(key.encode("utf-8"))
        key = RSA.importKey(key_bytes)
        digest = SHA256.new()
        digest.update(data.encode("utf-8"))
        signer = pss.new(key)
        signature = signer.sign(digest)
        return b64encode(signature).decode("utf-8")
    else:
        return "Only allowed to the type SHA256withRSA hash"


def verify(request):
    # publicKey = env("public_key")
    publicKey = env("private_key")
    exclude_fields = ["sign", "sign_type", "header",
                      "refund_info", "openType", "raw_request"]
    join = []
    signature = request.pop["sign"]
    for key in request:
        if key in exclude_fields:
            continue
        if key == "biz_content":
            biz_content = request["biz_content"]
            for k in biz_content:
                join.append(k+"="+biz_content[k])
        else:
            join.append(key+"="+request[key])
    join.sort()
    separator = '&'
    inputString = str(separator.join(join))
    return VerifyWithRSA(inputString, publicKey, signature, "SHA256withRSA")


def VerifyWithRSA(message, key, signature, sign_type="SHA256withRSA",):
    if sign_type == "SHA256withRSA":
        decoded_signature = base64.b64decode(signature)
        rsa_key = RSA.importKey(key)
        mesage_hash = SHA256.new(message.encode('utf-8'))
        verifier = pss.new(rsa_key)
        try:
            verifier.verify(mesage_hash, decoded_signature)
            return True
        except(ValueError, TypeError):
            return False

    else:
        return "Only allowed to the type SHA256withRSA hash"


def createMerchantOrderId():
    return str(int(time.time()))


def createTimeStamp():
    return str(int(time.time()))


def createNonceStr():
    result_str = ''.join(random.choices(
        string.ascii_uppercase + string.ascii_lowercase + string.digits, k=32))
    return result_str

# class Decrypt:
#     def __init__(self, message):
#         self.message = message
#         self.result = decode(message)


def decrypt(public_key, payload):
    public_key = re.sub("(.{64})", "\\1\n",
                        public_key.replace("\n", ""), 0, re.DOTALL)
    public_key = '-----BEGIN PUBLIC KEY-----\n{}\n-----END PUBLIC KEY-----\n'.format(
        public_key)
    b64data = '\n'.join(public_key.splitlines()[1:-1])
    key = load_der_public_key(base64.b64decode(b64data), default_backend())

    signature = base64.b64decode(payload)
    decrypted = b''
    for i in range(0, len(signature), 256):
        partial = key.recover_data_from_signature(
            signature[i:i + 256 if i + 256 < len(signature) else len(signature)], PKCS1v15(), None)
        decrypted += partial
        print(decrypted)

        try:
            data_json = json.loads(decrypted)
            return data_json
        except json.JSONDecodeError:
            return f'this is empty json'
