# input_frame.py
import tkinter as tk
from tkinter import ttk


class InputFrame:
    def __init__(self, parent):
        self.parent = parent
        self.style = ttk.Style()
        self.style.configure("Custom.TEntry", padding=(3, 5))
        self.size_options = ["1024x1024", "1792x1024", "1024x1792"]
        self.submit_button_initial_text = "获取回答"
        self.submit_button_changed_text = "⬛"

        self.submit_button_is_changed = False
        self.bottom_frame = tk.Frame(self.parent)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=(5, 20))

        self.input_text = tk.Text(self.bottom_frame, width=10, height=1, padx=5, pady=5)
        self.input_text.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.input_text.config(font=("Microsoft YaHei", 10))

        self.submit_button = ttk.Button(self.bottom_frame, text="获取回答", state=tk.DISABLED)
        self.submit_button.pack(side=tk.RIGHT, padx=(10, 0), anchor=tk.S)

        self.option_var = tk.StringVar(value="文字")
        self.option_menu = ttk.OptionMenu(self.bottom_frame, self.option_var, "文字", "文字", "图片")
        self.option_menu.pack(side=tk.RIGHT, padx=5, anchor=tk.S)

        self.size_var = tk.StringVar(value="1024x1024")
        self.size_menu = ttk.OptionMenu(self.bottom_frame, self.size_var, "1024x1024", "1024x1024", "1792x1024",
                                        "1024x1792")
        self.size_menu.pack(side=tk.RIGHT, padx=5, anchor=tk.S)
        self.size_menu.pack_forget()  # Initially hidden
