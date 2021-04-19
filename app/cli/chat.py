"""
Cli interface for handling chat functionality
"""
from simple_term_menu import TerminalMenu
from typing import List


def choose_contact(contacts_nicknames:List[str]):
    """return chosen contact option"""
    return TerminalMenu(contacts_nicknames).show()