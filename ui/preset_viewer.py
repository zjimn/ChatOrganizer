import os
from tkinter import ttk, filedialog

import tkinter as tk
from ttkbootstrap import Style

from widget.custom_listbox import CustomListbox


class PresetViewer:
    def __init__(self, parent):
        self.win_width = 373
        self.win_height = 264
        self.main_window = tk.Toplevel(parent)
        self.main_window.title("预设管理")
        self.main_window.geometry(f"{self.win_width}x{self.win_height}")
        self.main_window.resizable(False, False)
        # self.main_window.attributes('-topmost', True)

        self.main_frame = ttk.Frame(self.main_window, borderwidth=0, relief=tk.RAISED)

        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(side = tk.TOP, fill=tk.X, padx=(0, 18), pady=(10, 10))

        self.listbox_frame = ttk.Frame(self.main_frame, borderwidth=0, relief=tk.RAISED)

        self.listbox_bottom_frame = ttk.Frame(self.listbox_frame, borderwidth=0, relief=tk.RAISED)
        self.dir_path_var = tk.StringVar()
        self.load_file_var = tk.StringVar()

        self.add_button = ttk.Button(self.button_frame, text="添加预设")
        self.listbox = CustomListbox(self.listbox_bottom_frame, exportselection=0, width=1, enable_drag = False)
        self.h_scrollbar_listbox = ttk.Scrollbar(self.listbox_bottom_frame, orient=tk.HORIZONTAL, command=self.listbox.xview)
        self.listbox.config(xscrollcommand=self.h_scrollbar_listbox.set)
        self.scrollbar_listbox = ttk.Scrollbar(self.listbox_bottom_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox.config(yscrollcommand=self.scrollbar_listbox.set)

        self.listbox_frame.pack(side='left', padx=0, pady=(0, 0), fill='both', expand=True)

        self.add_button.pack(side='left', padx=(0, 5), pady=(0, 0))

        self.scrollbar_listbox.pack(side='right', fill='y')
        self.h_scrollbar_listbox.pack(side='bottom', fill='x')
        self.listbox.pack(side='left', padx=(0, 5), pady=(0, 5), fill=tk.BOTH, expand=True)
        self.listbox_bottom_frame.pack(side='top', pady=0, fill='both', expand=True)
        self.main_frame.pack(side='left', padx=(5, 5), pady=(0, 0), fill=tk.BOTH, expand=True)
        self.main_window.withdraw()
        self.main_window.iconbitmap("res/icon/model_preset.ico")



if __name__ == "__main__":
    root = tk.Tk()
    root.title("Preset Viewer")
    root.geometry("300x200")
    style = Style(theme='flatly')

    preset_viewer = PresetViewer(root)
    root.mainloop()