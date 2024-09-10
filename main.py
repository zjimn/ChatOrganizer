import tkinter as tk

from db.config_data_access import ConfigDataAccess
from db.database import init_db
from events import EventManager
from system_config import SystemConfig

from ui import MainWindow
from data_management import DataManagement  # Import the class

def main():
    init_db()
    system_config = SystemConfig()
    root = tk.Tk()
    root.title("GPT Completion Tool")
    root.geometry("800x600")

    config_data_access = ConfigDataAccess()
    main_window = MainWindow(root, config_data_access)
    # 创建 UI 元素
    # 绑定事件
    event_manager = EventManager(root, main_window, config_data_access, system_config)
    event_manager.bind_events()

    data_manager = DataManagement(main_window)
    data_manager.update_data_items()
    main_window.data_manager = data_manager
    # 调整下拉列表宽度
    event_manager.adjust_option_menu_width()

    root.mainloop()

if __name__ == "__main__":
    main()
