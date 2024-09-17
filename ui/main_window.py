# main_window.py
import tkinter as tk
from tkinter import ttk

from config import constant
from config.enum import ViewType
from ui.input_frame import InputFrame
from ui.directory_tree import DirectoryTree
from ui.display_frame import DisplayFrame
from ui.output_window import OutputWindow
from db.config_data_access import ConfigDataAccess
from db.database import init_db

class MainWindow:
    def __init__(self, root):
        self.selected_type_option = None
        self.selected_size_option = None
        self.output_window = None
        self.display_frame = None
        self.input_frame = None
        self.directory_tree = None
        self.view_type = ViewType.TXT
        self.data_manager = None
        self.set_config_from_database()
        self.create_ui(root)

    def set_config_from_database(self):
        with ConfigDataAccess() as cda:
            self.selected_size_option = int(cda.get_config_value_by_key(constant.IMG_SIZE_OPTION_KEY_NAME, '0'))
            self.selected_type_option = int(cda.get_config_value_by_key(constant.TYPE_OPTION_KEY_NAME, '0'))

    def create_ui(self, root):
        # Initialize Frames

        self.input_frame = InputFrame(root)
        paned_window = tk.PanedWindow(root, orient=tk.HORIZONTAL, sashwidth=10)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=20, pady=(20, 5))

        # Initialize Frames

        self.directory_tree = DirectoryTree(paned_window)
        self.display_frame = DisplayFrame(paned_window)
        self.output_window = OutputWindow(root)


        paned_window.add(self.directory_tree.left_frame, stretch="always")
        paned_window.add(self.display_frame.right_frame, stretch="always")


if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    root.title("GPT Completion Tool")
    root.geometry("800x600")

    config_data_access = ConfigDataAccess()

    root.mainloop()
