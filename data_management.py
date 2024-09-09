import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import record_manager


class DataManagement():
    def __init__(self, main_window):
        # Create Treeview
        self.tree = main_window.tree
        self.main_window = main_window
        # Initialize style and image list
        self.style = ttk.Style()
        self.image_list = []
        self.bind_events()

    def configure_styles(self):
        # 设置 Treeview 标题的悬停和点击样式
        self.style.map('Treeview.Heading',
                  background=[('active', '#005f9e'),  # 鼠标悬停时的背景颜色
                              ('pressed', '#004080')],  # 点击时的背景颜色
                  foreground=[('active', 'white'),  # 鼠标悬停时的字体颜色
                              ('pressed', 'white')]  # 点击时的字体颜色
                  )
        self.style.configure('Treeview', background='blue', foreground='white')
        self.style.map('Treeview', background=[('selected', '#add8e6')])
        self.style.map('Treeview', foreground=[('selected', 'white')])

        # Configure tags for row colors
        self.tree.tag_configure('odd', background='#f0f0f0', foreground='#505050')
        self.tree.tag_configure('even', background='white', foreground='#505050')
        self.tree.tag_configure('hover', background='#e6e6e6', foreground='#505050')

    def bind_events(self):
        self.tree.bind("<Motion>", self.on_mouse_move)
        # 绑定列宽度变化事件
        self.tree.bind('<Configure>', self.on_tree_resize)

    def update_txt_data_items(self, output_frame):
        self.set_txt_style()
        records = record_manager.load_txt_records()
        for index, record in enumerate(records):
            tag = self.get_tag(index)
            self.tree.insert("", tk.END, values=(
                record["prompt"],
                "",
                record["content"],
                record["create_time"]
            ), tags=(tag,))
        self.tree.update_idletasks()
        self.tree.update()


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
        prompt = record["prompt"]
        item = None
        try:
            img_path = record["img"]
            img = Image.open(img_path)
            img = img.resize((80, 80), Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            tag = self.get_tag(index)
            item = self.tree.insert("", tk.END, text="", image=img_tk,
                             values=(
                                 record["prompt"],
                                 "",
                                 record["img"],
                                 record["create_time"]
                             ), tags=(tag,))

            self.image_list.append(img_tk)

        except Exception as e:
            print(f"Error adding item with image {prompt}: {e}")
        return item

    def set_img_style(self):

        # 设置 Treeview 标题的样式
        self.style.configure('Treeview.Heading',
                        padding=(0, 20, 0, 20),
                        font=('Helvetica', 15, 'bold'),
                        background='#f0f0f0',  # 标题背景颜色与内容行保持一致
                        foreground='#232323'  # 标题字体颜色为白色
                        )
        self.configure_styles()
        self.style.configure('Treeview',
                        rowheight=100, font=("Arial", 12),
                        fieldbackground = 'white',
                        bordercolor = '#cccccc',  # 设置列之间的竖线颜色
                        borderwidth = 10,
                        highlightthickness=1,  # 设置高亮边框厚度
                        bd=1,  # 设置边框宽度
                        #relief = 'solid'  # 使用 solid 来显示边框
                             )

        self.tree["show"] = "tree headings"
        self.tree["displaycolumns"] = ("prompt", "create_time", "operation")
        self.set_column_width(self.main_window.output_frame)
        self.clear_treeview()
        self.image_list.clear()


    def set_txt_style(self):
        self.configure_styles()
        # 设置 Treeview 标题的样式
        self.style.configure('Treeview.Heading',
                             borderwidth=0,  # 设置边框宽度为 0
                             relief='flat',  # 设置为平面样式
                             padding=(0, 10, 0, 10),
                             font=('Helvetica', 15, 'bold'),
                             background='#f0f0f0',  # 标题背景颜色与内容行保持一致
                             foreground='#232323'  # 标题字体颜色为白色
                             )
        self.style.configure('Treeview',
                             rowheight=50, font=("Arial", 12),
                             fieldbackground='white',
                             bordercolor='#cccccc',  # 设置列之间的竖线颜色
                             borderwidth=1,
                             #relief='solid'  # 使用 solid 来显示边框
                             )
        self.tree["show"] = "headings"
        self.tree["displaycolumns"] = ("prompt", "content", "create_time", "operation")
        self.style.configure("Treeview", font=("Arial", 12))  # 设置字体为 Arial, 大小为 12
        self.set_column_width(self.main_window.output_frame)
        self.clear_treeview()

    def update_img_data_items(self, output_frame):
        self.set_img_style()
        records = record_manager.load_img_records()
        index = 0
        for record in records:
            item = self.add_item(record, index)
            index += 1
        self.tree.update_idletasks()  # Force update to ensure styles are applied
        self.tree.update()
        self.add_buttons_to_tree_item(self.main_window.root)

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
            else:
                print(f"Bounding box not found for item {item} in column {last_column}")



    def set_column_width(self, output_frame):
        frame_width = output_frame.winfo_width()
        num_columns = len(self.tree["columns"])
        if num_columns > 0:
            # 设置列宽
            column_width = frame_width // num_columns
            self.tree.column("#0", width=200)  # 固定宽度的列
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