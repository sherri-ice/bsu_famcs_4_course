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


if __name__ == '__main__':
    app = ApplicationState(all_files_list=[], session_token='')
    pub, priv = crypto.rsa.generate_keypair(73, 103)
    client_keys = RsaKeys(public=pub, private=priv)
    server_public_key: tuple[int, int]


    def update_file_list():
        req = requests.get('http://127.0.0.1:5000/api/get_all_files',
                           json={'session_token': crypto.rsa.encrypt(server_public_key, app.session_token)})
        app.all_files_list = req.json()["all_files_names"]
        file_listbox.delete(0, tk.END)
        for name in app.all_files_list:
            file_listbox.insert(0, name)


    def save_file():
        if file_listbox.curselection():
            selected_index = file_listbox.curselection()[0]
            file_name = app.all_files_list[selected_index]
            file_content = text.get("1.0", tk.END)
            text_bytes = bytes(file_content, 'UTF-8')
            encrypted_text = crypto.aes.encrypt(text_bytes, app.session_token)
            payload = {'session_token': crypto.rsa.encrypt(server_public_key, app.session_token),
                       'file_name': file_name,
                       'file_content': encrypted_text}
            requests.post('http://127.0.0.1:5000/api/edit_file', json=payload)


    def new_file():
        file_name = input_field.get()
        if file_name == '':
            print("Empty name!")
            return
        payload = {'session_token': crypto.rsa.encrypt(server_public_key, app.session_token), 'file_name': file_name}
        res = requests.post('http://127.0.0.1:5000/api/new_file', json=payload)
        if res:
            update_file_list()


    def delete_file():
        if file_listbox.curselection():
            selected_index = file_listbox.curselection()[0]
            file_name = app.all_files_list[selected_index]
            text_bytes = bytes(file_name, 'UTF-8')
            encrypted_text = crypto.aes.encrypt(text_bytes, app.session_token)
            payload = {'session_token': crypto.rsa.encrypt(server_public_key, app.session_token),
                       'file_name': encrypted_text}
            requests.post('http://127.0.0.1:5000/api/delete', json=payload)

    def get_file_contents(event):
        if file_listbox.curselection():
            selected_index = file_listbox.curselection()[0]
            file_name = app.all_files_list[selected_index]
            payload = {'session_token': crypto.rsa.encrypt(server_public_key, app.session_token),
                       'file_name': file_name}
            res = requests.get('http://127.0.0.1:5000/api/get_file_content', json=payload)
            if res:
                file_contents = crypto.aes.decrypt(res.json()["file_content"], app.session_token)
                text.delete('1.0', tk.END)
                text.insert(tk.END, ''.join(file_contents))
            else:
                return


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

    input_field = tk.Entry(button_frame)
    input_field.pack(side=tk.TOP, padx=5, pady=5)

    new_button = tk.Button(button_frame, text="Create new file", command=new_file)
    new_button.pack(side=tk.TOP, padx=5, pady=5)

    update_button = tk.Button(button_frame, text="Update file list", command=update_file_list)
    update_button.pack(side=tk.TOP, padx=5, pady=5)

    save_button = tk.Button(button_frame, text="Save file to server", command=save_file)
    save_button.pack(side=tk.TOP, padx=5, pady=5)

    delete_button = tk.Button(button_frame, text="Delete current file", command=delete_file)
    delete_button.pack(side=tk.TOP, padx=5, pady=5)

    # Binding file selection to update text
    file_listbox.bind('<<ListboxSelect>>', get_file_contents)

    res = requests.get('http://127.0.0.1:5000/api/get_public_key')
    if res:
        server_public_key = res.json()["server_public_key"]
    else:
        print(res.text)
        raise ConnectionError('Server not enabled')

    login_payload = {
        'username': crypto.rsa.encrypt(server_public_key, 'admin'),
        'password': crypto.rsa.encrypt(server_public_key, 'admin'),
        'public_key': client_keys.public,

    }

    res = requests.post('http://127.0.0.1:5000/api/login',
                        json=login_payload)
    if res:
        print("Connect successful!")
        app.session_token = crypto.rsa.decrypt(client_keys.private, res.json()["session_token"])
    else:
        print(res.text)
        raise ConnectionError('Server not enabled')

    # Start the main loop
    root.mainloop()
