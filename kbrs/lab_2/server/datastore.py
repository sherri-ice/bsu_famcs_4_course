class DataStore:

    def __init__(self):
        self.__text_store__: dict[str, str] = {}
        self.__active_sessions__: dict[str, str] = {}
        self.__key_vault__: dict[str, str] = {"admin": "admin"}

    def validate_credentials(self, username: str, provided_password: str):
        return username in self.__key_vault__ and self.__key_vault__[username] == provided_password

    def start_session(self, user_id: str) -> str:
        if user_id not in self.__active_sessions__.keys():
            session_token = str(user_id)
            self.__active_sessions__[session_token] = user_id
            return session_token
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
            if session_token in self.__active_sessions__:
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
        # todo: encrypt_file
        return self.__text_store__[file_name]

    @__require_session__
    def put_file(self, session_token: str, file_name: str, file_content: str):
        if file_name in self.__text_store__:
            raise ValueError(f"File {file_name} already exist, use edit_file function")
        self.__text_store__[file_name] = file_content

    @__require_session__
    def edit_file(self, session_token: str, file_name, new_file_content: str):
        if file_name not in self.__text_store__:
            raise ValueError(f"File {file_name} doesn't exist, use add_file function")
        self.__text_store__[file_name] = new_file_content

    @__require_session__
    def delete_file(self, session_token: str, file_name):
        if file_name not in self.__text_store__:
            raise ValueError(f"File {file_name} doesn't exist, nothing to delete")
        del self.__text_store__[file_name]
