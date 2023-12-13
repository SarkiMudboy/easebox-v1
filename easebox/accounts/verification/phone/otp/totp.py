import hmac
import base64
from sys import byteorder
import time
import datetime


def low_order_4_bits(val):
    return val & 0b1111

def last_31_bits(p):
    res = bytearray()
    res.append(p[0] & 0x7F)

    for b in p[1:]:
        res.append(b & 0xFF)

    return res

def truncate(hs):

    offset = low_order_4_bits(hs[19])
    p = hs[offset:offset+4]

    return last_31_bits(p)


def hotp(k, c) -> int:

    counter_bytes = c.to_bytes(8, byteorder="big")
    hs_hmac = hmac.new(k, counter_bytes, "sha1")
    hs = hs_hmac.digest()
    s_bits = truncate(hs)
    s_num = int(s_bits.hex(), 16)

    return s_num % 10 ** 6

