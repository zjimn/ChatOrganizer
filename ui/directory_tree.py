import tkinter as tk
from tkinter import ttk
from PIL import ImageTk
from config import constant
from ui.syle.tree_view_style_manager import TreeViewStyleManager
from util import image_util


class DirectoryTree:
    def __init__(self, parent):
        self.parent = parent
        self.left_frame = tk.Frame(parent, width=100)
        self.tree = ttk.Treeview(self.left_frame, show='tree', style='Tree.Treeview')
        self.tree.column("#0", width=150)
        self.tree.pack(expand=True, fill="both")
        closed_folder_resized = image_util.resize_image_by_path(constant.CLOSED_FOLDER_IMAGE, (20, 20))
        self.closed_folder_resized_icon = ImageTk.PhotoImage(closed_folder_resized)
        open_folder_resized = image_util.resize_image_by_path(constant.OPEN_FOLDER_IMAGE, (20, 20))
        self.open_folder_resized_icon = ImageTk.PhotoImage(open_folder_resized)
        self.style_manager = TreeViewStyleManager(self.tree)
        self.style_manager.set_tree_style()