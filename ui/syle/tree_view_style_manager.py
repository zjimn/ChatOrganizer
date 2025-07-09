from tkinter import ttk

from ttkbootstrap import Style


class TreeViewStyleManager:
    def __init__(self, tree):
        self.tree = tree
        self.style = Style(theme= "flatly")
        self.tree.tag_configure('even', background='#f0f0f0', foreground='#505050')
        self.tree.tag_configure('odd', background='white', foreground='#505050')

    def configure_styles(self):
        self.tree.tag_configure('hover', background='#e6e6e6', foreground='#505050')

    def configure_image_style(self):
        self.configure_styles()
        self.style.configure('Img.List.Treeview',
                             rowheight=95, font=("Microsoft YaHei UI", 12),
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
                             font=('Microsoft YaHei UI', 15, 'bold'),
                             background='#f0f0f0',
                             foreground='#232323'
                             )
        self.style.map('Img.List.Treeview', background=[('selected', '#bdbdbd')])
        self.style.map('Img.List.Treeview', foreground=[('selected', '#272727')])
        self.style.configure("Txt.List.Treeview.Heading", background="#d9d9d9", foreground="#4d4d4d",
                             font=("Microsoft YaHei UI", 12, "bold"))
        self.style.map("Txt.List.Treeview.Heading", background=[("active", "#bdbdbd")], foreground=[("active", "#272727")])
        self.style.configure("Img.List.Treeview.Heading", background="#d9d9d9", foreground="#4d4d4d",
                             font=("Microsoft YaHei UI", 12, "bold"))
        self.style.map("Img.List.Treeview.Heading", background=[("active", "#bdbdbd")], foreground=[("active", "#272727")])
        self.tree["show"] = "tree headings"
        self.tree["displaycolumns"] = ("describe", "create_time")

    def configure_text_style(self):
        self.configure_styles()
        self.style.configure('Txt.List.Treeview',
                             rowheight=50, font=("Microsoft YaHei UI", 12),
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
                             font=('Microsoft YaHei UI', 15, 'bold'),
                             background='#f0f0f0',
                             foreground='#232323'
                             )
        self.style.map('Txt.List.Treeview', background=[('selected', '#bdbdbd')])
        self.style.map('Txt.List.Treeview', foreground=[('selected', '#272727')])
        self.tree["show"] = "headings"
        self.tree["displaycolumns"] = ("describe", "content", "create_time")

    def set_tree_style(self):
        self.style.map('Tree.Treeview', background=[('selected', '#add8e6')])
        self.style.map('Tree.Treeview', foreground=[('selected', 'white')])
        self.style.configure('Tree.Treeview',
                             rowheight=40, font=("Microsoft YaHei UI", 12),
                             padding=(5, 10, 5, 10),
                             fieldbackground='white',
                             background='white',
                             foreground='#0d0d0d',
                             bordercolor='#cccccc',
                             borderwidth=10,
                             highlightthickness=1,
                             bd=1,
                             )
        self.tree.tag_configure('normal', background='white', foreground='#0d0d0d')
        self.tree.tag_configure('hover', background='#e8eaed', foreground='#0d0d0d')
        self.style.map('Tree.Treeview', background=[('selected', '#bdbdbd')])
        self.style.map('Tree.Treeview', foreground=[('selected', '#272727')])

    def set_list_editor_tree_style(self):
        self.style.map('Editor.Tree.Treeview', background=[('selected', '#add8e6')])
        self.style.map('Editor.Tree.Treeview', foreground=[('selected', 'white')])
        self.style.configure('Editor.Tree.Treeview',
                             rowheight=25, font=("Microsoft YaHei UI", 10),
                             padding=(5, 10, 5, 10),
                             fieldbackground='white',
                             background='white',
                             foreground='#0d0d0d',
                             bordercolor='#cccccc',
                             borderwidth=10,
                             highlightthickness=1,
                             bd=1,
                             )
        self.tree.tag_configure('normal', background='white', foreground='#0d0d0d')
        self.tree.tag_configure('hover', background='#e8eaed', foreground='#0d0d0d')
        self.style.map('Editor.Tree.Treeview', background=[('selected', '#bdbdbd')])
        self.style.map('Editor.Tree.Treeview', foreground=[('selected', '#272727')])
