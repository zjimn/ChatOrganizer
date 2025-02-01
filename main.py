import tkinter as tk

from db.data_initializer import DataInitializer
from db.database import init_db
from db.init_folder import init_folder
from event.advanced_log_window_manager import AdvancedLogWindowManager
from event.input_manager import InputManager
from event.list_manager import ListManager
from event.main_manager import MainManager
from event.output_manager import OutputManager
from event.setting_window_manager import SettingWindowManager
from event.top_bar_manager import TopBarManager
from event.tree_manager import TreeManager
from ui.main_window import MainWindow
from util.window_util import center_window


def initialize_application():
    init_folder()
    init_db()
    data_initializer = DataInitializer()
    data_initializer.initialize()

def main():
    initialize_application()
    root = tk.Tk()
    root.title("openai chat")
    root.geometry("1000x620")
    center_window(root, None,1000, 630)

    main_window = MainWindow(root)
    TopBarManager(main_window)
    SettingWindowManager(main_window)
    AdvancedLogWindowManager(main_window)
    MainManager(main_window)
    ListManager(main_window)
    OutputManager(main_window)
    TreeManager(main_window)
    InputManager(main_window)


    root.mainloop()
if __name__ == "__main__":
    main()
