import tkinter as tk

from config.app_config import AppConfig
from event.output_manager import OutputManager
from event.input_manager import InputManager
from event.tree_manager import TreeManager
from db.database import init_db
from event.main_manager import MainManager
from event.list_editor import ListEditor

from ui.main_window import MainWindow
from event.list_manager import ListManager  # Import the class

def main():
    init_db()
    system_config = AppConfig()
    root = tk.Tk()
    root.title("GPT Completion Tool")
    root.geometry("800x620")

    main_window = MainWindow(root)

    # 绑定事件
    main_manager = MainManager(root, main_window)
    main_manager.bind_events()
    ListManager(root, main_window)
    TreeManager(root, main_window.directory_tree.tree, main_window)
    ListEditor(root, main_window)


    InputManager(root, main_window)
    OutputManager(root, main_window)

    root.mainloop()

if __name__ == "__main__":
    main()
