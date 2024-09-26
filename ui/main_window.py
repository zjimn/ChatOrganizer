import tkinter as tk
from config.enum import ViewType
from db.config_data_access import ConfigDataAccess
from ui.directory_tree import DirectoryTree
from ui.display_frame import DisplayFrame
from ui.input_frame import InputFrame
from ui.output_window import OutputWindow


class MainWindow:
    def __init__(self, root):
        self.paned_window = None
        self.root = root
        self.selected_type_option = None
        self.selected_size_option = None
        self.output_window = None
        self.display_frame = None
        self.input_frame = None
        self.directory_tree = None
        self.view_type = ViewType.TXT
        self.data_manager = None
        self.create_ui(root)

    def create_ui(self, root):
        self.input_frame = InputFrame(root)
        self.paned_window = tk.PanedWindow(root, orient=tk.HORIZONTAL, sashwidth=10)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=20, pady=(20, 5))
        self.directory_tree = DirectoryTree(self.paned_window)
        self.display_frame = DisplayFrame(self.paned_window)
        self.output_window = OutputWindow(root)
        self.paned_window.add(self.directory_tree.left_frame, stretch="always")
        self.paned_window.add(self.display_frame.right_frame, stretch="always")
        self.paned_window.update_idletasks()
        self.paned_window.sash_place(0, 150, 0)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("GPT Completion Tool")
    root.geometry("800x600")
    config_data_access = ConfigDataAccess()
    root.mainloop()
