import tkinter as tk
from tkinter import ttk

from config.enum import ViewType
from ui.directory_tree import DirectoryTree
from ui.display_frame import DisplayFrame
from ui.input_frame import InputFrame
from ui.output_window import OutputWindow


class MainWindow:
    def __init__(self, root):
        self._paned_window = None
        self.root = root
        self.output_window = None
        self.display_frame = None
        self.input_frame = None
        self.directory_tree = None
        self.create_ui(root)

    def create_ui(self, root):
        self.input_frame = InputFrame(root)
        self._paned_window = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        self._paned_window.pack(fill=tk.BOTH, expand=True, padx=20, pady=(20, 5))
        self.directory_tree = DirectoryTree(self._paned_window)
        self.display_frame = DisplayFrame(self._paned_window)
        self.output_window = OutputWindow(root)
        self._paned_window.add(self.directory_tree.left_frame, weight=1)
        self._paned_window.add(self.display_frame.right_frame, weight=6)
        self._paned_window.update_idletasks()
        #self._paned_window.sash_place(0, 150, 0)
