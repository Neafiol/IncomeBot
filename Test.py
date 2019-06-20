import json

import requests
from peewee import *
from peewee_encrypted_field import EncryptedField
from binascii import unhexlify
from functools import partial
from Crypto.Protocol import KDF
from Crypto.Hash import SHA512, HMAC


_SALT = unhexlify('48B755AB80CD1C3DA61182D3DCD2E3A2CA869B783618FF6551FB4B0CDC3B8066')  # some salt
_KEY_LENGTH = 32

key_derivation_fn = partial(
    KDF.PBKDF2,
    salt=_SALT,
    dkLen=_KEY_LENGTH,
    count=5000,
    prf=lambda p, s: HMAC.new(p, s, SHA512).digest()
)


# KDF usage


class SecureTable(Model):
    sensitive_data = EncryptedField()

    class Meta:
        db_table = 'SecureTable'


SecureTable.sensitive_data.key = key_derivation_fn("password")
new_secret = SecureTable(sensitive_data='My New BIG Secret')
new_secret.save()
