import os
import pyAesCrypt

bufferSize = 64 * 1024
password = input("Password: ")

#
# with open("config.ini", "rb") as fIn:
#     with open("config.py.aes", "wb") as fOut:
#         pyAesCrypt.encryptStream(fIn, fOut, password, bufferSize)

pyAesCrypt.decryptFile("../config.py.aes", "conf.py", password, bufferSize)
from conf import *
os.remove("conf.py")