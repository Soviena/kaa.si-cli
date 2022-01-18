import base64
from Crypto.Cipher import AES

pad = lambda s: s + (16 - len(s) % 16) * chr(16 - len(s) % 16) 
unpad = lambda s : s[:-ord(s[len(s)-1:])]

def encrypt(raw, key:bytearray, iv:bytearray ):
    raw = pad(raw)
    cipher = AES.new( key, AES.MODE_CBC, iv )
    return base64.b64encode(cipher.encrypt(str(raw).encode('utf8')))

def decrypt(enc, key:bytearray, iv:bytearray ):
    enc = base64.b64decode(enc)
    cipher = AES.new(key, AES.MODE_CBC, iv )
    return unpad(cipher.decrypt(enc))