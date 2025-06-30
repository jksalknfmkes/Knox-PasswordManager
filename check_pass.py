import string
import hashlib
import pwinput
import requests

def check_pwned_password(password):
    password_hash = hashlib.sha1(password.encode()).hexdigest().upper()
    prefix = password_hash[:5]
    suffix = password_hash[5:]
    try:
        url = f"https://api.pwnedpasswords.com/range/{prefix}"
        response = requests.get(url)
        if response.status_code == 200:
            hashes = response.text.splitlines()
            for hash_entry in hashes:
                hash_suffix, count = hash_entry.split(':')
                if hash_suffix == suffix:
                    return int(count)
        elif response.status_code == 429:
            return 429001
        elif response.status_code == 503:
            return 503001
        return 0    
    except requests.exceptions.RequestException:
        return 154896

def checkpass_reliability(password):
    length = len(password) >= 10
    figure_case = any(char.isdigit() for char in password)
    upper_case = any(char.isupper() for char in password)
    lower_case = any(char.islower() for char in password)
    special_char = any(char in string.punctuation for char in password)

    characters = [figure_case, upper_case, lower_case, special_char, length]

    score = sum(characters)
    return int(score)

def checkpass_manual():
    print("\033[92mВведите пароль который хотите проверить на утечку:\033[0m")
    password = pwinput.pwinput(prompt="\033[91m>> \033[0m", mask='*')
    while True:
        count = check_pwned_password(password)
        if count == 154896:
            print("\n\033[91mПроверка не удалась, возможно отсутствует соеденение с интернетом.\nПовторить проверку?(y|ns).\033[0m")
            response2 = input("\033[91m>> \033[0m").lower()
            if response2 == 'y':
                print("\033[92mПовторная проверка.....\033[0m")
                continue
            elif response2 == 'exit':
                print("\033[92mЗавершение проверки...\033[0m")
                break
            else:
                print("\033[91mВведите только 'y' или 'exit'.\033[0m")
                continue
        elif count == 429001:
            print("\033[91mСлишком много запросов — лимит скорости превышен. Попробуйте позже.\033[0m")
            break
        elif count == 503001:
            print("\033[91mСервис временно недоступен.\033[0m")
            break
        elif count > 0:
            print(f"\033[91mЭтот пароль был утечен {count} раз(а).\033[0m")
            break
        else:
            print("\033[92mПароль не найден в известных утечках.\033[0m")
            break