from typing import List
from app.user_state import UserState

class DatabaseController:
    # TODO: IMPLEMENT THIS CLASS!!!
    def __init__(self, user_state:UserState):
        self.user_state = user_state

    def update_user_id(self):
        self.user_state.user_id = 'dsajkndsadnaksnk'

    def get_user_contacts(self) -> List[str]:
        return [
            "Adam",
            "John",
            "Mark"
        ]