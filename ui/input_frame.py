import tkinter as tk
from tkinter import ttk

from widget.undo_redo_text import UndoRedoText


class InputFrame:
    def __init__(self, parent):
        self.parent = parent
        self.size_options = ["1024x1024", "1792x1024", "1024x1792"]
        self.type_options = ["文字", "图片"]
        self.submit_button_initial_text = "获取回答"
        self.submit_button_changed_text = "⬛"
        self.submit_button_is_changed = False
        self.frame = ttk.Frame(self.parent)
        self.frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=(5, 20))
        self.input_text = UndoRedoText(self.frame, wrap='word', width=10, height=1, padx=5, pady=5)
        self.input_text.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.input_text.config(font=("Microsoft YaHei", 10))
        self.submit_button = ttk.Button(self.frame, text="获取回答", state=tk.DISABLED)
        self.submit_button.pack(side=tk.RIGHT, padx=(10, 0), anchor=tk.S)
        self.option_var = tk.StringVar(value="文字")
        self.option_menu = ttk.OptionMenu(self.frame, self.option_var, "文字", *self.type_options)
        self.option_menu.pack(side=tk.RIGHT, padx=5, anchor=tk.S)
        self.size_var = tk.StringVar(value="1024x1024")
        self.size_menu = ttk.OptionMenu(self.frame, self.size_var, "1024x1024", *self.size_options)
        self.size_menu.pack(side=tk.RIGHT, padx=5, anchor=tk.S)
        self.new_chat_button = ttk.Button(self.frame, text="新的对话", state=tk.NORMAL)
        self.new_chat_button.pack(side=tk.RIGHT, padx=(0, 10), anchor=tk.S)
        self.size_menu.pack_forget()

