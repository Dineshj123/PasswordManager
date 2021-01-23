from Crypto.Cipher import AES


class Key:
    def __init__(self,key):
        super(Key,self).__init__()
        self.key = key
    def encrypt(self):
        diff = 16 - len(self.key)
        if(len(self.key)>=16):
            return self.key[0:16]
        while(diff>0):
            diff = 16 - len(self.key)
            mod = diff%len(self.key)
            self.key = self.key+(self.key[0:mod+1])
            diff = 16 - len(self.key)
        return self.key[0:16]
    def getEncryptedKey(self):
        encryptKey = self.encrypt()
        return AES.new(encryptKey.encode("utf8").strip(), AES.MODE_CFB, encryptKey.encode("utf8").strip())

    def getDecryptedKey(self):
        decryptKey = self.encrypt()
        return AES.new(decryptKey.encode("utf8").strip(), AES.MODE_CFB, decryptKey.encode("utf8").strip())
        
        
