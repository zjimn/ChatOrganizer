import textwrap
import tkinter as tk
from tkinter import ttk

from PIL.ImageOps import expand

from util.undo_redo_entry import UndoRedoEntry
from util.window_util import center_window  # 假设这个函数是你定义的

class InputDialog:
    def __init__(self, parent = None, title="输入", prompt="输入内容", init_content = "", confirm_name ="确定", cancel_name ="取消", width = 200, height = 120):

        if not parent:
            parent = parent
        self.parent = parent
        self.result = None
        self.entry = None
        self.input_content = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.attributes('-toolwindow', True)
        self.dialog.attributes('-topmost', True)
        self.dialog.title(title)

        # 计算窗口高度，最小高度为100
        win_width = width
        win_height = height
        self.dialog.geometry(f"{win_width}x{win_height}")
        self.dialog.resizable(False, False)

        # 添加提示信息
        label = ttk.Label(self.dialog, text=prompt, wraplength=win_width - 43, font=("Microsoft YaHei UI", 10))
        label.pack(side=tk.TOP, padx=10, pady=(5, 2), anchor=tk.W)

        self.entry = UndoRedoEntry(self.dialog, width=20, style="Custom.TEntry")
        self.entry.pack(side=tk.TOP, padx=10, pady=(3,5), fill = tk.X)

        # 添加按钮
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(side=tk.BOTTOM, padx=0, pady=(5, 10), fill = tk.X)



        yes_button = ttk.Button(button_frame, text=confirm_name, command=self.on_confirm, width=10)
        yes_button.pack(side="right", padx=10)

        no_button = ttk.Button(button_frame, text=cancel_name, command=self.on_cancel, width=10)
        no_button.pack(side="left", padx=10)

        # 处理关闭窗口
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_close)
        center_window(self.dialog, parent, win_width, win_height)
        self.dialog.grab_set()
        self.dialog.transient(parent)
        self.entry.focus()
        self.entry.delete(0, tk.END)
        self.entry.insert(0, init_content)
        root = self.dialog.winfo_toplevel()
        root.wait_window(self.dialog)

    def on_confirm(self):
        self.result = True
        self.input_content = self.entry.get()
        self.close_dialog()

    def on_cancel(self):
        self.result = False
        self.entry.delete(0, tk.END)
        self.input_content = self.entry.get()
        self.close_dialog()

    def on_close(self):
        self.result = None
        self.close_dialog()

    def close_dialog(self):
        self.dialog.grab_release()
        self.dialog.destroy()



if __name__ == "__main__":
    def confirm_delete():
        dialog = InputDialog(title="确认删除", prompt="444444")
        root.wait_window(dialog.dialog)
        if dialog.result:
            print("用户确认删除")
        else:
            print("用户取消删除")

    root = tk.Tk()
    root.title("删除确认示例")
    root.geometry("300x400")

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