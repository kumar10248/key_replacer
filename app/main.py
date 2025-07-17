import tkinter as tk
from tkinter import messagebox
import keyboard
import threading
import time
import os
import json
import platform
import pyautogui

replacements = {}
MAPPING_FILE = "mappings.json"

def load_mappings():
    if os.path.exists(MAPPING_FILE):
        with open(MAPPING_FILE, "r") as f:
            try:
                replacements.update(json.load(f))
            except json.JSONDecodeError:
                pass

def save_mappings():
    with open(MAPPING_FILE, "w") as f:
        json.dump(replacements, f)

def type_text(text):
    system = platform.system()
    if system == "Linux":
        os.system(f'xdotool type --delay 1 "{text}"')
    else:
        pyautogui.write(text, interval=0.01)

def add_pair():
    key = key_entry.get().strip().lower()
    value = value_entry.get().strip()
    if key and value:
        replacements[key] = value
        save_mappings()
        messagebox.showinfo("Success", f"Added {key} → {value}")
        key_entry.delete(0, tk.END)
        value_entry.delete(0, tk.END)
    else:
        messagebox.showerror("Error", "Both key and value are required!")

def listen_keys():
    typed = ""
    suppress = False
    while True:
        try:
            event = keyboard.read_event()
            if event.event_type != keyboard.KEY_DOWN or suppress:
                continue

            key = event.name.lower()

            if key in ("space", "enter"):
                match = typed.lower()
                if match in replacements:
                    suppress = True
                    for _ in range(len(typed) + 1):
                        keyboard.press_and_release("backspace")
                    time.sleep(0.1)
                    type_text(replacements[match])
                    if key == "space":
                        keyboard.press_and_release("space")
                    elif key == "enter":
                        keyboard.press_and_release("enter")
                    time.sleep(0.2)
                    typed = ""
                    suppress = False
                else:
                    typed = ""
            elif key == "backspace":
                typed = typed[:-1]
            elif len(key) == 1 or key.isalnum():
                typed += key
            else:
                typed = ""
        except Exception as e:
            print("[Error]", e)

# GUI Setup
root = tk.Tk()
root.title("Key Replacer")

tk.Label(root, text="Key (e.g. e1):").grid(row=0, column=0, padx=10, pady=5)
key_entry = tk.Entry(root)
key_entry.grid(row=0, column=1)

tk.Label(root, text="Value (e.g. Kumar Devashish):").grid(row=1, column=0, padx=10, pady=5)
value_entry = tk.Entry(root)
value_entry.grid(row=1, column=1)

tk.Button(root, text="Add Mapping", command=add_pair).grid(row=2, column=0, columnspan=2, pady=10)

load_mappings()
threading.Thread(target=listen_keys, daemon=True).start()
root.mainloop()
