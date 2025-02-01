import tkinter as tk
from tkinter import ttk

from ttkbootstrap import Style

from config.enum import ViewType
from ui.advanced_log_window import AdvancedLogWindow
from ui.directory_tree import DirectoryTree
from ui.display_frame import DisplayFrame
from ui.input_frame import InputFrame
from ui.output_window import OutputWindow
from ui.setting_window import SettingsWindow
from ui.top_bar import TopBar


class MainWindow:
    def __init__(self, root):
        self.settings_window = None
        self.advanced_log_window = None
        self.top_bar = None
        self._paned_window = None
        self.root = root
        self.output_window = None
        self.display_frame = None
        self.input_frame = None
        self.directory_tree = None
        self.create_ui(root)
        self.style = Style(theme="flatly")
    def create_ui(self, root):
        self.top_bar = TopBar(root)
        self.settings_window = SettingsWindow(root)
        self.advanced_log_window = AdvancedLogWindow(root)
        self.input_frame = InputFrame(root)
        self._paned_window = tk.PanedWindow(root, orient=tk.HORIZONTAL, sashwidth=10)
        self._paned_window.pack(fill=tk.BOTH, expand=True, padx=20, pady=(5, 5))
        self.directory_tree = DirectoryTree(self._paned_window)
        self.display_frame = DisplayFrame(self._paned_window)
        self.output_window = OutputWindow(root)
        self._paned_window.add(self.directory_tree.left_frame)
        self._paned_window.add(self.display_frame.right_frame)
        self._paned_window.update_idletasks()
        #self._paned_window.sash_place(0, 150, 0)
