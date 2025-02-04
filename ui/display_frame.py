import tkinter as tk
from tkinter import ttk
from PIL import ImageTk
from ttkbootstrap import Style

from config import constant
from widget.undo_redo_entry import UndoRedoEntry
from ui.syle.tree_view_style_manager import TreeViewStyleManager
from util import image_util


class DisplayFrame:
    def __init__(self, parent):
        self.parent = parent
        self.right_frame = ttk.Frame(parent)
        closed_folder_resized = image_util.resize_image_by_path(constant.CLOSED_FOLDER_IMAGE, (20, 20))
        self.closed_folder_resized_icon = ImageTk.PhotoImage(closed_folder_resized)
        # self.style = ttk.Style()
        self.style = Style(theme="flatly")
        self.top_frame = ttk.Frame(self.right_frame)
        self.top_frame.pack(side=tk.TOP, fill=tk.X)
        self.search_button = ttk.Button(self.top_frame, text="搜索")
        self.search_button.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 0), pady=(0, 10),anchor=tk.S)
        self.search_input_entry_text = tk.StringVar()
        self.style.configure("Custom.TEntry")
        self.search_input_text = UndoRedoEntry(self.top_frame, width=50, style="Custom.TEntry",
                                           textvariable=self.search_input_entry_text)
        self.search_input_text.pack(side=tk.LEFT, fill=tk.X, padx=0, pady=(0, 10), anchor=tk.S,expand = True)
        self.search_input_text.config(font=("Microsoft YaHei", 10))
        self.pagination_frame = ttk.Frame(self.right_frame, borderwidth=1, relief="raised")
        self.pagination_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.prev_button = tk.Button(self.pagination_frame, text="上一页")
        self.prev_button.pack(side=tk.LEFT)
        self.page_label = tk.Label(self.pagination_frame, text="")
        self.page_label.pack(side=tk.LEFT)
        self.next_button = tk.Button(self.pagination_frame, text="下一页")
        self.next_button.pack(side=tk.LEFT)
        self.total_label = tk.Label(self.pagination_frame, text="")
        self.total_label.pack(side=tk.LEFT)
        self.tree_frame = ttk.Frame(self.right_frame)
        self.tree_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.tree = None

        self.style.configure('Txt.List.Treeview',
                             rowheight=50, font=("微软雅黑", 12),
                             padding=(5, 10, 5, 10),
                             fieldbackground='white',
                             bordercolor='#cccccc',
                             borderwidth=1,
                             highlightthickness=1,
                             bd=1,
                             )
        self.style.configure('Txt.List.Treeview.Heading',
                             borderwidth=0,
                             relief='flat',
                             padding=(10, 10, 10, 10),
                             font=('微软雅黑', 15, 'bold'),
                             background='#f0f0f0',
                             foreground='#232323'
                             )
        self.txt_tree = ttk.Treeview(self.tree_frame, columns=("id", "describe", "content", "create_time"),
                                     style='Txt.List.Treeview')
        self.txt_tree.heading("id", text="id")
        self.txt_tree.heading("describe", text="描述")
        self.txt_tree.heading("content", text="内容")
        self.txt_tree.heading("create_time", text="创建时间")
        self.txt_tree.column("id", width=0, anchor="center")
        self.txt_tree.column("describe", width=150, anchor="center")
        self.txt_tree.column("content", width=200, anchor="center")
        self.txt_tree.column("create_time", width=100, anchor="center")
        self.tree_txt_scrollbar = tk.Scrollbar(self.txt_tree, orient=tk.VERTICAL, command=self.txt_tree.yview)
        self.tree_txt_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_tree.configure(yscrollcommand=self.tree_txt_scrollbar.set)
        self.txt_tree.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        self.style_manager = TreeViewStyleManager(self.txt_tree)
        self.style_manager.configure_text_style()
        self.tree = self.txt_tree
        self.style.configure('Img.List.Treeview',
                             rowheight=95, font=("微软雅黑", 12),
                             padding=(5, 10, 5, 10),
                             fieldbackground='white',
                             bordercolor='#cccccc',
                             borderwidth=1,
                             highlightthickness=1,
                             bd=1,
                             )
        self.style.configure('Img.List.Treeview.Heading',
                             borderwidth=0,
                             relief='flat',
                             padding=(10, 20, 10, 20),
                             font=('微软雅黑', 15, 'bold'),
                             background='#f0f0f0',
                             foreground='#232323'
                             )
        self.img_tree = ttk.Treeview(self.tree_frame, columns=("#0", "id", "img", "describe", "create_time"),
                                     style='Img.List.Treeview')
        self.img_tree.heading("#0", text="图片")
        self.img_tree.heading("id", text="id")
        self.img_tree.heading("img", text="图片")
        self.img_tree.heading("describe", text="描述")
        self.img_tree.heading("create_time", text="创建时间")
        self.img_tree.column("#0", width=100, anchor="center")
        self.img_tree.column("id", width=0, anchor="center")
        self.img_tree.column("img", width=0, anchor="center")
        self.img_tree.column("describe", width=250, anchor="center")
        self.img_tree.column("create_time", width=100, anchor="center")
        self.tree_img_scrollbar = tk.Scrollbar(self.img_tree, orient=tk.VERTICAL, command=self.img_tree.yview)
        self.tree_img_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.img_tree.configure(yscrollcommand=self.tree_img_scrollbar.set)
        self.style_manager = TreeViewStyleManager(self.img_tree)
        self.style_manager.configure_image_style()
        self.img_tree.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        self.img_tree.pack_forget()
        self.tree_img_scrollbar.pack_forget()
        self.bottom_frame = ttk.Frame(self.right_frame, height=0)
        self.bottom_frame.pack(side=tk.TOP, fill=tk.BOTH)