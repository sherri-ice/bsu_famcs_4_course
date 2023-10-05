import tkinter as tk
from dataclasses import dataclass

import requests

import crypto.aes
import crypto.rsa
from crypto.utils import RsaKeys


@dataclass
class ApplicationState:
    all_files_list: list[str]
    session_token: str  # stores non encrypted session token for aes
    __pub__, __private__ = crypto.rsa.generate_keypair(73, 103)
    client_keys = RsaKeys(public=__pub__, private=__private__)
    server_public_key: tuple[int, int]


if __name__ == '__main__':
    app = ApplicationState(all_files_list=[], session_token='', server_public_key=(0,0))

    def login():
        try:
            res = requests.get('http://127.0.0.1:5000/api/get_public_key')
            app.server_public_key = res.json()["server_public_key"]
            login_payload = {
                'username': crypto.rsa.encrypt(app.server_public_key, input_login_field.get()),
                'password': crypto.rsa.encrypt(app.server_public_key, input_password_field.get()),
                'public_key': app.client_keys.public,
            }
            res = requests.post('http://127.0.0.1:5000/api/login',
                                json=login_payload)
            app.session_token = crypto.rsa.decrypt(app.client_keys.private, res.json()["session_token"])
            update_file_list()
        except Exception as ex:
            input_error_label['text'] = "Error occurred on login"
            input_error_label['fg'] = 'red'
        input_error_label['text'] = "Login"
        input_error_label['fg'] = 'green'


    def update_file_list():
        try:
            req = requests.get('http://127.0.0.1:5000/api/get_all_files',
                               json={'session_token': crypto.rsa.encrypt(app.server_public_key, app.session_token)})
            app.all_files_list = req.json()["all_files_names"]
            file_listbox.delete(0, tk.END)
            for name in app.all_files_list:
                file_listbox.insert(tk.END, name)
        except Exception as ex:
            input_error_label['text'] = "Error occurred on updating"
            input_error_label['fg'] = 'red'
        input_error_label['text'] = "Update"
        input_error_label['fg'] = 'green'

    def save_file():
        if file_listbox.curselection():
            try:
                selected_index = file_listbox.curselection()[0]
                file_name = app.all_files_list[selected_index]
                file_content = text.get("1.0", tk.END)
                text_bytes = bytearray(file_content, 'UTF-8')
                encrypted_text = crypto.aes.encrypt(text_bytes, app.session_token)
                payload = {'session_token': crypto.rsa.encrypt(app.server_public_key, app.session_token),
                           'file_name': file_name,
                           'file_content': encrypted_text}
                requests.post('http://127.0.0.1:5000/api/edit_file', json=payload)
            except Exception as ex:
                input_error_label['text'] = "Error occurred on saving"
                input_error_label['fg'] = 'red'
            input_error_label['text'] = "Saved"
            input_error_label['fg'] = 'green'
        else:
            input_error_label['text'] = "Error: no file selected"
            input_error_label['fg'] = 'red'


    def new_file():
        try:
            file_name = input_filename_field.get()
            payload = {'session_token': crypto.rsa.encrypt(app.server_public_key, app.session_token), 'file_name': file_name}
            res = requests.post('http://127.0.0.1:5000/api/new_file', json=payload)
            if res:
                input_error_label['text'] = "Created"
                input_error_label['fg'] = 'green'
                update_file_list()
            else:
                input_error_label['text'] = "Error no filename"
                input_error_label['fg'] = 'red'
        except Exception as ex:
            input_error_label['text'] = "Error occurred on creating"
            input_error_label['fg'] = 'red'


    def delete_file():
        try:
            if file_listbox.curselection():
                selected_index = file_listbox.curselection()[0]
                file_name = app.all_files_list[selected_index]
                text_bytes = bytearray(file_name, 'UTF-8')
                encrypted_text = crypto.aes.encrypt(text_bytes, app.session_token)
                payload = {'session_token': crypto.rsa.encrypt(app.server_public_key, app.session_token),
                           'file_name': encrypted_text}
                requests.delete('http://127.0.0.1:5000/api/delete_file', json=payload)
                update_file_list()
        except Exception as ex:
            input_error_label['text'] = "Error occurred on deleting"
            input_error_label['fg'] = 'red'

    def get_file_contents(event):
        try:
            if file_listbox.curselection():
                selected_index = file_listbox.curselection()[0]
                file_name = app.all_files_list[selected_index]
                payload = {'session_token': crypto.rsa.encrypt(app.server_public_key, app.session_token),
                           'file_name': file_name}
                res = requests.get('http://127.0.0.1:5000/api/get_file_content', json=payload)
                if res:
                    file_contents = crypto.aes.decrypt(res.json()["file_content"], app.session_token)
                    text.delete('1.0', tk.END)
                    text.insert(tk.END, file_contents)
                else:
                    return
        except Exception as ex:
            input_error_label['text'] = "Error occurred on get file"
            input_error_label['fg'] = 'red'
        input_error_label['text'] = "Updated contents"
        input_error_label['fg'] = 'green'


    root = tk.Tk()
    root.title("File Manager")

    # Left frame for file list
    left_frame = tk.Frame(root, width=200, height=400, bg='lightgray')
    left_frame.pack(side=tk.LEFT, fill=tk.Y)

    file_listbox = tk.Listbox(left_frame, selectbackground='lightblue')
    file_listbox.pack(expand=tk.YES, fill=tk.BOTH)

    # Center frame for opened file
    center_frame = tk.Frame(root, width=400, height=400)
    center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    text = tk.Text(center_frame, wrap=tk.WORD)
    text.pack(expand=tk.YES, fill=tk.BOTH)

    # Buttons
    button_frame = tk.Frame(root, height=50)
    button_frame.pack(side=tk.LEFT, fill=tk.X)

    input_login_label = tk.Label(button_frame, text="Login")
    input_login_label.pack(side=tk.TOP)
    input_login_field = tk.Entry(button_frame)
    input_login_field.pack(side=tk.TOP)

    input_password_label = tk.Label(button_frame, text="Password")
    input_password_label.pack(side=tk.TOP)
    input_password_field = tk.Entry(button_frame)
    input_password_field.pack(side=tk.TOP)

    new_button = tk.Button(button_frame, text="Login", command=login)
    new_button.pack(side=tk.TOP, padx=5, pady=5)

    input_error_label = tk.Label(button_frame, text="")
    input_error_label.pack(side=tk.TOP, padx=5, pady=5)

    input_filename_label = tk.Label(button_frame, text="Enter filename to add here")
    input_filename_label.pack(side=tk.TOP)
    input_filename_field = tk.Entry(button_frame)
    input_filename_field.pack(side=tk.TOP, padx=5, pady=5)

    new_button = tk.Button(button_frame, text="Create new file", command=new_file)
    new_button.pack(side=tk.TOP, padx=5, pady=5)

    save_button = tk.Button(button_frame, text="Save file to server", command=save_file)
    save_button.pack(side=tk.TOP, padx=5, pady=5)

    delete_button = tk.Button(button_frame, text="Delete current file", command=delete_file)
    delete_button.pack(side=tk.TOP, padx=5, pady=5)

    update_button = tk.Button(button_frame, text="Update file list", command=update_file_list)
    update_button.pack(side=tk.TOP, padx=5, pady=5)

    # Binding file selection to update text
    file_listbox.bind('<<ListboxSelect>>', get_file_contents)

    # Start the main loop
    root.mainloop()

    end_session_payload = {"session_token": crypto.rsa.encrypt(app.server_public_key, app.session_token),
                           "username": "admin"}

    requests.post('http://127.0.0.1:5000/api/end_session', json=end_session_payload)
