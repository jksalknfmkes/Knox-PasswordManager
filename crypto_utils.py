import os
import sys
import json
import base64
import hashlib
import pwinput
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def get_data_dir():
    try:
        knox_path = os.path.dirname(sys.argv[0])  
        data_dir = os.path.join(knox_path, 'knox_data')
        os.makedirs(data_dir, exist_ok=True)
        return data_dir
    except Exception as e:
        return None

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

data_dir = get_data_dir()
crypto_file = os.path.join(data_dir, 'key.enc')
users_file = os.path.join(data_dir, 'users.json')

def create_master_key(password):
    with open(users_file, 'r') as f:
        users = json.load(f)
    encrypted_salt_b64 = users[0]["salt"]  
    encrypted_salt = base64.b64decode(encrypted_salt_b64.encode('utf-8'))
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=encrypted_salt,
        iterations=100000,
    )
    master_key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return master_key

def decrypt_key_vault():
    with open(users_file, 'r') as f:  
        users = json.load(f)
    i = 1
    while i:
        if i <= 5:
            print("\033[92mВведите пароль для доступа к хранилищу:\033[0m")
            password = pwinput.pwinput(prompt="\033[91m>> \033[0m", mask='*')
            password_hash = hash_password(password)
            if password_hash == users[0]["password_hash"]:
                master_key = create_master_key(password)
                cipher = Fernet(master_key)
                with open(crypto_file, 'rb') as f:
                    data = f.read()
                    key_vault = cipher.decrypt(data)
                return key_vault
            else:
                print("\033[91mНеверный пароль! Повторите ввод.\033[0m")
                i += 1
                continue
        else:
            print("\033[91mВы превысили количество неудачных попыток! Попробуйте позже.\033[0m")
            sys.exit(0)
    