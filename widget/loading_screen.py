
import tkinter as tk
from tkinter import ttk

from util.window_util import center_window


class LoadingScreen:
    def __init__(self, root):
        self.root = root
        self.loading_window = None
        self.loading_label = None
        self.message = ""
        self.dots = 0
        self.message_timer = None
        self.on_close_callback = None

    def create(self, on_close_callback=None):
        """创建加载画面"""
        self.loading_window = tk.Toplevel(self.root)
        self.loading_window.title("加载中")
        center_window(self.loading_window, None, 400, 200)
        self.loading_window.config(bg="white")
        self.loading_window.iconbitmap("res/icon/app_logo_small.ico")
        # 设置窗口关闭事件
        self.on_close_callback = on_close_callback
        self.loading_window.protocol("WM_DELETE_WINDOW", self._on_window_close)

        # 加载标签
        label = ttk.Label(self.loading_window, text="正在加载，请稍候...", font=("Microsoft YaHei UI", 10,  "bold"))
        label.pack(pady=20)

        # 显示一个进度条
        progress = ttk.Progressbar(self.loading_window, mode="indeterminate")
        progress.pack(fill="x", padx=20, pady=10)
        progress.start()

        self.loading_label = tk.Label(self.loading_window, text="", font=("Microsoft YaHei UI", 10), bg="white", anchor="w")
        self.loading_label.pack(side="bottom", anchor="w", padx=20, pady=5)

        self.root.update_idletasks()

    def _on_window_close(self):
        if self.on_close_callback:
            self.on_close_callback()
        self.close()

    def close(self, callback=None):
        self.stop_message_timer()
        if self.loading_window:
            self.loading_window.destroy()
        if callback:
            callback()

    def update_loading_info(self, message):
        self.message = message
        self.dots = 0  # 重置dots
        self.stop_message_timer()
        self._show_message()

    def _show_message(self):
        message_with_dots = self.message + "." * (self.dots + 1)
        self.loading_label.config(text=message_with_dots)
        self.dots = (self.dots + 1) % 3
        self.message_timer = self.root.after(500, self._show_message)

    def stop_message_timer(self):
        """停止消息计时器"""
        if self.message_timer:
            self.root.after_cancel(self.message_timer)
            self.message_timer = None