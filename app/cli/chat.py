"""
Cli interface for handling chat functionality
"""
import colorama
from simple_term_menu import TerminalMenu
from typing import List
from .message import Message


fore_colors = [
    colorama.Fore.GREEN,
    colorama.Fore.YELLOW,
    colorama.Fore.BLUE,
    colorama.Fore.MAGENTA,
    colorama.Fore.CYAN,
]

back_colors = [colorama.Back.RED, colorama.Back.BLACK, colorama.Back.WHITE]


def pretty_print(text: str):
    selected_fore = fore_colors[hash(text) % len(fore_colors)]
    selected_back = back_colors[hash(text) % len(back_colors)]
    print(selected_fore + selected_back + text)


def choose_contact(contacts_nicknames: List[str]):
    """return chosen contact option"""
    return TerminalMenu(contacts_nicknames).show()


def display_message(message: Message, pretty: bool = True):
    if message.body == "":
        pass
    elif pretty:
        print(
            f"{pretty_print(message.sender)}  "
            f"{message.time_stamp} - {message.body}"
        )
    else:
        print(f"{message.time_stamp} <{message.sender}> {message.body}")
