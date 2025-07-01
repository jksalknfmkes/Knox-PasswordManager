import os
import sys
import json

def get_data_dir():
    try:
        knox_path = os.path.dirname(sys.argv[0])  
        data_dir = os.path.join(knox_path, 'knox_data')
        os.makedirs(data_dir, exist_ok=True)
        return data_dir
    except Exception as e:
        return None

data_dir = get_data_dir()
if data_dir is None:
    print("Не удалось определить директорию. Программа завершится.")
    sys.exit(1)

users_file = os.path.join(data_dir, 'users.json')
vault_file = os.path.join(data_dir, 'vault.json')
system_file = os.path.join(data_dir, 'system_status.json')
crypto_file = os.path.join(data_dir, 'key.enc')

if not os.path.exists(crypto_file):
    open(crypto_file, 'w').close()

for file_path in [users_file, vault_file, system_file, crypto_file]:
    if not os.path.exists(file_path):
        if file_path == system_file:
            data = [
                {"service": "pwned_check", "status": "on"},
                {"service": "reliability_check", "status": "on"}
            ]
            with open(file_path, 'w') as f:
                f.write(json.dumps(data, indent=4))
        else:
            with open(file_path, 'w') as f:
                f.write('[]')
with open(users_file, 'r') as f:
    users = json.load(f)

import commands
import check_pass
from ui import show_logo
from sign_up import registration
from sign_in import authentication

def main():
    show_logo()
    if not users:
        registration()
    else:
        authentication()

if __name__ == "__main__":
    main()

while True:
    command = input("\033[91m@knox >>\033[0m").strip().lower()
    if command == "noxadd":
        commands.noxadd()
    elif command == "noxshow":
        commands.noxshow()
    elif command == "help":
        commands.help()
    elif command == "noxdel":
        commands.noxdelete()
    elif command == "noxdel_profile":
        commands.noxdelete_profile()
    elif command == "noxdel_vault":
        commands.noxdelete_vault()
    elif command == "noxst_change":
        commands.system_status_change()
    elif command == "noxcheck_pass":
        check_pass.checkpass_manual()
    elif command == "noxmodify":
        commands.modify()
    elif command == "noxgenerate":
        commands.generate_pass()
    elif command == "noxdel_pass":
        commands.del_pass()
    elif command == "noxkey":
        commands.noxkey()
    elif command == "noxkey_generation":
        commands.noxkey_generation()
    elif command == "exit":
        print("\033[91mВыход...\033[0m")
        break
    else:
        print("\033[91mНеизвестная команда. Напиши 'help', чтобы увидеть список команд.\033[0m")