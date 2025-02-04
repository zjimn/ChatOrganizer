from tkinter import ttk

import tkinter as tk
from ttkbootstrap import Style

from util.window_util import center_window


class ModelViewer:
    def __init__(self, parent):
        self.win_width = 373
        self.win_height = 250
        self.parent = parent
        self.main_window = tk.Toplevel(parent)
        self.main_window.title("模型管理")
        self.main_window.geometry(f"{self.win_width}x{self.win_height}")
        center_window(self.main_window, self.parent, self.win_width, self.win_height)
        # main_window.resizable(False, False)
        # self.main_window.attributes('-topmost', True)
        name = ""

        main_frame = ttk.Frame(self.main_window, borderwidth=0, relief=tk.RAISED)

        self.top_frame = ttk.Frame(main_frame, borderwidth=0, relief=tk.RAISED)
        hidden_model_id_label = ttk.Label(self.top_frame, text="", font=("Microsoft YaHei UI", 10))
        hidden_model_id_label.pack_forget()
        detail_label = ttk.Label(self.top_frame, text="(选择添加模型服务对应的模型)", font=("Microsoft YaHei UI", 10))
        detail_label.pack(side=tk.LEFT, padx=(10, 10), pady=5)

        self.save_button = ttk.Button(self.top_frame, text="保存", state=tk.NORMAL)

        self.save_button.pack(side=tk.RIGHT, padx=(10, 10))
        self.top_frame.pack(side=tk.TOP, fill=tk.X, padx=(0, 0), pady=(10, 10))

        separator_frame = ttk.Frame(main_frame, borderwidth=0, relief=tk.RAISED)
        separator = ttk.Separator(separator_frame, orient="horizontal")
        separator.pack(side="left", fill="x", padx=0, expand=True)
        separator_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(5, 0))

        self.detail_label_frame = ttk.Frame(main_frame)
        self.detail_label_frame.pack(side=tk.TOP, fill=tk.X, padx=(0, 0), pady=(10, 0))
        detail_label = ttk.Label(self.detail_label_frame, text="模型: ", font=("Microsoft YaHei UI", 10))
        detail_label.pack(side=tk.LEFT, padx=(10, 10), pady=5)

        self.input_body_frame = ttk.Frame(main_frame)
        self.input_body_frame.pack(side=tk.TOP, fill=tk.X, padx=(0, 0), pady=(0, 10))

        self.add_frame = ttk.Frame(main_frame)
        self.add_frame.pack(side=tk.TOP, fill=tk.X, padx=(0, 0), pady=5)

        self.add_button = ttk.Button(self.add_frame, text="添加", state=tk.NORMAL)
        self.add_button.pack(side=tk.TOP, fill=tk.X, padx=(10, 10), expand=True)
        main_frame.pack(side='left', padx=(5, 5), pady=(0, 0), fill=tk.BOTH, expand=True)

        self.main_window.withdraw()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("model Viewer")
    root.geometry("300x200")
    style = Style(theme='flatly')

    preset_viewer = ModelViewer(root)
    root.mainloop()
