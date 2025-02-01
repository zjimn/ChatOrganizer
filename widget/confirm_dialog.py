import textwrap
import tkinter as tk
from tkinter import ttk

from util.window_util import center_window  # 假设这个函数是你定义的

class ConfirmDialog:
    def __init__(self, parent = None, title="确认", message="确定要执行此操作吗？", confirm_name = "确定", cancel_name = "取消", width = 250, height = 100):

        if not parent:
            parent = parent
        self.parent = parent
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.attributes('-topmost', True)
        self.dialog.title(title)

        # 计算窗口高度，最小高度为100
        win_width = width
        win_height = height
        self.dialog.geometry(f"{win_width}x{win_height}")
        self.dialog.resizable(False, False)

        # 添加提示信息
        label = ttk.Label(self.dialog, text=message, wraplength=win_width-43, font=("Microsoft YaHei UI", 10))
        label.pack(side=tk.TOP, padx=20, pady=15, anchor=tk.W)

        # 添加按钮
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(side=tk.BOTTOM, padx=0, pady=(0, 15), anchor=tk.E)

        yes_button = ttk.Button(button_frame, text=confirm_name, command=self.on_confirm, width=7)
        yes_button.pack(side="right", padx=(5,15))

        no_button = ttk.Button(button_frame, text=cancel_name, command=self.on_cancel, width=7)
        no_button.pack(side="right", padx=5)

        # 处理关闭窗口
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_close)
        center_window(self.dialog, parent, win_width, win_height)
        self.dialog.grab_set()
        self.dialog.transient(parent)
        self.dialog.attributes('-toolwindow', True)
        root = self.dialog.winfo_toplevel()
        root.wait_window(self.dialog)

    def on_confirm(self):
        self.result = True
        self.close_dialog()

    def on_cancel(self):
        self.result = False
        self.close_dialog()

    def on_close(self):
        self.result = None
        self.close_dialog()

    def close_dialog(self):
        self.dialog.grab_release()
        self.dialog.destroy()



if __name__ == "__main__":
    def confirm_delete():
        dialog = ConfirmDialog(title="确认删除", message="912345678912345678912323456789123456789123456789123456789")
        root.wait_window(dialog.dialog)
        if dialog.result:
            print("用户确认删除")
        else:
            print("用户取消删除")

    root = tk.Tk()
    root.title("删除确认示例")
    root.geometry("300x200")

    # 计算屏幕居中位置
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = 300
    window_height = 200
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # 添加按钮
    delete_button = ttk.Button(root, text="删除", command=confirm_delete)
    delete_button.pack(pady=50)

    root.mainloop()