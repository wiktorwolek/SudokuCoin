from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Protocol.KDF import scrypt
from Crypto.Random import get_random_bytes

import os

class Wallet:
    def __init__(self, port, password):
        self.port = port
        self.balance = 0
        if os.path.exists(f'keys/{self.port}_priv.pem'):
            try:
                private_key_obj = self.decrypt_key(password)
                self.private_key = private_key_obj.export_key()
                self.public_key = private_key_obj.publickey().export_key()
                print("Hello")
            except:
                print("Wrong password\n")
        else:
            print("You are new here")
            self.private_key, self.public_key = self.generate_keys()
            self.save_credentials(password)

    def generate_keys(self):
        key = RSA.generate(2048)
        private_key = key.export_key()
        public_key = key.publickey().export_key()
        return private_key, public_key

    def save_credentials(self, password):
        os.makedirs(f'keys', exist_ok=True)
        encrypted_key, salt, iv = self.encrypt_key(password)
        with open(f'keys/{self.port}_salt.iv', 'wb') as f:
            f.write(salt + iv)
        with open(f'keys/{self.port}_priv.pem', 'wb') as f:
            f.write(encrypted_key)
        with open(f'keys/{self.port}_pub.pem', 'wb') as f:
            f.write(self.public_key)

    # def read_keys(self):
    #     entered_password = input("Enter Your password\n")
    #     self.priv_key = self.decrypt_key(entered_password)
    #     self.public_key = self.priv_key.publickey().export_key()
            
    def encrypt_key(self, password):
        salt = get_random_bytes(16)
        key = scrypt(password.encode(), salt, key_len=32, N=2**20, r=8, p=1)
        cipher = AES.new(key, AES.MODE_CBC)
        iv = cipher.iv # wektor 
# print(type(private_key_bytes)) 
        encrypted_key = cipher.encrypt(pad(self.private_key, AES.block_size))

        return encrypted_key, salt, iv
    
    def decrypt_key(self, password):
        with open(f'keys/{self.port}_salt.iv', 'rb') as f:
            salt_iv = f.read()
            salt, iv = salt_iv[:16], salt_iv[16:]
        
        with open(f'keys/{self.port}_priv.pem', 'rb') as f:
            encrypted_key = f.read()
        
        key = scrypt(password.encode(), salt, key_len=32, N=2**20, r=8, p=1)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        
        decrypted_pem = unpad(cipher.decrypt(encrypted_key), AES.block_size)
        return RSA.import_key(decrypted_pem)
    
    def show_balance(self):
        print(f"Current account balance: {self.balance}")

    def change_wallet_balance(self, amount):
        self.balance = self.balance + amount
    
    def read_pub_key_from_file(self,port):
        with open(f'keys/{port}_pub.pem', 'rb') as f:
            return f.read()
        
    def calculate_balance(self, address):
        balance = 0
        for block in self.chain:
            if block.data:
                for transaction_dict in block.data:
                    if 'recipient' in transaction_dict and transaction_dict['recipient'] == address:
                        balance += transaction_dict['amount']
                    if 'sender' in transaction_dict and transaction_dict['sender'] == address:
                        balance -= transaction_dict['amount']
        return balance

