
import tkinter as tk
from tkinter import ttk

from util.window_util import center_window


class CustomConfirmDialog:
    def __init__(self, parent = None, title="错误", message="", width = 250, height = 100):
        self.title = title
        self.message = message
        message_window = tk.Toplevel(parent)
        message_window.transient()
        message_window.grab_set()
        message_window.title(self.title)
        #message_window.resizable(False, False)
        message_window.attributes('-topmost', True)
        window_width = width

        window_height = height

        # 计算窗口在屏幕中心的位置
        screen_width = message_window.winfo_screenwidth()
        screen_height = message_window.winfo_screenheight()
        position_top = int((screen_height - window_height) / 2)
        position_right = int((screen_width - window_width) / 2)

        if parent:
            center_window(message_window, parent, window_width, window_height)
        else:
            message_window.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")

        # 创建错误消息的标签
        label = ttk.Label(message_window, text=self.message, wraplength=window_width - 40, font=("Microsoft YaHei UI", 10))
        label.pack(side=tk.TOP, padx=20, pady=15, anchor=tk.W)

        # 创建确认按钮
        close_button = ttk.Button(message_window, text="确定", command=message_window.destroy, width = 10)
        close_button.pack(side=tk.RIGHT, padx=15, pady=(0, 15), anchor=tk.SE)

# 示例调用
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    dialog = CustomConfirmDialog(title="错误", message="文件不存在或无法读取1234567891。")
