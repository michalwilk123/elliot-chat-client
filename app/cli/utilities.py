from app.config import MainMenuOptions
from simple_term_menu import TerminalMenu
from datetime import datetime
import aioconsole


def startup():
    print(
        """
    Hello to the ELLIOT!!
    """
    )


def get_credentials() -> str:
    print("Log in")
    login = input("login: ")
    return login


def get_menu_option() -> MainMenuOptions:
    opts = [
        "Send message",
        "Add user",
        "Update account",
        "Delete account",
        "Waitroom",
        "Exit",
    ]
    menu = TerminalMenu(opts)
    index_chosen = menu.show()
    return MainMenuOptions(index_chosen)


def get_timestamp() -> str:
    now = datetime.now()
    return now.strftime("%H:%M:%S")


async def get_contact_name():
    return await aioconsole.ainput("Contact Name:")
