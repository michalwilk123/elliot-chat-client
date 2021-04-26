"""
Handling user input, ALL FUNCTIONS DO NOT CHANGE STATE!!!
"""
from getpass import getpass
from app.config import MainMenuOptions
from simple_term_menu import TerminalMenu
from typing import Tuple


def startup():
    print(
        """
    Hello to the ELLIOT!!
    """
    )


def get_credentials() -> Tuple[str, str]:
    print("Log in")
    login = input("login: ")
    password = getpass("password: ")
    return login, password


def get_menu_option() -> MainMenuOptions:
    opts = [
        "Send message",
        "Add user",
        "Update account",
        "Delete account",
        "Exit",
    ]
    menu = TerminalMenu(opts)
    index_chosen = menu.show()
    return MainMenuOptions(index_chosen)
