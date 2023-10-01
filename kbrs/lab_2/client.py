import tkinter as tk
from tkinter import filedialog
import requests
from dataclasses import dataclass


@dataclass
class ApplicationState:
    all_files_list: list[str]
    session_token: list[int]


if __name__ == '__main__':
    app = ApplicationState(all_files_list=[], session_token=[])


    def update_file_list():
        req = requests.get('http://127.0.0.1:5000/api/login', json={'session_token': app.session_token[0]})
        app.all_files_list = req.json()["all_files_names"]
        file_listbox.delete(0, tk.END)
        for name in app.all_files_list:
            file_listbox.insert(0, name)


    def save_file():
        filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if filepath:
            with open(filepath, 'w') as file:
                file.write(text.get('1.0', tk.END))


    def new_file():
        file_name = input_field.get()
        payload = {'session_token': app.session_token[0], 'file_name': file_name, 'file_content': ''}
        res = requests.post('http://127.0.0.1:5000/api/load_file', json=payload)
        if res:
            update_file_list()


    def delete_file():
        if file_listbox.curselection():
            selected_index = file_listbox.curselection()[0]
            file_listbox.delete(selected_index)
            text.delete('1.0', tk.END)


    def get_file_contents(event):
        if file_listbox.curselection():
            selected_index = file_listbox.curselection()[0]
            selected_file = file_listbox.get(selected_index)
            text.delete('1.0', tk.END)
            text.insert(tk.END, selected_file)


    # Create main window
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

    res = requests.post('http://127.0.0.1:5000/api/login',
                        json={'username': 'admin', 'password': 'admin', 'pub_key_e': '10000007',
                              'pub_key_p': '1000007'})
    if res:
        print("connect successful")
        app.session_token = res.json()["session_token"]
    else:
        print(res.text)
        raise ConnectionError('Server not enabled')

    # Start the main loop
    root.mainloop()
