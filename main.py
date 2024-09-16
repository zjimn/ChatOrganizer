import tkinter as tk

from config.app_config import AppConfig
from event.tree_manager import TreeManager
from db.database import init_db
from event.events import EventManager

from ui.main_window import MainWindow
from event.list_manager import ListManager  # Import the class

def main():
    init_db()
    system_config = AppConfig()
    root = tk.Tk()
    root.title("GPT Completion Tool")
    root.geometry("800x600")

    main_window = MainWindow(root)
    content_hierarchy_tree_manager = TreeManager(root, main_window.directory_tree)
    # 绑定事件
    event_manager = EventManager(root, main_window, system_config, content_hierarchy_tree_manager)
    event_manager.bind_events()

    data_manager = ListManager(root, main_window.display_frame.tree)

    #cht.add_test_data()
    data_manager.update_data_items()
    main_window.data_manager = data_manager
    # 调整下拉列表宽度
    event_manager.adjust_option_menu_width()

    root.mainloop()

if __name__ == "__main__":
    main()
