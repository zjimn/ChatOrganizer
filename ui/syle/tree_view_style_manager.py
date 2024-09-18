# treeview_style_manager.py
from tkinter import ttk


class TreeViewStyleManager:
    def __init__(self, tree):
        self.tree = tree
        self.style = ttk.Style()
        self.style.theme_use('clam')

    def configure_styles(self):
        # Configure general style for the tree
        self.style.configure('List.Treeview',
                             rowheight=50, font=("Arial", 12),
                             padding=(5, 10, 5, 10),
                             fieldbackground='white',
                             bordercolor='#cccccc',  # Column border color
                             borderwidth=1,
                             highlightthickness=1,  # Highlight border thickness
                             bd=1,  # Border width
                             )
        self.style.configure('List.Treeview.Heading',
                             borderwidth=0,
                             relief='flat',
                             padding=(10, 10, 10, 10),
                             font=('Helvetica', 15, 'bold'),
                             background='#f0f0f0',  # Heading background color
                             foreground='#232323'  # Heading text color
                             )
        self.style.map('List.Treeview', background=[('selected', '#e8f0fe')])
        self.style.map('List.Treeview', foreground=[('selected', '#1a73e8')])
        # Configure tags for row colors
        self.tree.tag_configure('even', background='#f0f0f0', foreground='#505050')
        self.tree.tag_configure('odd', background='white', foreground='#505050')
        self.tree.tag_configure('hover', background='#e6e6e6', foreground='#505050')

    def configure_image_style(self):
        self.configure_styles()
        # Configure Treeview style specific for image items
        self.style.configure('List.Treeview',
                             rowheight=100, font=("Arial", 12),
                             padding=(5, 10, 5, 10),
                             fieldbackground='white',
                             bordercolor='#cccccc',  # Column border color
                             borderwidth=10,
                             )
        self.tree["show"] = "tree headings"
        self.tree["displaycolumns"] = ("prompt", "create_time")

    def configure_text_style(self):
        self.configure_styles()
        # Configure Treeview style specific for text items
        self.tree["show"] = "headings"
        self.tree["displaycolumns"] = ("prompt", "content", "create_time")
        self.style.configure("List.Treeview", font=("Arial", 12))  # Set font for text style


    def set_tree_style(self):
        self.style.map('Tree.Treeview', background=[('selected', '#add8e6')])
        self.style.map('Tree.Treeview', foreground=[('selected', 'white')])
        self.style.configure('Tree.Treeview',
                        rowheight=40, font=("Arial", 12),
                        padding=(5, 10, 5, 10),
                        fieldbackground = 'white',
                        background='white',  # Background color for the entire treeview
                        foreground='#0d0d0d',  # Font color
                        bordercolor = '#cccccc',  # 设置列之间的竖线颜色
                        borderwidth = 10,
                        highlightthickness=1,  # 设置高亮边框厚度
                        bd=1,  # 设置边框宽度
                        #relief = 'solid'  # 使用 solid 来显示边框
                             )
        self.tree.tag_configure('normal', background='white', foreground='#0d0d0d')
        self.tree.tag_configure('hover', background='#e8eaed', foreground='#0d0d0d')
        self.style.map('Tree.Treeview', background=[('selected', '#e8f0fe')])
        self.style.map('Tree.Treeview', foreground=[('selected', '#1a73e8')])