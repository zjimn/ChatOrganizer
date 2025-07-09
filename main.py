import tkinter as tk
from tkinter import messagebox

from db.data_initializer import DataInitializer
from db.database import init_db
from event.advanced_log_window_manager import AdvancedLogWindowManager
from event.input_manager import InputManager
from event.list_manager import ListManager
from event.main_manager import MainManager
from event.output_manager import OutputManager
from event.setting_window_manager import SettingWindowManager
from event.top_bar_manager import TopBarManager
from event.tree_manager import TreeManager
from ui.main_window import MainWindow
from util.file_util import init_folder
from util.logger import logger
from util.window_util import center_window
from widget.loading_screen import LoadingScreen


def initialize_application():
    init_folder()
    init_db()
    data_initializer = DataInitializer()
    data_initializer.initialize()

def main():
    # 创建主窗口
    root = tk.Tk()
    root.title("AI对话管理")
    root.geometry("1000x563")
    root.geometry(f"{1}x{1}+{10000}+{10000}")
    root.iconbitmap("res/icon/app_logo_small.ico")
    loading_screen = LoadingScreen(root)
    loading_screen.create()
    root.update()

    loading_screen.update_loading_info("初始化数据")
    initialize_application()
    loading_screen.update_loading_info("初始化数据完成")
    loading_screen.update_loading_info("初始化窗口")
    main_window = MainWindow(root)
    loading_screen.update_loading_info("初始化窗口完成")
    loading_screen.update_loading_info("加载数据")
    TopBarManager(main_window)
    SettingWindowManager(main_window)
    AdvancedLogWindowManager(main_window)
    MainManager(main_window)
    list_manager = ListManager(main_window)
    output_manager = OutputManager(main_window)
    TreeManager(main_window)
    InputManager(main_window)
    loading_screen.update_loading_info("加载数据完成")
    loading_screen.update_loading_info("启动中")
    root.after(1000, loading_screen.close, lambda: on_loading_screen_closed(root, list_manager, output_manager))

    root.mainloop()

def on_loading_screen_closed(root, list_manager, output_manager):
    center_window(root, None, 1000, 563)
    output_manager.set_output_window_pos()
    list_manager.update_scrollbar_visibility()



if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        message = f"错误: {type(e).__name__}: {e}"
        logger.log("critical", message)
        messagebox.showerror("错误", message)

