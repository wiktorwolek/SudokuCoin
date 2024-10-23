from Crypto.PublicKey import RSA
import os

class Wallet:
    def __init__(self, port):
        self.port = port
        print(self.port)
        if os.path.exists(f'keys/{self.port}_priv.pem'):
            is_password_correct = False
            while not is_password_correct:
                is_password_correct = self.check_password()
            self.public_key = self.private_key.publickey().exportKey()
        else:
            self.password = input("You are new here, please enter password:\n")
            self.private_key, self.public_key = self.generate_keys()
            self.save_credentials()

    def generate_keys(self):
        key = RSA.generate(2048)
        private_key = key.export_key().decode('utf-8')
        public_key = key.publickey().export_key().decode('utf-8')
        return private_key, public_key

    def save_credentials(self):
        with open(f'keys/{self.port}_password.pem', 'wb') as f:
            f.write(self.password.encode('utf-8'))
        with open(f'keys/{self.port}_priv.pem', 'wb') as f:
            f.write(self.private_key.encode('utf-8'))
        with open(f'keys/{self.port}_pub.pem', 'wb') as f:
            f.write(self.public_key.encode('utf-8'))

    def check_password(self, ) -> bool:
        entered_password = input("Enter Your password\n")
        with open(f'keys/{self.port}_password.pem', 'rb') as f:
            if f.read().decode('utf-8') == entered_password:
                print("Loggin success!")
                with open(f'keys/{self.port}_priv.pem', 'rb') as f_priv:
                    self.private_key = RSA.importKey(f_priv.read())
                    return True
            else:
                print("Wrong password!\n")
                return False
