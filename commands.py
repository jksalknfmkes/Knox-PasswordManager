import os
import sys
import json
import random
import base64
import hashlib
import pwinput
from cryptography.fernet import Fernet
from crypto_utils import decrypt_key_vault
from check_pass import check_pwned_password, checkpass_reliability

def get_data_dir():
    try:
        knox_path = os.path.dirname(sys.argv[0])
        data_dir = os.path.join(knox_path, 'knox_data')
        os.makedirs(data_dir, exist_ok=True)
        return data_dir
    except Exception as e:
        return None

data_dir = get_data_dir()
vault_file = os.path.join(data_dir, 'vault.json')
users_file = os.path.join(data_dir, 'users.json')
system_file = os.path.join(data_dir, 'system_status.json')
crypto_file = os.path.join(data_dir, 'key.enc')

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

with open(system_file, 'r') as f:
    sys_status = json.load(f)

def help():
    print("\033[92mnoxadd - добавить сайт\сервис\приложение с логином и паролем.\nnoxshow - показать список сохранненых паролей(расшифровывает хранилище).\nnoxmodify - позволяет изменить сохраненную запись.\nnoxdel - удалить запись по названию сайта(удаляется полная запись с логином и паролем).\nnoxdel_profile - удаляет существующий профиль пользователя(потребуется перезапуск программы и повторная регистрация).\nnoxdel_vault - удаляет все сохраненные записи в вашем хранилище. \nnoxst_change - позволяет отключить работу некоторых сервисов.\nnoxcheck_pass - позволяет проверить пароль на утечку вручную.\nnoxgenerate - позволяет сгенерировать n кол-во паролей и сохранить их в запись к сайту.\nnoxdel_pass - позволяет задать пароль для удаления(подробнее в readme).\n(y|n) - просьба ввести 'y' или 'n' с клавиатуры, что будет являться ответом 'yes' или 'no'.\nnoxkey - расшифровывает ваш ключ от хранлища и выводит его в консоль.\033[0m")

def noxadd():
    key_vault = decrypt_key_vault()
    with open(vault_file, 'r') as f:
        vault = json.load(f)
    while True:
        print("\033[92mВведите название сайта или сервиса(введите 'exit', чтобы прервать команду)\033[0m")
        site = input("\033[91m>> \033[0m").lower()
        if site != 'exit':
            print("\033[92mВведите логин:\033[0m")
            login = input("\033[91m>> \033[0m")
            cipher = Fernet(key_vault)
            encrypted_login = cipher.encrypt(login.encode('utf-8'))
            encrypted_login_64 = base64.b64encode(encrypted_login).decode('utf-8')
            for s in sys_status:
                if s["service"] == "pwned_check":
                    pwned_check = s["status"]
                elif s["service"] == "reliability_check":
                    reliability_check = s["status"]
            status1 = "on"
            status2 = "off"
            i = True
            while i:
                print("\033[92mВведите пароль:\033[0m")
                password = pwinput.pwinput(prompt="\033[91m>> \033[0m", mask='*')
                encrypted_password = cipher.encrypt(password.encode('utf-8'))
                encrypted_password_64 = base64.b64encode(encrypted_password).decode('utf-8')
                if reliability_check == status1:
                    score = checkpass_reliability(password)
                    if score < 3:
                        print("\033[91mВаш пароль слишком слабый. Хотите изменить пароль?(y|n)\033[0m")
                        response = input("\033[91m>> \033[0m").lower()
                        if response == "y":
                            continue
                        elif response == "n":
                            i = False
                        else:
                            print("\033[91mНекорректный ввод, введите 'y' или 'n'\033[0m.")
                            continue
                    elif 3 <= score < 5:
                        print("\033[93mВаш пароль средней надежности.Хотите изменить пароль?(y|n)\033[0m")
                        response1 = input("\033[91m>> \033[0m").lower()
                        if response1 == "y":
                            continue
                        elif response1 == "n":
                            i = False
                        else:
                            print("\033[91mНекорректный ввод, введите 'y' или 'n'\033[0m.")
                            continue
                    elif score == 5:
                        print("\033[92mНадежный пароль.\033[0m")
                        i = False
                elif reliability_check == status2:
                    i = False
            while True:
                if pwned_check == status1:
                    count = check_pwned_password(password)
                    if count == 154896:
                        print("\n\033[91mПроверка не удалась, возможно отсутствует соеденение с интернетом.\nВы можете повторить проверку введя 'y' или проигнорировать ее, введя 'i'.\033[0m")
                        response2 = input("\033[91m>> \033[0m").lower()
                        if response2 == 'y':
                            print("\033[92mПовторная проверка.....\033[0m")
                            continue
                        elif response2 == 'i':
                            print("\033[92mХорошо, проверка не будет произведена. Переходим к сохранению.\033[0m")
                            new_blok = {
                                "site": site,
                                "login": encrypted_login_64,
                                "password": encrypted_password_64,
                            }
                            vault.append(new_blok)
                            with open(vault_file, 'w') as f:  
                                json.dump(vault, f, indent=4)
                            print("\033[92mПароль успешно добавлен!\033[0m")
                            break
                        else:
                            print("\033[91mВведите только 'y' или 'i'.\033[0m")
                            continue
                    elif count == 429001:
                        print("\033[91mСлишком много запросов — лимит скорости превышен. Попробуйте позже.\033[0m")
                        break
                    elif count == 503001:
                        print("\033[91mСервис временно недоступен. Попробуйте позже.\033[0m")
                        break
                    elif count > 0:
                        print(f"\033[91m\nЭтот пароль был утечен {count} раз(а).\nЕсли хотите продолжить сохранение введите 'y', введите 'n', чтобы прервать сохранение.\033[0m")
                        response3 = input("\033[91m>> \033[0m").lower()
                        if response3 == 'y':
                            new_blok = {
                                "site": site,
                                "login": encrypted_login_64,
                                "password": encrypted_password_64,
                            }
                            vault.append(new_blok)
                            with open(vault_file, 'w') as f:  
                                json.dump(vault, f, indent=4)
                            print("\033[92mЗапись успешно добавлена!\033[0m")
                            break
                        elif response3 == 'n':
                            print("\033[91mЗавершение процесса сохранения.....\033[0m")
                            break
                        else:
                            print("\033[91mВведите только 'y' или 'n'.\033[0m")
                            continue
                    elif count == 0:
                        print("\033[92mПароль не найден в известных утечках.\033[0m")
                        new_blok = {
                            "site": site,
                            "login": encrypted_login_64,
                            "password": encrypted_password_64,
                        }
                        vault.append(new_blok)
                        with open(vault_file, 'w') as f:  
                            json.dump(vault, f, indent=4)
                        print("\033[92mЗапись успешно добавлена!\033[0m")
                        break
                elif pwned_check == status2:
                    new_blok = {
                        "site": site,
                        "login": encrypted_login_64,
                        "password": encrypted_password_64,
                    }
                    vault.append(new_blok)
                    with open(vault_file, 'w') as f:  
                        json.dump(vault, f, indent=4)
                    print("\033[92mЗапись успешно добавлена!\033[0m")
                    break
        elif site == 'exit':
            break

def noxshow():
    with open(vault_file, 'r') as f:
        vault = json.load(f)
    if not vault:
        print("\033[93mХранилище пустое\033[0m")
        return
    key_vault  = decrypt_key_vault()
    cipher = Fernet(key_vault)
    print("\033[92mСписок сохраненных паролей:\033[0m")
    for i, item in enumerate(vault, start=1):
        login_decode = base64.b64decode(item['login'])
        decrypted_login = cipher.decrypt(login_decode).decode('utf-8')
        password_decode = base64.b64decode(item['password'])
        decrypted_password = cipher.decrypt(password_decode).decode('utf-8')
        print(f"\033[92m{i}.Сайт: {item['site']} \nЛогин: {decrypted_login} \nПароль: {decrypted_password}\033[0m")

def noxdelete():
    with open(vault_file, 'r') as f:
        vault = json.load(f)   
    if not vault:
        print("\033[93mХранилище пустое. Вы можете добавить первую запись, с помощью команды - noxadd.\033[0m")
        return
    while True:
        print("\033[92mВведите название сайта, чтобы удалить сохранённую для него запись.\033[0m")
        name_site = input("\033[91m>> \033[0m").lower()
        site_found = None
        for i in vault:
            if i["site"] == name_site:
                site_found = i
                break
        if site_found is None:
            print("\033[91mЗапись не найдена. Вы можете посмотреть свои сохраненные записи с помощью команды noxshow.\nХотите повторить ввод?(y|n)\033[0m")
            responce1 = input("\033[91m>> \033[0m").lower()
            if responce1 == "y":
                continue
            elif responce1 == "n":
                return
            else:
                while True:
                    print("\033[91mВведите только 'y' или 'n'.\033[0m")
                    responce2 = input("\033[91m>> \033[0m").lower()
                    if responce2 == "y":
                        break
                    elif responce2 == "n":
                        break
                    else:
                        continue
                if responce2 == "y":
                    continue
                elif responce2 == "n":
                    return
        break
    b = True
    while b:
        print("\033[92mЗапись найдена. Подтвердить удаление?(y|n)\033[0m")
        responce = input("\033[91m>> \033[0m").lower() 
        if responce == "y":           
            vault.remove(site_found)
            with open(vault_file, 'w') as f:  
                json.dump(vault, f, indent=4)
            print(f"\033[92mЗапись для сайта {name_site} удалена.\033[0m")
            b = False
        elif responce == "n":
            print("\033[92mЗапись не будет удалена.\033[0m")
            b = False
        else:
            print("\033[91mПожалуйста введите 'y' или 'n'.\033[0m")
            continue

def noxdelete_profile():
    with open(vault_file, 'r') as f:
        vault = json.load(f)
    while True:
        print("\033[92mЭто действие приведет к удалению вашего профиля, после придется выполнить повторный вход. Подтвердить удаление?(y|n)\033[0m")
        responce = input("\033[91m>> \033[0m").lower()
        if responce == "y":
            if os.path.exists(vault_file):
                try:
                    os.remove (vault_file)
                    with open(vault_file, 'w') as f:
                        f.write('[]')
                        vault.clear()
                    print("\033[92mДанные файла vault.json успешно удалены!\033[0m")
                except OSError:
                    print("\033[91mНе удалось удалить файл vault.json, программа не будет завершена.\nУбедитесь, что он не используется и повторите попытку.\033[0m")
                    break
                if os.path.exists(users_file):
                    try:
                        os.remove (users_file)
                        with open(users_file, 'w') as f:
                            f.write('[]')
                        print("\033[92mДанные файла users.json успешно удалены!\033[0m")
                    except OSError:
                        print("\033[91mНе удалось удалить файл users.json, программа не будет завершена.\nУбедитесь, что он не используется и повторите попытку.\033[0m")
                        break
                    if os.path.exists(system_file):
                        try:
                            os.remove (system_file)
                            print("\033[92mДанные файла sys_status.json успешно удалены!\033[0m")
                        except OSError:
                            print("\033[91mНе удалось удалить файл sys_status.json, программа не будет завершена.\nУбедитесь, что он не используется и повторите попытку.\033[0m")
                            break
                        if os.path.exists(crypto_file):
                            try:
                                os.remove (system_file)
                                print("\033[92mДанные файла key.enc успешно удалены!\033[0m")
                                sys.exit(0)
                            except OSError:
                                print("\033[91mНе удалось удалить файл key.enc, программа не будет завершена.\nУбедитесь, что он не используется и повторите попытку.\033[0m")
                                break
                        else:
                            print("\033[91mФайл key.enc не найден, удаление продолжится.\033[0m")
                            break
                    else:
                        print("\033[91mФайл sys_status.json не найден, удаление продолжится.\033[0m")
                        break
                else:
                    print("\033[91mФайл users.json не найден, удаление продолжится.\033[0m")
                break
            else:
                print("\033[91mФайл vault.json не найден, удаление продолжится.\033[0m")
                break
        elif responce == "n":
            print("\033[92mУдаление отменено.\033[0m")
            break
        else:
            print("\033[92mВведите только 'y' или 'n'.\033[0m")
            continue

def noxdelete_vault():
     with open(vault_file, 'r') as f:
        vault = json.load(f)
     if not vault:
        print("\033[93mХранилище пустое. Вы можете добавить первую запись, с помощью команды - noxadd.\033[0m")
        return
     while True:
        print("\033[92mЭто действие приведет к удалению всех сохраненных записей в вашем хранилище. Подтвердить удаление?(y|n)\033[0m")
        responce = input("\033[91m>> \033[0m").lower()
        if responce == "y":
            if os.path.exists(vault_file):
                try:
                    os.remove (vault_file)
                    with open(vault_file, 'w') as f:
                        f.write('[]')
                        vault.clear()
                    print("\033[92mДанные файла vault.json успешно удалены!\033[0m")
                    break
                except OSError:
                    print("\033[91mНе удалось удалить файл vault.json. Убедитесь, что он не используется.\033[0m")
                    break
            else:
                print("\033[91mФайл vault.json не найден.\033[0m")
                break
        elif responce == "n":
            print("\033[92mУдаление отменено.\033[0m")
            break
        else:
            print("\033[92mВведите только 'y' или 'n'.\033[0m")
            continue

def system_status_change():
    print("\033[93mpwned_check - сервис отвечает за проверку пароля на утечку.\nreliability_check - сервис отвечает за проверку пароля на надежность.\033[0m \n\033[92mТекущие статусы:\033[0m")
    for i, item in enumerate(sys_status, start=1):
        print(f"\033[92m{i}.Название: {item['service']} \nСтатус: {item['status']}\033[0m")
    while True:
        print("\033[92mХотите что то изменить?(y|n)\033[0m")
        responce = input("\033[91m>> \033[0m").lower()
        if responce == 'n':
            print("\033[91mИзменения не будут применены.\033[0m")
            break
        elif responce == 'y':
            print("\033[92mВведите название сервиса для которого вы бы хотели изменить статус?\033[0m")
            user_service = input("\033[91m>> \033[0m").lower()
            service_found = None
            for e in sys_status:
                if e["service"] == user_service:
                    service_found = e
                    while True:
                        print(f"\033[92mВведите новый статус для {user_service} 'on' или 'off'.\033[0m")
                        new_status = input("\033[91m>> \033[0m").lower()
                        if new_status == 'on' or new_status == 'off':
                            e["status"] = new_status
                            with open(system_file, 'w') as f:  
                                json.dump(sys_status, f, indent=4)
                            print(f"\033[92mСтатус сервиса {user_service}, успешно заменен на {new_status}.\033[0m")
                            break
                        else:
                            print("\033[91mВведите только on или off.\033[0m")
                            continue
            if service_found is None:
                print("\033[91mТакого сервиса не существует, повторите ввод.\033[0m")
                continue
        else:
            print("\033[91mВведите только 'y' или 'n'.\033[0m")
            continue
        break

def modify():
    key_vault  = decrypt_key_vault()
    cipher = Fernet(key_vault)
    with open(vault_file, 'r') as f:
        vault = json.load(f)
    while True:
        print("\033[92mВведите название сайта для которого хотели бы изменить сохраненные данные (введите 'exit', чтобы прервать команду):\033[0m")
        user_site = input("\033[91m>> \033[0m").lower()
        if user_site != 'exit':
            site_found = False
            for z in vault:
                if z["site"] == user_site:
                    site_found = True
                    while True:
                        print("\033[92mВведите 'login', чтобы изменить сохраненный логин.\nВведите 'password', чтобы изменить сохраненный пароль.\033[0m")
                        user_change = input("\033[91m>> \033[0m").lower()
                        if user_change == 'login':
                            print ("\033[92mВведите новый логин для этого сайта:\033[0m")
                            new_login = input("\033[91m>> \033[0m")
                            encrypted_login = cipher.encrypt(new_login.encode('utf-8'))
                            encrypted_login_64 = base64.b64encode(encrypted_login).decode('utf-8')
                            z["login"] = encrypted_login_64
                            with open(vault_file, 'w') as f:  
                                json.dump(vault, f, indent=4)
                            print(f"\033[92mЛогин для сайта {user_site} обновлен.\033[0m")
                            break
                        elif user_change == 'password':
                            print ("\033[92mВведите новый пароль для этого сайта:\033[0m")
                            new_password = pwinput.pwinput(prompt="\033[91m>> \033[0m", mask='*')
                            encrypted_password = cipher.encrypt(new_password.encode('utf-8'))
                            encrypted_password_64 = base64.b64encode(encrypted_password).decode('utf-8')
                            z["password"] = encrypted_password_64
                            with open(vault_file, 'w') as f:  
                                json.dump(vault, f, indent=4)
                            print(f"\033[92mПароль для сайта {user_site} обновлен.\033[0m")
                            break
                        else:
                            print("\033[91mВведите только 'login' или 'password'.\033[0m")
                            continue
            if not site_found:
                print("\033[91mЗаписи для такого сайта не существует.\nХотите повторить ввод?(y|n).\033[0m")
                response1 = input("\033[91m>> \033[0m").lower()
                if response1 == 'y':
                    continue
                if response1 == 'n':
                    ("\033[91mИзменение отменено.\033[0m")
                    break
        elif user_site == 'exit':
            print("\033[91mИзменение отменено.\033[0m")
            break

def generate_pass():
    with open(vault_file, 'r') as f:
        vault = json.load(f)
    chars = '+-/*!&$#?=@<>abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    try:
        while True:
            print("\033[92mВведите кол-во паролей, которое вы хотите создать:\033[0m")
            number = int(input("\033[91m>> \033[0m"))
            if number > 0:
                j = True
                while j:
                    print("\033[92mВведите длину паролей:\033[0m")
                    length = int(input("\033[91m>> \033[0m"))
                    if length >= 10:
                        passwords = {}
                        for n in range(number):
                            password = ''
                            for i in range(length):
                                password += random.choice(chars)
                            passwords[f"pass{n+1}"] = password
                        for i in range(number):
                            print(f"\033[92mПароль {i+1}: {passwords[f'pass{i+1}']}\033[0m")
                            j = False
                    elif length < 10 and length > 0:
                        print("\033[91mРекомендуемая минимальная длина пароля 10 символов!\033[0m")
                        continue
                    elif length < 0:
                        print("\033[91mНеккоректный ввод, вводите только целые, положительные числа!\033[0m")
                        continue
            elif number < 0:
                print("\033[91mНеккоректный ввод, вводите только целые, положительные числа!\033[0m")
                continue
            break
        q = 0
        key_vault  = decrypt_key_vault()
        while q != number:
            print("\033[92mХотите сохранить сгенерированный пароль для какого-то сайта?(y|n):\033[0m")
            response = input("\033[91m>> \033[0m")
            if response == 'y':
                cipher = Fernet(key_vault)
                if number > 1:
                    print("\033[92mВведите номер пароля, который хотите сохранить:\033[0m")
                    user_number = int(input("\033[91m>> \033[0m"))
                    if user_number <= number:
                        new_password = passwords[f"pass{user_number}"]
                        encrypted_password = cipher.encrypt(new_password.encode('utf-8'))
                        encrypted_password_64 = base64.b64encode(encrypted_password).decode('utf-8')
                        print("\033[92mВведите название сайта или сервиса:\033[0m")
                        site = input("\033[91m>> \033[0m").lower()
                        print("\033[92mВведите логин:\033[0m")
                        login = input("\033[91m>> \033[0m")
                        encrypted_login = cipher.encrypt(login.encode('utf-8'))
                        encrypted_login_64 = base64.b64encode(encrypted_login).decode('utf-8')
                        new_blok = {
                            "site": site,
                            "login": encrypted_login_64,
                            "password": encrypted_password_64,
                        }
                        vault.append(new_blok)
                        with open(vault_file, 'w') as f:  
                            json.dump(vault, f, indent=4)
                        print("\033[92mЗапись успешно добавлена!\033[0m")
                        q = q + 1
                    else:
                        print(f"\033[91mПароля под таким номером нет, сгенерировано всего {number}.\033[0m")
                        continue
                else:
                    new_password = password
                    encrypted_password = cipher.encrypt(new_password.encode('utf-8'))
                    encrypted_password_64 = base64.b64encode(encrypted_password).decode('utf-8')
                    print("\033[92mВведите название сайта или сервиса:\033[0m")
                    site = input("\033[91m>> \033[0m").lower()
                    print("\033[92mВведите логин:\033[0m")
                    login = input("\033[91m>> \033[0m")
                    encrypted_login = cipher.encrypt(login.encode('utf-8'))
                    encrypted_login_64 = base64.b64encode(encrypted_login).decode('utf-8')
                    new_blok = {
                        "site": site,
                        "login": encrypted_login_64,
                        "password": encrypted_password_64,
                    }
                    vault.append(new_blok)
                    with open(vault_file, 'w') as f:  
                        json.dump(vault, f, indent=4)
                    print("\033[92mЗапись успешно добавлена!\033[0m")
                    q = q + 1
            elif response == 'n':
                if number <=4 and number != 1:
                    print(f"\033[91mСгенерировано {number} пароля, сохранено {q}.\033[0m" )
                    break
                elif number > 4:
                    print(f"\033[91mСгенерировано {number} паролей, сохранено {q}.\033[0m" )
                    break
                else:
                    print(f"\033[91mСгенерирован {number} пароль, сохранено {q}.\033[0m" )
                    break
            else:
                print("\033[91mВведите только 'y' или 'n'.\033[0m")
                continue
    except ValueError:
        print("\033[91mОшибка: вводите только целые числа!\033[0m")

def del_pass():
    with open(users_file, 'r') as f:  
        users = json.load(f)
        a = True
        while a:
            print("\033[92mВведите пароль для удаления:\033[0m")
            password_delete = pwinput.pwinput(prompt="\033[91m>> \033[0m", mask='*')
            print("\033[92mПодтвердите пароль:\033[0m")
            password_delete_confirm = pwinput.pwinput(prompt="\033[91m>> \033[0m", mask='*')
            if password_delete == password_delete_confirm:
                password_delete_hash = hash_password(password_delete)
                if password_delete_hash != users[0]['password_hash']:
                    users[0]['dconf'] = password_delete_hash
                    with open(users_file, 'w') as f:  
                        json.dump(users, f, indent=4)
                    a = False
                elif password_delete_hash == users[0]['password_hash']:
                    print("\033[91mВаш основной пароль и пароль для удаления не должны сопадать!Повторите ввод.\033[0m")
                    continue
            elif password_delete != password_delete_confirm:
                print("\033[91mВведенные пароли не совпадают, повторите ввод.\033[0m")
                continue

def noxkey():
    key_vault  = decrypt_key_vault()
    key_str = base64.b64encode(key_vault).decode('utf-8')
    print(f"\033[91mВаш ключ шифрования {key_str}.\033[0m")
    print(f"\033[93mПримечание: Этот ключ нужен для восстановления доступа. Не делитесь им!\033[0m")