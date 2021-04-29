from .user_state import UserState
from .cli import utilities, chat
from .config import MainMenuOptions
from .database.db_controller import DatabaseController
from .chat.chat_controller import ChatController


class AppController:
    __slots__ = "__user_state", "__db_controller", "__chat_controller"

    def __init__(self):
        utilities.startup()
        # login, password = utilities.get_credentials()
        login, password = "admin", "passw"

        self.__user_state = UserState(login, password)
        self.__db_controller = DatabaseController()


    def choose_reciever(self) -> str:
        """choosing contact to have chat with
        Returns:
            str: chosen contact login
        """
        contacts = self.__db_controller.get_user_contacts(self.__user_state)
        return contacts[chat.choose_contact(contacts)]

    def start(self):
        while True:
            # option = utilities.get_menu_option()
            option = MainMenuOptions.MESSAGE

            if option == MainMenuOptions.MESSAGE:
                # reciever = self.choose_reciever()
                reciever = "Mark"
                self.__chat_controller = ChatController(
                    self.__user_state,
                    reciever,
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
