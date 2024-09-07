import tkinter as tk
from tkinter import ttk, scrolledtext


def create_ui(root):
    """创建主窗口和主要组件。"""


    # 创建底部框架
    bottom_frame = tk.Frame(root)
    bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

    # 创建输入框
    style = ttk.Style()
    style.configure("Custom.TEntry", padding=(3, 3))

    input_text = ttk.Entry(bottom_frame, width=50, style="Custom.TEntry")
    input_text.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=(0, 15))

    input_text.config(font=("Microsoft YaHei", 10))

    # 创建提交按钮
    submit_button = tk.Button(bottom_frame, text="获取回答")
    submit_button.pack(side=tk.RIGHT, padx=10, pady=(0, 15))

    # 创建下拉列表
    option_var = tk.StringVar(value="文字")  # 默认值
    options = ["文字", "图片"]
    option_menu = tk.OptionMenu(bottom_frame, option_var, *options)
    option_menu.pack(side=tk.RIGHT, padx=5, pady=(0, 15))

    size_var = tk.StringVar(value="1024x1024")
    size_options = ["1024x1024", "1792x1024", "1024x1792"]
    size_menu = tk.OptionMenu(bottom_frame, size_var, *size_options)
    size_menu.pack(side=tk.RIGHT, padx=5, pady=(0, 15))
    size_menu.pack_forget()

    # 创建显示框
    output_frame = tk.Frame(root)
    output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD)
    output_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    output_text.config(state=tk.DISABLED, font=("Microsoft YaHei", 12))

    # 创建图片显示标签
    output_image = tk.Label(output_frame)
    output_image.pack_forget()  # 默认隐藏

    # 返回必要的组件供事件绑定使用
    return input_text, option_var, output_text, output_image, size_var, submit_button, size_menu, option_menu

