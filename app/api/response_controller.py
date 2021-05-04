


from typing import Tuple
from app.user_state import UserState


class ResponseController:
    """
    Class responsible for linking database, 
    user_state and our server

    Most important method there is 
    *server_task*. 
    Rest of the messages are utilities
    """
    def __init__(self, user_state:UserState, url:str) -> None:
        self.user_state = user_state
        self.url = url

    async def server_task(self):
        ...

    def add_new_contact(self):
        ...

    def init_conversation(self):
        ...

    
    def register_user(self):
        ...

    def login_user(self):
        ...

    def get_nessesary_params(self) -> Tuple[str, UserState]:
        return self.url, self.user_state