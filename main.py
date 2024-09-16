import tkinter as tk

from hierarchy_tree_manager import HierarchyTreeManager
from db.config_data_access import ConfigDataAccess
from db.database import init_db
from events import EventManager
from system_config import SystemConfig

from ui import MainWindow
from list_data_manager import ListDataManager  # Import the class

def main():
    init_db()
    system_config = SystemConfig()
    root = tk.Tk()
    root.title("GPT Completion Tool")
    root.geometry("800x600")

    config_data_access = ConfigDataAccess()
    main_window = MainWindow(root, config_data_access)
    content_hierarchy_tree_manager = HierarchyTreeManager(main_window)
    # 绑定事件
    event_manager = EventManager(root, main_window, config_data_access, system_config, content_hierarchy_tree_manager)
    event_manager.bind_events()

    data_manager = ListDataManager(main_window)

    #cht.add_test_data()
    data_manager.update_data_items()
    main_window.data_manager = data_manager
    # 调整下拉列表宽度
    event_manager.adjust_option_menu_width()

    root.mainloop()

if __name__ == "__main__":
    main()
