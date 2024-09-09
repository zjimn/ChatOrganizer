import tkinter as tk
from events import bind_events, adjust_option_menu_width
from ui import MainWindow
from data_management import DataManagement  # Import the class

def main():
    root = tk.Tk()
    root.title("GPT Completion Tool")
    root.geometry("800x600")

    main_window = MainWindow(root)
    # 创建 UI 元素

    # 绑定事件
    bind_events(root, main_window)

    data_manager = DataManagement(main_window)
    data_manager.update_txt_data_items(main_window.output_frame)
    main_window.data_manager = data_manager

    # 调整下拉列表宽度
    adjust_option_menu_width(main_window)

    root.mainloop()

if __name__ == "__main__":
    main()
