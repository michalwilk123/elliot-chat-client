from app.chat.crypto.establisher import Establisher
from .user_state import UserState
from .cli import utilities, chat
from .config import MainMenuOptions
from .database.db_controller import DatabaseController
from .chat.chat_controller import ChatController


class AppController:
    __slots__ = "__user_state", "__db_controller", "__chat_controller"

    def __init__(self):
        utilities.startup()
        login, password = utilities.get_credentials()

        self.user_state = UserState(login, password)
        self.db_controller = DatabaseController()
        self.establisher = Establisher(self.user_state, load_from_db=True)

    def choose_reciever(self) -> str:
        """choosing contact to have chat with
        Returns:
            str: chosen contact login
        """
        contacts = self.db_controller.get_user_contacts(self.user_state)
        return contacts[chat.choose_contact(contacts)]

    def start(self):
        while True:
            # option = utilities.get_menu_option()
            option = MainMenuOptions.MESSAGE

            if option == MainMenuOptions.MESSAGE:
                reciever = self.choose_reciever()
                self.__chat_controller = ChatController(
                    self.user_state, reciever, self.establisher
                )

                self.__chat_controller.start()
                del self.__chat_controller
            elif option == MainMenuOptions.ADD_FRIEND:
                pass
            elif option == MainMenuOptions.CHANGE_CREDENTIALS:
                pass
            elif option == MainMenuOptions.REMOVE_ACCOUNT:
                pass
            elif option == MainMenuOptions.EXIT:
                print("bye")
                break
            else:
                raise RuntimeError("This option currently is not implemented")
        print("cleanup")
