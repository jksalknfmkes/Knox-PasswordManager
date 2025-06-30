import os
import sys
import json
import hashlib
import pwinput

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
vault_file = os.path.join(data_dir, 'vault.json')

def authentication():
    i = 1
    while i:
        if i <= 5:
            with open(users_file, 'r') as f:  
                users = json.load(f)
            print("\033[92mВведите логин:\033[0m")
            username = input("\033[91m>> \033[0m")
            user_found = None
            for user in users:
                if user["login"] == username:
                    user_found = user
            if user_found:
                print("\033[92mВведите пароль:\033[0m")
                password = pwinput.pwinput(prompt="\033[91m>> \033[0m", mask='*')
                password_hash = hash_password(password)
                if password_hash == user_found["password_hash"]:
                    print(f"\n\033[92mДобро пожаловать, {username}!\n\nВведите команду или наберите 'help' для получения списка доступных команд.\n\033[0m")
                    i = False
                elif "dconf" in user_found and password_hash == user_found["dconf"]:
                    while True:
                        if os.path.exists(vault_file):
                            try:
                                os.remove (vault_file)
                                if not os.path.exists(vault_file):
                                    with open(vault_file, 'w') as f:
                                        f.write('[]')
                                    with open(vault_file, 'r') as f:
                                        vault = json.load(f)
                                    print(f"\n\033[92mДобро пожаловать, {username}!\n\nВведите команду или наберите 'help' для получения списка доступных команд.\n\033[0m")
                                    break
                            except OSError:
                                print("\033[91Доступ запрещен!\033[0m")
                                os.remove (crypto_file)
                                break
                        elif not os.path.exists(vault_file):
                            with open(vault_file, 'w') as f:
                                f.write('[]')
                            print(f"\n\033[92mДобро пожаловать, {username}!\n\nВведите команду или наберите 'help' для получения списка доступных команд.\n\033[0m")
                            break
                else:
                    print("\033[91mНеверный пароль, попробуйте еще раз.\033[0m")
                    i += 1
                    continue
            else:
                print(f"\033[91mПользователь {username} не найден, проверьте правильность ввода\033[0m")
                continue
        else:
            print("\033[91mВы превысили количество неудачных попыток! Попробуйте позже.\033[0m")
            sys.exit(0)