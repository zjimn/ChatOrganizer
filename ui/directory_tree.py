# directory_tree.py
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk
from config import constant
from util import image_utils

class DirectoryTree:
    def __init__(self, parent):
        self.parent = parent
        self.left_frame = tk.Frame(parent)
        self.left_frame.grid(row=0, column=0, sticky="nswe", padx=(0, 10))

        self.tree = ttk.Treeview(self.left_frame, show='tree', style='Tree.Treeview')
        self.tree.pack(expand=True, fill="both")

        closed_folder_resized = image_utils.resize_image_by_path(constant.CLOSED_FOLDER_IMAGE, (20, 20))
        self.closed_folder_resized_icon = ImageTk.PhotoImage(closed_folder_resized)

        open_folder_resized = image_utils.resize_image_by_path(constant.OPEN_FOLDER_IMAGE, (20, 20))
        self.open_folder_resized_icon = ImageTk.PhotoImage(open_folder_resized)

        self.insert_sample_data()

    def insert_sample_data(self):
        # Sample data to populate the tree ui
        root_node = self.tree.insert("", "end", text="Root", open=True, image=self.closed_folder_resized_icon)

        # Example directories and files
        folder1 = self.tree.insert(root_node, "end", text="Folder 1", open=False,
                                   image=self.closed_folder_resized_icon)
        self.tree.insert(folder1, "end", text="File 1-1.txt")
        self.tree.insert(folder1, "end", text="File 1-2.txt")

        folder2 = self.tree.insert(root_node, "end", text="Folder 2", open=False,
                                   image=self.closed_folder_resized_icon)
        self.tree.insert(folder2, "end", text="File 2-1.txt")

        folder3 = self.tree.insert(root_node, "end", text="Folder 3", open=False,
                                   image=self.closed_folder_resized_icon)
        self.tree.insert(folder3, "end", text="File 3-1.txt")
        self.tree.insert(folder3, "end", text="File 3-2.txt")

    def on_folder_open(self, event):
        item = self.tree.selection()[0]
        self.tree.item(item, image=self.open_folder_resized_icon)

    def on_folder_close(self, event):
        item = self.tree.selection()[0]
        self.tree.item(item, image=self.closed_folder_resized_icon)

    def clear_data(self):
        # Method to clear all items in the tree ui
        for item in self.tree.get_children():
            self.tree.delete(item)