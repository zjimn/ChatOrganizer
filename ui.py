import tkinter as tk
from distutils.command.config import config
from tkinter import ttk, scrolledtext
import config
from db.config_data_access import ConfigDataAccess
from db.database import init_db
from record_manager import load_records, load_txt_records
from data_management import DataManagement
from enums import ViewType
from system_config import SystemConfig


class MainWindow:
    def __init__(self, root, config_data_access):
        self.top_frame = None
        self.left_frame = None
        self.search_input_text = None
        self.search_input_entry_text = tk.StringVar()
        self.right_frame = None
        self.output_window_scrollbar_frame = None
        self.output_window_scrollbar = None
        self.tree_frame = None
        self.output_window = None
        self.type_option = None
        self.__size_option = None
        self.__config_data_access = config_data_access
        self.set_config_from_database()
        # Initialize member variables
        self.style = None
        self.tree_scrollbar = None
        self.txt_frame = None
        self.output_window_canvas = None
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
        self.__size_option = int(self.__config_data_access.get_config_value_by_key(config.IMG_SIZE_OPTION_KEY, '0'))
        self.type_option = int(self.__config_data_access.get_config_value_by_key(config.TYPE_OPTION_KEY, '0'))

    def create_ui(self):
        """创建主窗口和主要组件。"""

        self.style = ttk.Style()
        self.style.theme_use('clam')




        # 创建底部框架
        self.bottom_frame = tk.Frame(self.root)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=(5, 20))

        # 创建输入框
        self.style.configure("Custom.TEntry", padding=(3, 3))
        self.input_text = tk.Text(self.bottom_frame, width=10, height = 1, padx=5, pady=5)
        self.input_text.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.input_text.config(font=("Microsoft YaHei", 10))

        # 创建提交按钮
        self.submit_button = ttk.Button(self.bottom_frame, text="获取回答")
        self.submit_button.pack(side=tk.RIGHT, padx=(10, 0), anchor=tk.S)

        # 创建下拉列表
        self.option_var = tk.StringVar(value="文字")  # 默认值
        options = ["文字", "图片"]
        self.option_menu = ttk.OptionMenu(self.bottom_frame, self.option_var, options[self.type_option],*options)
        self.option_menu.pack(side=tk.RIGHT, padx=5, anchor=tk.S)

        # 创建尺寸选择菜单
        self.size_var = tk.StringVar(value="1024x1024")
        size_options = ["1024x1024", "1792x1024", "1024x1792"]
        self.size_menu = ttk.OptionMenu(self.bottom_frame, self.size_var, size_options[self.__size_option], *size_options)
        self.size_menu.pack(side=tk.RIGHT, padx=5, anchor=tk.S)
        self.size_menu.pack_forget()  # Initially hidden




        # 创建底部框架
        self.top_frame = tk.Frame(self.root)

        self.top_frame.pack(side=tk.TOP, fill=tk.BOTH,  expand=True, padx=20, pady=(20, 5))





        # 创建底部框架
        self.right_frame = tk.Frame(self.top_frame)
        #self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=20, expand=True, pady=(20, 5))
        #self.right_frame.grid(row=0, column=0, sticky="ns")
        self.right_frame.grid(row=0, column=1, sticky="nswe")

        # 创建底部框架
        self.left_frame = tk.Frame(self.top_frame)
        #self.left_frame.grid(row=0, column=0, sticky="ns")
        self.left_frame.grid(row=0, column=0, sticky="nswe", padx=(0, 10))  # 使用 grid 放置
        #self.left_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=20, expand=True, pady=(20, 5))

        self.top_frame.grid_columnconfigure(0, weight=1)  # 左侧框架占 1/3
        self.top_frame.grid_columnconfigure(1, weight=5)  # 右侧框架占 2/3
        self.top_frame.grid_rowconfigure(0, weight=1)
        # 创建输入框
        self.style.configure("Custom.TEntry", padding=(3, 5))
        self.search_input_text = ttk.Entry(self.right_frame, width=50, style="Custom.TEntry", textvariable=self.search_input_entry_text)
        self.search_input_text.pack(side=tk.TOP, fill=tk.X, padx=0, pady=(0, 10), anchor=tk.S)
        self.search_input_text.config(font=("Microsoft YaHei", 10))

        # 创建显示框
        self.tree_frame = tk.Frame(self.right_frame)
        self.tree_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # Create Treeview component
        self.tree = ttk.Treeview(self.tree_frame, columns=("#0","id", "img", "prompt", "content", "create_time", "operation"))
        self.tree.heading("#0", text="图片")  # Default column for images
        self.tree.heading("id", text="id")
        self.tree.heading("img", text="图片")
        self.tree.heading("prompt", text="描述")
        self.tree.heading("content", text="内容")
        self.tree.heading("create_time", text="创建时间")
        self.tree.heading("operation", text="操作")
        self.tree.column("#0", width=100, anchor="center")
        self.tree.column("id", width=150, anchor="center")
        self.tree.column("img", width=1000, anchor="center")
        self.tree.column("prompt", width=450, anchor="center")
        self.tree.column("content", width=450, anchor="center")
        self.tree.column("create_time", width=150, anchor="center")
        self.tree.column("operation", width=150, anchor="center")
        # Create the vertical scrollbar
        self.tree_scrollbar = tk.Scrollbar(self.tree, orient=tk.VERTICAL, command=self.tree.yview)
        #self.tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        # Add Treeview to window
        self.tree.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        self.tree.configure(yscrollcommand=self.tree_scrollbar.set)





        # 创建 Treeview 控件
        self.dir_tree = ttk.Treeview(self.left_frame)

        # 添加根节点
        root_node = self.dir_tree.insert("", "end", text="根节点", open=True)

        # 添加子节点到根节点
        child1 = self.dir_tree.insert(root_node, "end", text="子节点 1", open=True)
        child2 = self.dir_tree.insert(root_node, "end", text="子节点 2", open=True)

        # 添加子节点到子节点 1
        self.dir_tree.insert(child1, "end", text="子节点 1-1")
        self.dir_tree.insert(child1, "end", text="子节点 1-2")

        # 添加子节点到子节点 2
        self.dir_tree.insert(child2, "end", text="子节点 2-1")

        # 显示 Treeview 控件
        self.dir_tree.pack(expand=True, fill="both")



        self.output_window = tk.Toplevel(self.root)
        self.output_window.title("")
        self.output_window.withdraw()
        # 获取主窗口的位置
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        # 设置 Toplevel 窗口的尺寸和位置
        self.output_window.geometry(f"{800}x{600}+{x + 50}+{y + 50}")
        # 创建显示框
        self.output_frame = tk.Frame(self.output_window)
        # self.output_frame.pack_forget()  # 默认隐藏
        # Create Canvas component
        self.output_window_canvas = tk.Canvas(self.output_frame, bg="#f0f0f0", width=600)
        self.output_window_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.output_window_scrollbar = tk.Scrollbar(self.output_frame, orient=tk.VERTICAL,
                                                    command=self.output_window_canvas.yview)
        self.output_window_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure the canvas to use the scrollbar
        self.output_window_canvas.configure(yscrollcommand=self.output_window_scrollbar.set)

        # Create a frame inside the canvas to hold the content
        self.output_window_scrollbar_frame = tk.Frame(self.output_window_canvas)

        # Create a frame inside the canvas to hold the content
        self.output_window_canvas.create_window((0, 0), window=self.output_window_scrollbar_frame, anchor='nw')
        self.output_window_scrollbar_frame.bind("<Configure>", lambda e: self.output_window_canvas.configure(
            scrollregion=self.output_window_canvas.bbox("all")))

        self.output_text = scrolledtext.ScrolledText(self.output_window_canvas, wrap=tk.WORD, state=tk.DISABLED)
        self.output_text.pack_forget()
        self.output_text.config(font=("Microsoft YaHei", 12), padx=10, pady=10)

        # 创建图片显示标签
        self.output_image = tk.Label(self.output_window_canvas, bg="#f0f0f0")
        self.output_image.pack_forget()  # 默认隐藏


        self.output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))





        #self.output_frame_scrollbar = tk.Scrollbar(self.output_frame, orient=tk.VERTICAL, command=self.canvas.yview)





























    def set_dialog_images(self, data):
        # Clear previous data
        self.output_window.deiconify()  # Show the output window

        # Create display areas for each item in the data
        for item in data:
            # Create a frame inside the scrollable frame
            frame = tk.Frame(self.output_window_scrollbar_frame)
            frame.pack(side=tk.TOP, fill=tk.NONE, padx=10, pady=10)

            image_path = item.get('img_path')
            txt = f"{item.get('role')}: {item.get('message')}\n"
            text_label = tk.Label(frame, text=txt, font=('Arial', 12, 'bold'))
            text_label.pack(side=tk.TOP, anchor=tk.W)
            # Create a label to display the image
            img_label = tk.Label(frame)
            img_label.pack(side=tk.TOP, fill=tk.BOTH, expand=True)


#class MainWin:



if __name__ == "__main__":
    init_db()
    system_config = SystemConfig()
    root = tk.Tk()
    root.title("GPT Completion Tool")
    root.geometry("800x600")

    config_data_access = ConfigDataAccess()
    main_window = MainWindow(root, config_data_access)

    # Sample data with text and optional image paths
    test_data = [
        {"role": "User", "message": "This is a test message.", "img_path": None},
        {"role": "User", "message": "More content here with no image.", "img_path": None},
        {"role": "Bot", "message": "Testing multiple entries.", "img_path": "data/images/2024-09-10_04-38-26.png"},
        {"role": "User", "message": "Scrolling should work well with long text.", "img_path": None},
        {"role": "Bot", "message": "Testing multiple entries.", "img_path": "data/images/2024-09-10_04-38-26.png"}
    ]

    # Set dialog images and text with sample data
    main_window.set_dialog_images(test_data)




    root.mainloop()
