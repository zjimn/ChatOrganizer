import re
import tkinter as tk
from tkinter import ttk, messagebox, DISABLED, NORMAL
from PIL import Image, ImageTk
import record_manager
from db.content_data_access import ContentDataAccess
from list_editor import ListEditor
from util.image_utils import resize_image


class ListDataManager:
    def __init__(self, main_window):
        # Create Treeview
        self.tree = main_window.tree
        self.main_window = main_window
        # Initialize style and image list
        self.style = ttk.Style()
        self.list_editor = ListEditor(self.main_window.root, self.tree)
        self.image_list = []
        # 创建右键菜单
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.bind_events()

    def configure_styles(self):
        # 设置 Treeview 标题的悬停和点击样式
        self.style.map('Treeview.Heading',
                  background=[('active', '#005f9e'),  # 鼠标悬停时的背景颜色
                              ('pressed', '#004080')],  # 点击时的背景颜色
                  foreground=[('active', 'white'),  # 鼠标悬停时的字体颜色
                              ('pressed', 'white')]  # 点击时的字体颜色
                  )
        self.style.configure('List.Treeview', background='blue', foreground='white')
        self.style.map('List.Treeview', background=[('selected', '#e8f0fe')])
        self.style.map('List.Treeview', foreground=[('selected', '#1a73e8')])
        # Configure tags for row colors
        self.tree.tag_configure('even', background='#f0f0f0', foreground='#505050')
        self.tree.tag_configure('odd', background='white', foreground='#505050')
        self.tree.tag_configure('hover', background='#e6e6e6', foreground='#505050')

    def bind_events(self):
        self.tree.bind("<Motion>", self.on_mouse_move)
        # 绑定列宽度变化事件
        self.tree.bind('<Configure>', self.on_tree_resize)

    def show_context_menu(self, event):
        # 弹出菜单项
        iid = self.tree.identify_row(event.y)
        if iid:
            selected_item_ids = self.tree.selection()
            if len(selected_item_ids) <= 1:
                self.context_menu.entryconfig(0, state=NORMAL)
                self.tree.selection_set(iid)
            else:
                self.context_menu.entryconfig(0, state=DISABLED)
            self.context_menu.post(event.x_root, event.y_root)


    def get_first_50_chars(self, text):
        if text is None:
            return ""
        # 将所有的换行符替换为空格，去掉空白行
        text = re.sub(r'\s*\n\s*', ' ', text)
        # 使用正则表达式替换连续的多个空格为一个空格
        text = re.sub(r'\s+', ' ', text).strip()
        # 返回前 50 个字符
        return text[:50]

    def update_txt_data_items(self, txt, selected_content_hierarchy_child_id = None):
        self.set_txt_style()
        self.clear_treeview()
        records = record_manager.load_txt_records(txt, selected_content_hierarchy_child_id)
        for index, record in enumerate(records):
            tag = self.get_tag(index)
            self.tree.insert("", tk.END, values=(
                record.id,
                "",
                "",
                record.describe,
                self.get_first_50_chars(record.content),
                record.create_time.strftime('%Y-%m-%d %H:%M'),
            ), tags=(tag,))
        self.tree.update_idletasks()
        self.tree.update()
        children = self.tree.get_children()
        if len(children) == 0:
            return
        last_item = self.tree.get_children()[-1]
        # Scroll to the last row
        self.tree.see(last_item)

    def insert_txt_data_item(self, content_id):
        self.set_txt_style()
        records = record_manager.load_txt_records(content_id=content_id)
        last_item = None
        for index, record in enumerate(records):
            tag = self.get_tag(index)
            last_item = self.tree.insert("", tk.END, values=(
                record.id,
                "",
                "",
                record.describe,
                self.get_first_50_chars(record.content),
                record.create_time.strftime('%Y-%m-%d %H:%M'),
            ), tags=(tag,))
        #self.tree.update_idletasks()
        #self.tree.update()
        # Scroll to the last row
        if last_item:
            self.tree.see(last_item)
            self.tree.focus(last_item)
            self.tree.selection_set(last_item)


    def update_data_items(self, txt = ""):
        if self.main_window.selected_type_option == 0:
            self.update_txt_data_items(txt)
        else:
            self.update_img_data_items(txt)


    def get_tag(self, index):
        return 'odd' if index % 2 == 0 else 'even'

    def on_mouse_move(self, event):
        # Get the item under the mouse
        item = self.tree.identify_row(event.y)

        # Reset background and foreground colors for all items
        for row in self.tree.get_children():
            tag = self.get_tag(self.tree.index(row))
            self.tree.item(row, tags=(tag,))

        if item:
            # Highlight the hovered item
            self.tree.item(item, tags=('hover',))

    def add_item(self, record, index):
        prompt = record.describe
        item = None
        try:
            img_path = record.img_path
            img = Image.open(img_path)
            img = resize_image(img, (80, 80))
            img_tk = ImageTk.PhotoImage(img)
            tag = self.get_tag(index)
            item = self.tree.insert("", tk.END, text="", image=img_tk,
                             values=(
                                 record.id,
                                 "",
                                 "",
                                 record.describe,
                                 record.img_path,
                                 record.create_time.strftime('%Y-%m-%d %H:%M'),
                             ), tags=(tag,))

            self.image_list.append(img_tk)

        except Exception as e:
            print(f"Error adding item with image {prompt}: {e}")
        return item

    def set_img_style(self):

        # 设置 Treeview 标题的样式
        self.style.configure('List.Treeview.Heading',
                        borderwidth=0,  # 设置边框宽度为 0
                        relief='flat',  # 设置为平面样式
                        padding=(10, 20, 10, 20),
                        font=('Helvetica', 15, 'bold'),
                        background='#f0f0f0',  # 标题背景颜色与内容行保持一致
                        foreground='#232323'  # 标题字体颜色为白色
                        )
        self.configure_styles()
        self.style.configure('List.Treeview',
                        rowheight=100, font=("Arial", 12),
                        padding=(5, 10, 5, 10),
                        fieldbackground = 'white',
                        bordercolor = '#cccccc',  # 设置列之间的竖线颜色
                        borderwidth = 10,
                        highlightthickness=1,  # 设置高亮边框厚度
                        bd=1,  # 设置边框宽度
                        #relief = 'solid'  # 使用 solid 来显示边框
                             )

        self.tree["show"] = "tree headings"
        self.tree["displaycolumns"] = ("prompt", "create_time")
        #self.set_column_width(self.main_window.output_frame)


    def set_txt_style(self, clean = True):
        self.configure_styles()
        # 设置 Treeview 标题的样式
        self.style.configure('List.Treeview.Heading',
                             borderwidth=0,  # 设置边框宽度为 0
                             relief='flat',  # 设置为平面样式
                             padding=(10, 10, 10, 10),
                             font=('Helvetica', 15, 'bold'),
                             background='#f0f0f0',  # 标题背景颜色与内容行保持一致
                             foreground='#232323'  # 标题字体颜色为白色
                             )
        self.style.configure('List.Treeview',
                             rowheight=50, font=("Arial", 12),
                             padding=(5, 10, 5, 10),
                             fieldbackground='white',
                             bordercolor='#cccccc',  # 设置列之间的竖线颜色
                             borderwidth=1,
                             #relief='solid'  # 使用 solid 来显示边框
                             )
        self.tree["show"] = "headings"
        self.tree["displaycolumns"] = ("prompt", "content", "create_time")
        self.style.configure("List.Treeview", font=("Arial", 12))  # 设置字体为 Arial, 大小为 12
        #self.set_column_width(self.main_window.output_frame)


    def update_img_data_items(self, txt, selected_content_hierarchy_child_id = None):
        self.set_img_style()
        self.clear_treeview()
        self.image_list.clear()
        records = record_manager.load_img_records(txt, selected_content_hierarchy_child_id)
        index = 0
        for record in records:
            self.add_item(record, index)
            index += 1
        self.tree.update_idletasks()  # Force update to ensure styles are applied
        self.tree.update()
        children = self.tree.get_children()
        if len(children) == 0:
            return
        last_item = self.tree.get_children()[-1]
        # Scroll to the last row
        self.tree.see(last_item)

    def insert_img_data_item(self, content_id):
        self.set_img_style()
        records = record_manager.load_img_records(content_id=content_id)
        index = 0
        last_item = None
        for record in records:
            last_item = self.add_item(record, index)
            index += 1
        #self.tree.update_idletasks()  # Force update to ensure styles are applied
        #self.tree.update()
        # Scroll to the last row
        if last_item:
            self.tree.see(last_item)
            self.tree.focus(last_item)
            self.tree.selection_set(last_item)

    def add_buttons_to_tree_item(self, root):
        # 移除之前添加的按钮
        for widget in root.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.destroy()

        tree_width = self.tree.winfo_width()
        tree_height = self.tree.winfo_height()

        # 获取每列的宽度
        column_widths = {col: self.tree.column(col, "width") for col in self.tree["columns"]}

        # 遍历所有条目，为每条目添加按钮
        for item in self.tree.get_children():
            # 获取最后一列的宽度
            last_column = self.tree["columns"][-1]
            last_bbox = self.tree.bbox(item, column=last_column)

            if last_bbox:
                x1, y1, x2, y2 = last_bbox
                # 计算按钮的 x 坐标
                button_x = x2/2 + x1 - 10  # 在列的右边缘右移 10 像素

                # 计算按钮的 y 坐标以垂直居中
                row_height = y2
                button_height = 30  # 按钮的高度
                button_y = y1 + (row_height - button_height) / 2 + button_height/2

                button_width = 80  # 按钮的宽度
                if button_x + button_width > tree_width:
                    button_x = tree_width - button_width

                # 确保按钮不会超出树的下边界
                if button_y + button_height > tree_height:
                    continue

                button = ttk.Button(root, text="Button", command=lambda i=item: self.on_button_click(i))
                button.place(x=button_x, y=button_y, anchor="nw")



    def set_column_width(self, output_frame):
        frame_width = output_frame.winfo_width()
        num_columns = len(self.tree["columns"])
        if num_columns > 0:
            # 设置列宽
            column_width = frame_width // num_columns
            self.tree.column("#0", width=100)  # 固定宽度的列
            for col in self.tree["columns"]:
                if col != "#0":
                    self.tree.column(col, width=column_width)

        self.tree.update_idletasks()  # Force update to ensure styles are applied
        self.tree.update()

    def on_tree_resize(self, event):
        # 处理 Treeview 调整时的事件
        self.add_buttons_to_tree_item(self.main_window.root)


    def on_button_click(self, index):
        print(f"Button clicked for item {index}")

    def clear_treeview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)


