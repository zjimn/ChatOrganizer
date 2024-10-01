import tkinter as tk
from db.database import init_db
from db.init_data import insert_default_content_hierarchy
from event.input_manager import InputManager
from event.list_manager import ListManager
from event.main_manager import MainManager
from event.output_manager import OutputManager
from event.tree_manager import TreeManager
from ui.main_window import MainWindow
from util.window_util import center_window


def main():
    init_db()
    insert_default_content_hierarchy()
    root = tk.Tk()
    root.title("openai chat")
    root.geometry("800x620")
    center_window(root, 800, 620)
    main_window = MainWindow(root)
    MainManager(main_window)
    ListManager(main_window)
    TreeManager(main_window)
    InputManager(main_window)
    OutputManager(main_window)
    root.mainloop()


if __name__ == "__main__":
    main()
