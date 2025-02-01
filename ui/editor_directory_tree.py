import tkinter as tk
from tkinter import ttk
from PIL import ImageTk
from config import constant
from util import image_util
from ttkbootstrap import Style


class EditorDirectoryTree:
    def __init__(self, parent):
        self.style = Style(theme="flatly")
        self.style.configure('Editor.Tree.Treeview',
                             rowheight=25, font=("微软雅黑", 10),
                             padding=(5, 10, 5, 10),
                             fieldbackground='white',
                             background='white',
                             foreground='#0d0d0d',
                             bordercolor='#cccccc',
                             borderwidth=10,
                             highlightthickness=1,
                             bd=1,
                             )
        self.tree = ttk.Treeview(parent, show="tree", style='Editor.Tree.Treeview', height=5)
        self.tree.column("#0", width=100, stretch=True)
        self.tree.pack(fill=tk.BOTH, expand=True)
        closed_folder_resized = image_util.resize_image_by_path(constant.CLOSED_FOLDER_IMAGE, (20, 20))
        self.closed_folder_resized_icon = ImageTk.PhotoImage(closed_folder_resized)
        open_folder_resized = image_util.resize_image_by_path(constant.OPEN_FOLDER_IMAGE, (20, 20))
        self.open_folder_resized_icon = ImageTk.PhotoImage(open_folder_resized)
