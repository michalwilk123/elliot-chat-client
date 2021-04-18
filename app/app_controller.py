from .user.current_user import CurrentUserData
from .cli import utilities
from .config import MainMenuOptions
from .chat.chat_manager import ChatManager
from .database.db_controller import 

class AppController:
    def __init__(self, state:CurrentUserData):
        self.__user_data = state
        utilities.startup()
        self.login, self.password = utilities.get_credentials()

    
    @staticmethod
    def choose_reciever():
        pass


    def start(self):
        while True:
            option = utilities.get_menu_option()

            if option == MainMenuOptions.MESSAGE:
                self.reciever = AppController.choose_reciever()
                chat_manager = ChatManager()
                chat_manager.start()
                # we get rid of the client immediately!!
                del chat_manager
            elif option == MainMenuOptions.ADD_FRIEND:
                pass
            elif option == MainMenuOptions.CHANGE_CREDENTIALS:
                pass
            elif option == MainMenuOptions.REMOVE_ACCOUNT:
                pass
            elif option == MainMenuOptions.EXIT:
                pass
            else:
                raise RuntimeError("This option currently is not implemented")
