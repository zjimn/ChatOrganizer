import tkinter as tk
from distutils.command.config import config
from tkinter import ttk, scrolledtext
import config
from db.config_data_access import ConfigDataAccess
from record_manager import load_records, load_txt_records
from data_management import DataManagement
from enums import ViewType


class MainWindow:
    def __init__(self, root, config_data_access):
        self.__type_option = None
        self.__size_option = None
        self.__config_data_access = config_data_access
        self.set_config_from_database()
        # Initialize member variables
        self.style = None
        self.scrollbar = None
        self.txt_frame = None
        self.canvas = None
        self.tree = None
        self.root = root
        self.bottom_frame = None
        self.input_text = None
        self.submit_button = None
        self.option_var = None
        self.option_menu = None
        self.size_var = None
        self.size_menu = None
        self.output_frame = None
        self.output_text = None
        self.output_image = None
        self.output_image = None
        self.data_manager = None
        self.view_type = ViewType.TXT
        # Create the UI
        self.create_ui()

    def set_config_from_database(self):
        self.__size_option = self.__config_data_access.get_operation_config_value_by_key(config.IMG_SIZE_OPTION_KEY, 0)
        self.__type_option = self.__config_data_access.get_operation_config_value_by_key(config.TYPE_OPTION_KEY, 0)

    def create_ui(self):
        """创建主窗口和主要组件。"""

        self.style = ttk.Style()
        self.style.theme_use('clam')

        # 创建底部框架
        self.bottom_frame = tk.Frame(self.root)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

        # 创建输入框
        self.style.configure("Custom.TEntry", padding=(3, 3))

        self.input_text = ttk.Entry(self.bottom_frame, width=50, style="Custom.TEntry")
        self.input_text.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=(0, 15))
        self.input_text.config(font=("Microsoft YaHei", 10))

        # 创建提交按钮
        self.submit_button = ttk.Button(self.bottom_frame, text="获取回答")
        self.submit_button.pack(side=tk.RIGHT, padx=10, pady=(0, 15))

        # 创建下拉列表
        self.option_var = tk.StringVar(value="文字")  # 默认值
        options = ["文字", "图片"]
        self.option_menu = ttk.OptionMenu(self.bottom_frame, self.option_var, options[self.__type_option],*options)
        self.option_menu.pack(side=tk.RIGHT, padx=5, pady=(0, 15))

        # 创建尺寸选择菜单
        self.size_var = tk.StringVar(value="1024x1024")
        size_options = ["1024x1024", "1792x1024", "1024x1792"]
        self.size_menu = ttk.OptionMenu(self.bottom_frame, self.size_var, size_options[self.__size_option], *size_options)
        self.size_menu.pack(side=tk.RIGHT, padx=5, pady=(0, 15))
        self.size_menu.pack_forget()  # Initially hidden

        # 创建显示框
        self.output_frame = tk.Frame(self.root)
        self.output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        #self.output_frame.pack_forget()  # 默认隐藏
        # Create Canvas component
        self.canvas = tk.Canvas(self.output_frame, bg="#f0f0f0", width=600, height=200)


        self.txt_frame = tk.Frame(self.output_frame)
        self.txt_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.txt_frame.pack_forget()  # 默认隐藏
        self.output_text = scrolledtext.ScrolledText(self.output_frame, wrap=tk.WORD, state=tk.DISABLED)
        #self.output_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.output_text.pack_forget()
        self.output_text.config(font=("Microsoft YaHei", 12), padx=10, pady=10)

        # 创建图片显示标签
        self.output_image = tk.Label(self.canvas, bg="#f0f0f0")
        self.output_image.pack_forget()  # 默认隐藏


        # Create Treeview component
        self.tree = ttk.Treeview(self.output_frame, columns=("prompt", "img", "content", "create_time", "operation"), height=7)
        self.tree.heading("#0", text="图片")  # Default column for images
        self.tree.heading("img", text="图片")
        self.tree.heading("prompt", text="描述")
        self.tree.heading("content", text="内容")
        self.tree.heading("create_time", text="创建时间")
        self.tree.heading("operation", text="操作")
        self.tree.column("#0", width=100, anchor="center")
        self.tree.column("img", width=1000, anchor="center")
        self.tree.column("prompt", width=450, anchor="center")
        self.tree.column("content", width=450, anchor="center")
        self.tree.column("create_time", width=150, anchor="center")
        self.tree.column("operation", width=150, anchor="center")
        # Create the vertical scrollbar
        self.scrollbar = tk.Scrollbar(self.tree, orient=tk.VERTICAL, command=self.tree.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        # Add Treeview to window
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.tree.configure(yscrollcommand=self.scrollbar.set)

#class MainWin:



if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow(root)
    records = load_txt_records()
    root.mainloop()
