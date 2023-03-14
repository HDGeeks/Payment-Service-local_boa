import random
import string

def generate_nonce(length):
    result_str = "".join(random.choices(string.ascii_uppercase +
                       string.digits + string.digits, k=length)
    )
    return result_str
