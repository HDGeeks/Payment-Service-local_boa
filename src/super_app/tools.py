import base64
import json
import random
import re
import string
import time
import uuid
from base64 import b64decode, b64encode

import environ
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pss
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.serialization import load_der_public_key
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

env = environ.Env()
environ.Env.read_env(DEBUG=(bool, False))


def sign(request):
    privateKey = env("private_key")
    exclude_fields = [
        "sign",
        "sign_type",
        "header",
        "refund_info",
        "openType",
        "raw_request",
    ]
    join = []
    for key in request:
        if key in exclude_fields:
            continue
        if key == "biz_content":
            biz_content = request["biz_content"]
            for k in biz_content:
                join.append(k + "=" + biz_content[k])
        else:
            join.append(key + "=" + request[key])
    join.sort()
    separator = "&"
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


def verify(request, sign):
    publicKey = env("ET_public_key")
    exclude_fields = [
        "sign",
        "sign_type",
        "header",
        "refund_info",
        "openType",
        "raw_request",
    ]
    join = []
    signature = sign
    for key in request:
        if key in exclude_fields:
            continue
        if key == "biz_content":
            biz_content = request["biz_content"]
            for k in biz_content:
                join.append(k + "=" + biz_content[k])
        else:
            join.append(key + "=" + request[key])
    join.sort()
    separator = "&"
    message = str(separator.join(join))
    return VerifyWithRSA(message, publicKey, signature, "SHA256withRSA")


def VerifyWithRSA(
    message,
    key,
    signature,
    sign_type="SHA256withRSA",
):
    if sign_type == "SHA256withRSA":
        decoded_signature = base64.b64decode(signature)
        rsa_key = RSA.importKey(key)
        mesage_hash = SHA256.new(message.encode("utf-8"))
        verifier = pss.new(rsa_key)
        try:
            verifier.verify(
                mesage_hash,
                decoded_signature,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )

        except (ValueError, TypeError):
            return False

        return True

    else:
        return "Only allowed to the type SHA256withRSA hash"


def createMerchantOrderId():
    return str(int(time.time()))


def createTimeStamp():
    return str(int(time.time()))


def createNonceStr():
    result_str = "".join(
        random.choices(
            string.ascii_uppercase + string.ascii_lowercase + string.digits, k=32
        )
    )
    return result_str
