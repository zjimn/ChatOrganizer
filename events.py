import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import requests
from io import BytesIO
from enum import Enum
import math
import record_manager
from config import TYPE_OPTION_KEY, IMG_SIZE_OPTION_KEY
from record_manager import load_txt_records
from enums import ViewType
from image_completion import create_image_from_text
from system_config import SystemConfig
from text_completion import generate_gpt_completion
from datetime import datetime
from typing import Optional
from PIL import Image, ImageDraw, ImageTk, ImageFont
from data_management import DataManagement  # Import the class
from pathlib import Path

from db.config_data_access import ConfigDataAccess


class EventManager:
    def __init__(self, root, main_window, config_data_access, system_config):
        self.root = root
        self.system_config = system_config
        self.main_window = main_window
        self.config_data_access = config_data_access
        self.original_image: Optional[Image.Image] = None
        self.photo_image = None
        self.zoom_level = 1.0
        self.session_id = None
        self.update_option()
        self.bind_events()
        root.update_idletasks()
        self.center_window()
        root.update_idletasks()
        self.set_output_window_pos()
    def save_image(self, main_window, image, root):
        # 获取当前日期和时间，格式化为文件名
        default_filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.png")

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            initialfile=default_filename,  # 设置默认文件名
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if file_path and image:
            try:
                prompt = main_window.input_text.get()
                db_file_path = Path(self.system_config.get("image_dir_path")) / default_filename
                self.original_image.save(file_path)
                record_manager.save_img_record(prompt, db_file_path)
            except Exception as e:
                print(f"Failed to save image: {e}")

    def on_right_click(self, event,main_window, image_url, root):
        menu = tk.Menu(root, tearoff=0)
        menu.add_command(
            label="保存图片",
            command=lambda: self.save_image(main_window, image_url, root)
        )
        menu.post(event.x_root, event.y_root)


    def show_image(self, main_window, url, root):
        main_window.output_window.deiconify()  # 弹出窗口
        # Show Canvas
        main_window.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        main_window.output_image.pack(fill=tk.BOTH, expand=True, padx=0, pady=(40, 0))
        main_window.output_text.pack_forget()
        main_window.canvas.delete("all")
        try:
            # 下载并加载新图像
            response = requests.get(url)
            image_data = BytesIO(response.content)
            self.original_image = Image.open(image_data)
            # 更新图像
            self.update_image(main_window.output_image)
            # 绑定右键点击事件
            main_window.output_image.bind("<Button-3>", lambda event: self.on_right_click(event, main_window, url, root))
            print(f"in load image:")
        except Exception as e:
            print(f"Failed to load image: {e}")


    def show_image_by_path(self, main_window, img_path, root):
        main_window.output_window.deiconify()  # 弹出窗口
        # Show Canvas
        main_window.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        main_window.output_image.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)  # Show image
        main_window.output_text.pack_forget()
        main_window.canvas.delete("all")
        try:
            # 下载并加载新图像
            self.original_image = Image.open(img_path)
            # 更新图像
            self.update_image(main_window.output_image)
            main_window.output_image.place(x=0, y=40, relwidth=1, relheight=0.8)  # 调整Label的位置和大小

        except Exception as e:
            print(f"Failed to load image: {e}")


    def update_image(self, label):

        if self.original_image:
            # 根据缩放级别调整图像大小
            if self.zoom_level <= 0:
                self.zoom_level = 0.01
            if self.zoom_level > 10:
                self.zoom_level = 10
            new_size = (
                math.ceil(self.original_image.width * self.zoom_level),
                math.ceil(self.original_image.height * self.zoom_level)
            )
            resized_image = self.original_image.resize(new_size, Image.Resampling.LANCZOS)
            photo_image = ImageTk.PhotoImage(resized_image)

            label.config(image=photo_image)
            label.photo = photo_image

    def show_text(self, main_window, txt, root):
        """显示生成的文本内容。"""
        main_window.output_window.deiconify()  # 弹出窗口

        scrollbar_width = 15
        main_window.canvas.place(
            relx=1.0,  # Right edge of the parent window
            rely=0.0,  # Top edge of the parent window
            anchor='ne',  # North-east corner of the canvas
            x=-10 - scrollbar_width,  # Offset from the right edge (10 pixels margin minus scrollbar width)
            y=0,  # Offset from the top edge (20 pixels margin)
            width=100,  # Set width of the canvas
            height=50  # Set height of the canvas
        )

        main_window.output_image.pack_forget()
        main_window.output_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(40, 0))
        main_window.output_text.config(state=tk.NORMAL)  # 禁止编辑
        main_window.output_text.delete(1.0, tk.END)  # Clear the text box
        main_window.output_text.insert(tk.END, txt)
        main_window.output_text.config(state=tk.DISABLED)

    def get_scrollbar_width(self, main_window):
        scrollbars = [w for w in main_window.output_text.winfo_children() if isinstance(w, tk.Scrollbar)]
        if scrollbars:
            return scrollbars[0].winfo_width()

    def show_tree(self, main_window):
        view_type = main_window.view_type

        data_manager = DataManagement(main_window)
        if view_type == ViewType.TXT:
            data_manager.set_column_width(main_window.output_frame)
            data_manager.update_txt_data_items()
        elif view_type == ViewType.IMG:
            data_manager.set_column_width(main_window.output_frame)
            data_manager.update_img_data_items()
        main_window.data_manager = data_manager

    def on_submit(self, main_window, root):
        """处理提交按钮的点击事件。"""
        prompt = main_window.input_text.get().strip()
        option = main_window.option_var.get()
        selected_size = main_window.size_var.get()  # 获取选定的图像尺寸
        main_window.output_window.deiconify()  # 弹出窗口
        if not prompt:
            return
        if option == "图片":
            image_data = create_image_from_text(prompt, selected_size, 1)
            url = image_data[0]  # 从返回的数据中提取 URL
            self.show_image(main_window, url, root)
            filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.png")
            file_path = Path(self.system_config.get("image_dir_path")) / filename
            self.original_image.save(file_path)
            record_manager.save_img_record(prompt, str(file_path))
        else:
            answer = generate_gpt_completion(prompt)
            self.show_text(main_window, answer, root)
            prompt = main_window.input_text.get()
            record_manager.save_txt_record(prompt, answer)


    def on_type_option_change(self):
        self.update_option()
        """处理下拉列表选择变化事件。"""
        if self.main_window.option_var.get() == "图片":
            self.show_tree(self.main_window)
            self.config_data_access.upsert_config(TYPE_OPTION_KEY, 1)
        else:
            self.show_tree(self.main_window)
            self.config_data_access.upsert_config(TYPE_OPTION_KEY, 0)


    def update_option(self):
        if self.main_window.option_var.get() == "图片":
            self.main_window.view_type = ViewType.IMG
            self.main_window.size_menu.pack(side=tk.RIGHT, padx=5, pady=(0, 15))
        else:
            self.main_window.view_type = ViewType.TXT
            self.main_window.size_menu.pack_forget()  # 隐藏尺寸下拉列表

    def center_window(self):
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        # 获取屏幕的宽度和高度
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # 计算窗口的 x 和 y 坐标，使其在屏幕中心
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        # 设置窗口的大小和位置
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def set_output_window_pos(self):
        width = self.root.winfo_width()
        height = self.root.winfo_height()

        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()

        # 获取屏幕的宽度和高度
        window_width = self.main_window.output_window.winfo_width()
        window_height = self.main_window.output_window.winfo_width()

        # 计算窗口的 x 和 y 坐标，使其在屏幕中心
        x = root_x + width
        y = root_y

        # 设置窗口的大小和位置
        self.main_window.output_window.geometry(f"{window_width}x{window_height}+{x+5}+{y}")

    def on_size_option_change(self):
        """处理下拉列表选择变化事件。"""
        size_options = ["1024x1024", "1792x1024", "1024x1792"]
        for index, option in enumerate(size_options):
            if self.main_window.size_var.get() == option:
                self.config_data_access.upsert_config(IMG_SIZE_OPTION_KEY, index)
                break


    def on_key_press(self, event, submit_button):
        """处理键盘按下事件，触发按钮点击事件并调用 on_submit。"""
        if event.keysym == 'Return':
            submit_button.state(['pressed'])  # 按钮按下状态
            # 调用 on_submit 函数

    def on_key_release(self, event, main_window, root):
        """处理键盘按下事件，触发按钮点击事件并调用 on_submit。"""
        if event.keysym == 'Return':
            main_window.submit_button.state(['!pressed'])  # 取消按钮按下状态
            self.on_submit(main_window, root)


    def on_mouse_wheel(self, event, label):

        if event.num == 4 or event.delta > 0:  # Scroll up
            self.zoom_level *= 1.1
        elif event.num == 5 or event.delta < 0:  # Scroll down
            self.zoom_level /= 1.1

        self.update_image(label)

    def adjust_option_menu_width(self):
        """调整下拉列表宽度以匹配提交按钮的宽度。"""
        button_width = self.main_window.submit_button.winfo_width()
        self.main_window.option_menu.config(width=button_width // 10)  # 估算宽度基于字符数

    def update_column_widths(self, tree):
        total_width = tree.winfo_width()
        num_columns = len(tree["columns"])
        if num_columns > 0:
            column_width = total_width // num_columns
            for col in tree["columns"]:
                tree.column(col, width=column_width)

    def on_resize(self, event, main_window):
        """处理窗口调整事件，调整下拉列表宽度。"""
        self.adjust_option_menu_width()
        self.update_column_widths(main_window.tree)


    def on_item_double_click(self, event, main_window, root):
        item = main_window.tree.selection()[0]  # Get the selected item
        values = main_window.tree.item(item, 'values')  # Get the values of the selected item
        #show_text(main_window, values[0], root)

        if main_window.view_type == ViewType.TXT:
            self.show_text(main_window, values[2], root)
        elif main_window.view_type == ViewType.IMG:
            self.show_image_by_path(main_window, values[2], root)

    def on_close_output_window(self):
        self.main_window.output_window.withdraw()

    def bind_mouse_wheel(self, event):
        # 鼠标进入时绑定滚轮事件
        self.main_window.output_image.bind("<MouseWheel>", lambda e: self.on_mouse_wheel(e, self.main_window.output_image))

    def unbind_mouse_wheel(self, event):
        # 鼠标离开时解绑滚轮事件
        self.main_window.output_image.unbind("<MouseWheel>")


    def bind_events(self):
        # 绑定事件
        self.root.bind("<Configure>", lambda e: self.on_resize(e, self.main_window))
        self.main_window.option_var.trace("w", lambda *args: self.on_type_option_change())
        self.main_window.size_var.trace("w", lambda *args: self.on_size_option_change())
        self.root.bind("<KeyPress>", lambda event: self.on_key_press(event, self.main_window.submit_button))

        self.main_window.output_window.protocol("WM_DELETE_WINDOW", self.on_close_output_window)

        self.root.bind("<KeyRelease>", lambda e: self.on_key_release(e, self.main_window, self.root))
        # 绑定鼠标滚轮事件到目标区域
        self.main_window.output_image.bind("<Enter>", self.bind_mouse_wheel)
        self.main_window.output_image.bind("<Leave>", self.unbind_mouse_wheel)
        self.main_window.submit_button.config(command=lambda: self.on_submit(self.main_window, self.root))

        # Bind double-click event to Treeview
        self.main_window.tree.bind("<Double-1>", lambda event: self.on_item_double_click(event, self.main_window, self.root))
