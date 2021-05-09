from app.chat.crypto.crypto_utils import generate_DH
from .user_state import UserState
from app.database.db_controller import DatabaseController


def resolve_user_state(user_state: UserState, db_path: str) -> bool:
    if not user_state_keys_present(user_state):
        return False

    db_controller = DatabaseController(DB_PATH=db_path)
    id_key, signed_pre_key = db_controller.get_user_keys(user_state)

    if id_key is None or signed_pre_key is None:
        user_state.id_key = generate_DH()
        user_state.signed_pre_key = generate_DH()
        db_controller.set_user_keys(user_state)
    else:
        user_state.id_key = id_key
        user_state.signed_pre_key = signed_pre_key

    return True


def user_state_keys_present(user_state: UserState) -> bool:
    return (
        user_state.id_key is not None and user_state.signed_pre_key is not None
    )
