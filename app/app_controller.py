from app.api.response_controller import ResponseController
from app.chat.crypto.establisher import Establisher
from .user_state import UserState
from .cli import utilities, chat
from .config import MainMenuOptions, SERVER_URL
from .database.db_controller import DatabaseController
from .chat.chat_controller import ChatController
from app.api.api_util_operations import get_pending_responses


class AppController:
    __slots__ = "__user_state", "__db_controller", "__chat_controller"

    def __init__(self):
        self.resolve_startup()
        self.db_controller = DatabaseController()
        utilities.startup()
        login, password = utilities.get_credentials()

        self.user_state = UserState(login, password)
        self.response_controller = ResponseController(self.user_state, SERVER_URL)
        self.establisher = Establisher(self.user_state, self.response_controller, load_from_db=True)

    def choose_reciever(self) -> str:
        """choosing contact to have chat with
        Returns:
            str: chosen contact login
        """
        contacts = self.db_controller.get_user_contacts(self.user_state)
        return contacts[chat.choose_contact(contacts)]

    def resolve_startup(self):
        ...

    def add_new_user_contact(self):
        ...

    def get_blocking_server_message(self):
        ...

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
            elif option == MainMenuOptions.WAITROOM:
                pass
            elif option == MainMenuOptions.EXIT:
                print("bye")
                break
            else:
                raise RuntimeError("This option currently is not implemented")
        print("cleanup")
