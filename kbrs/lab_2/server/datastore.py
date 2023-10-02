import crypto.aes
from crypto.utils import get_session_key
from crypto.consts import AES_KEY_LENGTH
from crypto.rsa import encrypt as encrypt_rsa
from crypto.aes import encrypt as encrypt_aes

class DataStore:

    def __init__(self):
        self.__text_store__: dict[str, str] = {}
        self.__active_sessions__: dict[str, str] = {}
        self.__key_vault__: dict[str, str] = {"admin": "admin"}

    def validate_credentials(self, username: str, provided_password: str):
        return username in self.__key_vault__ and self.__key_vault__[username] == provided_password

    def start_session(self, user_id: str, rsa_pub_key: tuple[int, int]) -> str:
        if user_id not in self.__active_sessions__.keys():
            session_token = get_session_key(AES_KEY_LENGTH)
            self.__active_sessions__[user_id] = session_token
            encrypted_session_token = encrypt_rsa(rsa_pub_key, session_token)
            return encrypted_session_token
        raise ValueError("Only one active session per user")

    def end_session(self, session_token: str):
        if session_token in self.__active_sessions__:
            del self.__active_sessions__[session_token]
        else:
            raise ValueError("User has already closed the session")

    @staticmethod
    def __require_session__(func):
        def wrapper(self, *args, **kwargs):
            session_token = kwargs['session_token']
            if session_token in self.__active_sessions__.values():
                return func(self, *args, **kwargs)
            else:
                raise ValueError("Session wasn't started")

        return wrapper

    @__require_session__
    def get_all_files(self, session_token: str) -> list[str]:
        return list(self.__text_store__.keys())

    @__require_session__
    def get_file_content(self, session_token: str, file_name: str) -> str:
        if file_name not in self.__text_store__:
            raise FileNotFoundError(f"No {file_name} file on server")
        text = self.__text_store__[file_name]
        text_bytes = bytes(text, 'UTF-8')
        encrypted_text = encrypt_aes(text_bytes, session_token)
        return encrypted_text

    @__require_session__
    def put_file(self, session_token: str, file_name: str, file_content: str):
        if file_name in self.__text_store__:
            raise ValueError(f"File {file_name} already exist, use edit_file function")
        self.__text_store__[file_name] = file_content

    @__require_session__
    def edit_file(self, session_token: str, file_name, new_file_content: str):
        if file_name not in self.__text_store__:
            raise ValueError(f"File {file_name} doesn't exist, use add_file function")

        self.__text_store__[file_name] = ''.join(crypto.aes.decrypt(new_file_content,session_token))

    @__require_session__
    def delete_file(self, session_token: str, file_name):
        if file_name not in self.__text_store__:
            raise ValueError(f"File {file_name} doesn't exist, nothing to delete")

        file_name_decrypted = ''.join(crypto.aes.decrypt(file_name, session_token))

        del self.__text_store__[file_name_decrypted]
