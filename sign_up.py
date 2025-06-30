import os
import sys
import json
import base64
import hashlib
import pwinput
from cryptography.fernet import Fernet
from crypto_utils import create_master_key

def get_data_dir():
    try:
        knox_path = os.path.dirname(sys.argv[0])  
        data_dir = os.path.join(knox_path, 'knox_data')
        os.makedirs(data_dir, exist_ok=True)
        return data_dir
    except Exception as e:
        return None

data_dir = get_data_dir()
crypto_file = os.path.join(data_dir, 'key.enc')
users_file = os.path.join(data_dir, 'users.json')

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def registration():
    with open(users_file, 'r') as f:  
        users = json.load(f)
    while True:
        print("\033[92mПриветствую вас в Knox. Вы можете зарегистрироваться, введя 'y' или выйти введя — 'exit'.\033[0m")
        response = input("\033[91m>> \033[0m").lower()
        if response == "y":
            print("\033[92mВведите имя пользователя: \033[0m")
            username = input("\033[91m>> \033[0m")
            while True:
                print("\033[92mВведите пароль:\033[0m")
                password = pwinput.pwinput(prompt="\033[91m>> \033[0m", mask='*')
                print("\033[92mВведите пароль повторно:\033[0m")
                password_confirm = pwinput.pwinput(prompt="\033[91m>> \033[0m", mask='*')
                if password == password_confirm:
                    password_hash = hash_password(password)
                    salt = os.urandom(16)
                    temp_key = hashlib.sha256(password.encode()).digest()
                    temp_key_b64 = base64.urlsafe_b64encode(temp_key) 
                    cipher = Fernet(temp_key_b64)
                    encrypted_salt = cipher.encrypt(salt)
                    encrypted_salt_b64 = base64.b64encode(encrypted_salt).decode('utf-8')
                    new_user = {
                        "login": username,
                        "password_hash": password_hash,
                        "salt": encrypted_salt_b64
                    }
                    users.append(new_user)
                    with open(users_file, 'w') as f:  
                        json.dump(users, f, indent=4)
                    print(f"\033[95mПользователь {username} успещно зарегестрирован.\033[0m")
                    break  
                elif password != password_confirm:
                    print("\033[91mПароли не совпадают, повторите ввод.\033[0m")
                    continue
        elif response == "exit":
            print("\033[91mВыход из программы...\033[0m")
            sys.exit(0)
        else:
            print("\033[91mВведите только 'y' или 'exit'.\033[0m")
            continue
        with open(users_file, 'r') as f:  
            users = json.load(f)
        master_key = create_master_key(password)
        key_vault = Fernet.generate_key()
        cipher1 = Fernet(master_key)
        key_vault_encrypt = cipher1.encrypt(key_vault)
        with open(crypto_file, 'wb') as f:
                f.write(key_vault_encrypt)
        print(f"\n\033[92mДобро пожаловать, {username}!\n\nВведите команду или наберите 'help' для получения списка доступных команд.\n\033[0m")
        break