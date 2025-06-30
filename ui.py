from art import text2art
from colorama import init, Fore, Style

init()

def show_logo():
    logo = text2art("knox")
    print(Fore.RED + logo)
    print(Fore.RED + Style.BRIGHT + "Ваш надежный менеджер паролей.          Tg: @goja56.")
    print(Style.RESET_ALL)