import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import requests
from io import BytesIO
from enum import Enum
import math

import config
import record_manager
import system_config
from config import TYPE_OPTION_KEY, IMG_SIZE_OPTION_KEY
from image_completion import ImageGenerator
from record_manager import load_txt_records
from enums import ViewType
import text_completion
import image_completion
from system_config import SystemConfig
from datetime import datetime
from typing import Optional
from PIL import Image, ImageDraw, ImageTk, ImageFont
from data_management import DataManagement  # Import the class
from pathlib import Path
import util.token_management

from db.config_data_access import ConfigDataAccess
from util.token_management import TokenManager


class EventManager:
    def __init__(self, root, main_window, config_data_access, system_config):
        self.focus_dialog_index = None
        self.dialog_frames = []
        self.dialog_labels = []
        self.zoom_levels = []
        self.dialog_images = []
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
        self.token_management = TokenManager()
        self.img_generator = ImageGenerator()
        self.txt_generator = text_completion.TextGenerator()

    def save_image(self, image):
        # 获取当前日期和时间，格式化为文件名
        default_filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.png")

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            initialfile=default_filename,  # 设置默认文件名
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if file_path and image:
            try:
                image.save(file_path)
            except Exception as e:
                print(f"Failed to save image: {e}")

    def on_right_click(self, event, image):
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(
            label="保存图片",
            command=lambda: self.save_image(image)
        )
        menu.post(event.x_root, event.y_root)


    def show_image(self, main_window, url, root):
        main_window.output_window.deiconify()  # 弹出窗口
        # Show Canvas
        main_window.output_window_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        main_window.output_image.pack(fill=tk.BOTH, expand=True, padx=0, pady=(40, 0))
        main_window.output_text.pack_forget()
        main_window.output_window_canvas.delete("all")
        try:
            # 下载并加载新图像
            response = requests.get(url)
            image_data = BytesIO(response.content)
            self.original_image = Image.open(image_data)
            # 更新图像
            self.update_dialog_images(main_window.output_image)
            # 绑定右键点击事件
            main_window.output_image.bind("<Button-3>", lambda event: self.on_right_click(event, main_window, url, root))
            print(f"in load image:")
        except Exception as e:
            print(f"Failed to load image: {e}")


    def show_image_by_path(self, main_window, img_path, root):
        main_window.output_window.deiconify()  # 弹出窗口
        # Show Canvas
        main_window.output_window_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        main_window.output_image.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)  # Show image
        main_window.output_text.pack_forget()
        main_window.output_window_canvas.delete("all")
        try:
            # 下载并加载新图像
            self.original_image = Image.open(img_path)
            # 更新图像
            self.update_dialog_images(main_window.output_image)
            main_window.output_image.place(x=0, y=40, relwidth=1, relheight=0.8)  # 调整Label的位置和大小

        except Exception as e:
            print(f"Failed to load image: {e}")

    def show_text(self, main_window, txt, append = False):
        """显示生成的文本内容。"""
        main_window.output_window.deiconify()  # 弹出窗口
        self.main_window.output_window_scrollbar.pack_forget()
        self.main_window.output_window_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        #self.main_window.output_window_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.clear_output_window_canvas_data()
        main_window.output_image.pack_forget()
        main_window.output_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 15))
        main_window.output_text.config(state=tk.NORMAL)  # 禁止编辑
        if not append:
            main_window.output_text.delete(1.0, tk.END)  # Clear the text box
        else:
            # Scroll to the end of the text
            main_window.output_text.yview(tk.END)
        main_window.output_text.insert(tk.END, txt)
        main_window.output_text.config(state=tk.DISABLED)

    def get_scrollbar_width(self, main_window):
        scrollbars = [w for w in main_window.output_text.winfo_children() if isinstance(w, tk.Scrollbar)]
        if scrollbars:
            return scrollbars[0].winfo_width()

    def show_tree(self):
        view_type = self.main_window.view_type
        txt = self.main_window.search_input_text.get()
        data_manager = DataManagement(self.main_window)
        if view_type == ViewType.TXT:
            data_manager.set_column_width(self.main_window.output_frame)
            data_manager.update_txt_data_items(txt)
        elif view_type == ViewType.IMG:
            data_manager.set_column_width(self.main_window.output_frame)
            data_manager.update_img_data_items(txt)
        self.main_window.data_manager = data_manager

    def download_img(self, url):
        response = requests.get(url)
        image_data = BytesIO(response.content)
        return Image.open(image_data)

    def on_submit(self, main_window, root):
        """处理提交按钮的点击事件。"""
        prompt = main_window.input_text.get('1.0', 'end-1c').strip()
        option = main_window.option_var.get()
        selected_size = main_window.size_var.get()  # 获取选定的图像尺寸
        main_window.output_window.deiconify()  # 弹出窗口
        if not prompt:
            return
        if option == "图片":
            image_data = self.img_generator.create_image_from_text(prompt, selected_size, 1, self.session_id is None)
            url = image_data[0]  # 从返回的数据中提取 URL
            #self.show_image(main_window, url, root)
            filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.png")
            file_path = Path(self.system_config.get("image_dir_path")) / filename
            img = self.download_img(url)
            img.save(file_path)

            self.session_id = record_manager.save_img_record(self.session_id, prompt, str(file_path))

            dialogs = record_manager.load_img_dialogs(self.session_id)
            self.set_dialog_images(dialogs)
            self.show_tree()

        else:
            answer = self.txt_generator.generate_gpt_completion(prompt, self.session_id is None)
            prompt = main_window.input_text.get('1.0', 'end-1c')
            content = f"\n{config.USER_NAME}: {prompt}\n"
            content += f"\n{config.ASSISTANT_NAME}: {answer}\n"
            self.show_text(main_window, content, True)
            self.session_id = record_manager.save_txt_record(self.session_id, prompt, answer)
            self.show_tree()

    def clear_output_window_canvas_data(self):
        if self.dialog_labels is None:
            return
        # 清除所有图片和文本
        for label in self.dialog_labels:
            label.config(image=None)
        for frame in self.dialog_frames:
            frame.destroy()  # 销毁包含图片和文本的 Frame
        self.dialog_images.clear()
        self.zoom_levels.clear()
        self.dialog_labels.clear()
        self.dialog_frames.clear()
        self.focus_dialog_index = None

    def set_dialog_images(self, data):
        self.main_window.output_text.pack_forget()
        self.main_window.output_window_canvas.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        self.main_window.output_window.deiconify()  # 弹出窗口
        self.main_window.output_window_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.clear_output_window_canvas_data()
        # 创建显示区域的 Frame
        for item in data:
            image_path = item.img_path
            height = 400
            is_img = True
            if image_path is None or image_path == "":
                is_img = False
                height = 50

            frame = tk.Frame(self.main_window.output_window_scrollbar_frame, width=600, height=height)
            #frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            frame.pack_propagate(False)  # Prevent frame resizing
            frame.pack(side=tk.TOP, fill=tk.Y, padx=10, pady=10)


            txt = f"{item.role}: {item.message}\n"
            text_label = tk.Label(frame, text=txt, font=('Arial', 12, 'bold'))
            text_label.pack(side=tk.TOP, anchor=tk.W)

            if image_path is None or image_path == "":
                continue
            img = Image.open(image_path)
          
            self.dialog_images.append(img)
            self.zoom_levels.append(1.0)  # 初始缩放级别为1.0



            img_label = tk.Label(frame)
            img_label.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

            self.dialog_labels.append(img_label)
            self.dialog_frames.append(frame)

            self.update_dialog_images(len(self.dialog_labels) - 1)
            img_label.bind("<Button-1>", self.on_click_img)
            #img_label.bind("<Button-1>", self.on_mouse_click)
            img_label.bind("<Button-3>", lambda event: self.on_right_click(event, img))

            img_label.bind("<Leave>", self.on_mouse_leave_img)

    def update_dialog_images(self, index):
        if 0 <= index < len(self.dialog_images):
            image = self.dialog_images[index]
            zoom_level = self.zoom_levels[index]

            # 根据缩放级别调整图像大小
            if zoom_level <= 0:
                zoom_level = 0.01
            if zoom_level > 10:
                zoom_level = 10
            new_size = (
                math.ceil(image.width * zoom_level),
                math.ceil(image.height * zoom_level)
            )
            resized_image = image.resize(new_size, Image.Resampling.LANCZOS)
            photo_image = ImageTk.PhotoImage(resized_image)

            label = self.dialog_labels[index]
            label.config(image=photo_image)
            label.photo = photo_image

    def on_type_option_change(self):
        self.update_option()
        """处理下拉列表选择变化事件。"""
        if self.main_window.option_var.get() == "图片":
            self.show_tree()
            self.system_config.set(TYPE_OPTION_KEY,'1')
        else:
            self.show_tree()
            self.system_config.set(TYPE_OPTION_KEY,'0')
        self.close_output_window()



    def update_option(self):
        if self.main_window.option_var.get() == "图片":
            self.main_window.view_type = ViewType.IMG
            self.main_window.size_menu.pack(side=tk.RIGHT, padx=5, pady=(0, 0), anchor=tk.S)
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
        window_height = self.main_window.output_window.winfo_height()

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
        if event.keysym == 'Return' and event.state & 0x20000 == 0:
            submit_button.state(['pressed'])  # 按钮按下状态
            # 调用 on_submit 函数

    def on_key_release(self, event, main_window, root):
        """处理键盘按下事件，触发按钮点击事件并调用 on_submit。"""
        if event.keysym == 'Return' and event.state & 0x20000 == 0:
            main_window.submit_button.state(['!pressed'])  # 取消按钮按下状态
            self.on_submit(main_window, root)


    def on_click_img(self, event):
        self.focus_dialog_index = self.dialog_labels.index(event.widget)

    def on_mouse_leave_img(self, event):
        # 当鼠标离开图片区域时，清除焦点索引
        if self.focus_dialog_index == self.dialog_labels.index(event.widget):
            self.focus_dialog_index = None

    def on_mouse_wheel(self, event):

        if self.focus_dialog_index is not None:
            # 鼠标滚轮事件处理
            if event.delta > 0:  # 向上滚动
                self.zoom_levels[self.focus_dialog_index] *= 1.1
            elif event.delta < 0:  # 向下滚动
                self.zoom_levels[self.focus_dialog_index] /= 1.1
            self.update_dialog_images(self.focus_dialog_index)

    def on_output_window_canvas_mouse_wheel(self, event):
        if self.focus_dialog_index is not None or self.system_config.get(TYPE_OPTION_KEY) == config.TYPE_OPTION_TXT_KEY: # only for img canvas and img focus
            return
        # Adjust the scroll speed by multiplying the delta value (on Windows, it's usually 120 per wheel notch)
        self.main_window.output_window_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

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
        self.session_id = values[0]
        if main_window.view_type == ViewType.TXT:
            data = record_manager.load_txt_dialogs(self.session_id)
            content = "\n".join(f"{item.role}: {item.message}\n" for item in data)
            self.token_management.clear_txt_history()
            for item in data:
                self.token_management.add_txt_message(item.role, item.message) # add session message

            self.txt_generator.token_manager = self.token_management
            self.show_text(main_window, content)
        elif main_window.view_type == ViewType.IMG:
            dialogs = record_manager.load_img_dialogs(self.session_id)
            self.token_management.clear_img_history()
            for item in dialogs:
                if item.role == "user":
                    self.token_management.add_img_message("Prompt", item.message) # add session message, only prompt, because the img url will expire
            self.img_generator.token_manager = self.token_management
            self.set_dialog_images(dialogs)


    def on_close_output_window(self):
        self.close_output_window()

    def close_output_window(self):
        self.main_window.output_window.withdraw()
        self.session_id = None
        self.token_management.clear_img_history()
        self.token_management.clear_txt_history()

    def on_text_change(self, event):
        self.main_window.input_text.edit_modified(False)
        self.root.after(100, lambda: self.main_window.input_text.see(tk.END))
        lines = self.main_window.input_text.get('1.0', 'end-1c').split('\n')
        num_lines = len(lines)
        new_height = max(num_lines, 1)
        self.main_window.input_text.config(height=new_height)

    def on_search_text_change(self, *args):
        self.main_window.input_text.edit_modified(False)
        self.show_tree()

    def on_alt_return_press(self, event):
        """处理 Alt + Return 组合键，执行回车键效果。"""
        # 插入换行符
        self.main_window.input_text.insert(tk.INSERT, "\n")
        return "break"  # 确保没有其他默认行为

    def bind_events(self):
        # 绑定事件
        self.root.bind("<Configure>", lambda e: self.on_resize(e, self.main_window))
        self.main_window.option_var.trace("w", lambda *args: self.on_type_option_change())
        self.main_window.size_var.trace("w", lambda *args: self.on_size_option_change())
        self.root.bind("<KeyPress>", lambda event: self.on_key_press(event, self.main_window.submit_button))

        self.main_window.output_window.protocol("WM_DELETE_WINDOW", self.on_close_output_window)

        self.root.bind("<KeyRelease>", lambda e: self.on_key_release(e, self.main_window, self.root))

        self.main_window.submit_button.config(command=lambda: self.on_submit(self.main_window, self.root))
        self.main_window.output_window.bind("<MouseWheel>", self.on_mouse_wheel)
        # Bind double-click event to Treeview
        self.main_window.tree.bind("<Double-1>", lambda event: self.on_item_double_click(event, self.main_window, self.root))
        self.main_window.output_window_canvas.bind_all("<MouseWheel>", self.on_output_window_canvas_mouse_wheel)
        self.main_window.input_text.bind("<<Modified>>", self.on_text_change)

        # 绑定 Alt + Return 键事件到 on_alt_return_press 方法
        self.main_window.input_text.bind("<Alt-Return>", self.on_alt_return_press)

        # 禁用单独 Return 键的默认行为
        self.main_window.input_text.bind("<Return>", lambda event: "break")
        self.main_window.search_input_entry_text.trace('w', self.on_search_text_change)  # 'w' 表示监听写操作