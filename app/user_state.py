import secrets

class UserState:
    """
    Current informations about the app state. 
    This functionality is based on redux state class
    """
    def __init__(self, login:str, password:str):
        self._login = login
        self._password = password

    @property
    def login(self): return self._login

    @property
    def password(self): return self._password

    @property
    def user_id(self): return self._user_id

    @user_id.setter
    def user_id(self, uid:str):
        # this should be called ONLY ONCE!
        assert hasattr(self, '_user_id') == False
        self._user_id = uid
