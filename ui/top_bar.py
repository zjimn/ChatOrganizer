import tkinter as tk
from tkinter import ttk


class TopBar:
    def __init__(self, parent):
        self.parent = parent
        self.preset_options = []
        self.preset_var = tk.StringVar(value="")
        self.main_frame = ttk.Frame(self.parent)

        self.preset_combobox = ttk.Combobox(self.main_frame, textvariable = self.preset_var, values=self.preset_options,state="readonly")
        self.preset_combobox.pack(side = tk.LEFT, fill=tk.X, padx=0, pady=0)
        self.preset_manager_button = ttk.Button(self.main_frame, text="预设管理", state=tk.NORMAL)
        self.preset_manager_button.pack(side=tk.LEFT, padx=(10, 0), anchor=tk.S)


        self.model_options = []
        self.model_var = tk.StringVar(value="")

        self.model_combobox = ttk.Combobox(self.main_frame, textvariable = self.model_var, values=self.model_options,state="readonly")


        self.setting_button = ttk.Button(self.main_frame, text="设置", state=tk.NORMAL)
        self.setting_button.pack(side=tk.RIGHT, padx=(20, 0), anchor=tk.S)

        self.model_manager_button = ttk.Button(self.main_frame, text="模型管理", state=tk.NORMAL)
        self.model_manager_button.pack(side=tk.RIGHT, padx=(10, 0), anchor=tk.S)
        self.model_combobox.pack(side = tk.RIGHT, fill=tk.X, padx=(20, 0), pady=0)
        self.main_frame.pack(side=tk.TOP, fill=tk.X, padx=20, pady=(5, 0))
