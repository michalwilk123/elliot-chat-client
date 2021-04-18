from .user import CurrentUser, UserDataLoader
from .app_controller import AppController

# Create global user state (like in redux)
user_state = CurrentUser.CurrentUser()

# assign saved data
UserDataLoader.UserLoader.load_user_data(user_state)

controller = AppController(user_state)
controller.start()