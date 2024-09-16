import threading
import tkinter as tk
from tkinter import filedialog
import requests
from io import BytesIO
import math

from config import constant
from config.constant import TYPE_OPTION_KEY, IMG_SIZE_OPTION_KEY, ASSISTANT_NAME
from db.models import Dialogue

from config.enum import ViewType

from datetime import datetime
from typing import Optional
from PIL import Image, ImageTk
from event.list_manager import ListManager  # Import the class
from pathlib import Path
import tkinter.font as tkfont

from api.openai_image_api import OpenaiImageApi

from api.openai_text_api import OpenaiTextApi
from service.content_service import ContentService
from util.text_inserter import TextInserter
from util.image_utils import full_cover_resize
from util.token_management import TokenManager


class EventManager:
    def __init__(self, root, main_window, system_config, content_hierarchy_tree_manager):
        self.output_window_canvas_scroll_enabled = None
        self.focus_dialog_index = None
        self.dialog_frames = []
        self.dialog_labels = []
        self.zoom_levels = []
        self.dialog_images = []
        self.root = root
        self.system_config = system_config
        self.content_service = ContentService()

        self.content_hierarchy_tree_manager = content_hierarchy_tree_manager
        self.main_window = main_window
        self.original_image: Optional[Image.Image] = None
        self.photo_image = None
        self.zoom_level = 1.0
        self.session_id = None
        self.update_option()
        self.token_management = TokenManager()
        self.img_generator = OpenaiImageApi()
        self.txt_generator = OpenaiTextApi()
        self.bind_events()
        root.update_idletasks()
        self.center_window()
        root.update_idletasks()
        self.set_output_window_pos()
        self.text_inserter = TextInserter(self.root, self.main_window.output_window.output_text)

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


    def show_text(self, main_window, data, append = False):
        """显示生成的文本内容。"""
        main_window.output_window.output_window.deiconify()  # 弹出窗口
        self.main_window.output_window.output_window_scrollbar.pack_forget()
        self.main_window.output_window.output_window_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.clear_output_window_canvas_data()
        main_window.output_window.output_image.pack_forget()
        main_window.output_window.output_text.pack(fill=tk.BOTH, expand=True)
        main_window.output_window.output_text.config(state=tk.NORMAL)
        if not append:
            main_window.output_window.output_text.delete(1.0, tk.END)  # Clear the text box
        else:
            main_window.output_window.output_text.yview(tk.END)

        for index, item in enumerate(data):
            main_window.output_window.output_text.config(state=tk.NORMAL)
            role = item.role
            message = item.message
            if role == ASSISTANT_NAME:
                self.text_inserter.set_color("#ebebeb")
                self.text_inserter.insert_text_batch(f"{message}\n", 0, False)
            else:

                if index == 0:
                    user_content = f"{message}\n\n"
                else:
                    user_content = f"\n{message}\n\n"
                font = ("Helvetica", 15, "bold")
                self.text_inserter.insert_normal(user_content, font)
            main_window.output_window.output_text.config(state=tk.NORMAL)
            #self.main_window.output_window.output_text.insert(tk.END, message)



    def show_text_append(self, main_window, user_message, response_message, append = False):
        """显示生成的文本内容。"""
        main_window.output_window.output_window.deiconify()  # 弹出窗口
        self.main_window.output_window.output_window_scrollbar.pack_forget()
        self.main_window.output_window.output_window_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        #self.main_window.output_window.output_window_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.clear_output_window_canvas_data()
        main_window.output_window.output_image.pack_forget()
        main_window.output_window.output_text.pack(fill=tk.BOTH, expand=True)
        main_window.output_window.output_text.config(state=tk.NORMAL)
        if not append:
            main_window.output_window.output_text.delete(1.0, tk.END)  # Clear the text box
        else:
            # Scroll to the end of the text
            main_window.output_window.output_text.yview(tk.END)
        if main_window.output_window.output_text.get('1.0', 'end-1c') == "":
            user_content = f"{user_message}\n\n"
        else:
            user_content = f"\n{user_message}\n\n"
        response_name = f"\n{constant.DISPLAY_ASSISTANT_NAME}: \n"
        response_content = f"{response_message}\n"
        # e8f0fe
        #self.text_inserter.set_color("#e8f0fe")
        font = ("Helvetica", 15, "bold")
        #self.main_window.output_window.output_text.insert(tk.END, user_content)
        if user_message is not None:
            self.text_inserter.insert_normal(user_content, font)
        #self.main_window.output_window.output_text.insert(tk.END, response_name)
        if response_message is not None:
            self.text_inserter.set_color("#e6e6e6")
            self.text_inserter.insert_text(response_content, 1000)

        #main_window.output_text.config(state=tk.DISABLED)

    def set_output_text_default_background(self):
        pass
        self.text_inserter.clean_bg() # clean tag to reset bg color

    def show_tree(self):
        view_type = self.main_window.view_type
        txt = self.main_window.display_frame.search_input_text.get()
        data_manager = ListManager(self.root, self.main_window.display_frame.tree)
        selected_item_id = self.content_hierarchy_tree_manager.get_selected_item_id()
        if view_type == ViewType.TXT:
            data_manager.set_column_width(self.main_window.output_window.output_frame)
            data_manager.update_txt_data_items(txt, selected_item_id)
        elif view_type == ViewType.IMG:
            data_manager.set_column_width(self.main_window.output_window.output_frame)
            data_manager.update_img_data_items(txt, selected_item_id)
        self.main_window.data_manager = data_manager

    def insert_tree_item(self, content_id):
        view_type = self.main_window.view_type
        txt = self.main_window.display_frame.search_input_text.get()
        data_manager = ListManager(self.root, self.main_window.display_frame.tree)
        selected_item_id = self.content_hierarchy_tree_manager.get_selected_item_id()
        if view_type == ViewType.TXT:
            data_manager.set_column_width(self.main_window.output_window.output_frame)
            data_manager.insert_txt_data_item(content_id)
        elif view_type == ViewType.IMG:
            data_manager.set_column_width(self.main_window.output_window.output_frame)
            data_manager.insert_img_data_item(content_id)
        self.main_window.data_manager = data_manager

    def download_img(self, url):
        response = requests.get(url)
        image_data = BytesIO(response.content)
        return Image.open(image_data)

    def submit_prompt(self):
        """处理提交按钮的点击事件。"""
        prompt = self.main_window.input_frame.input_text.get('1.0', 'end-1c').strip()
        option = self.main_window.input_frame.option_var.get()
        selected_size = self.main_window.input_frame.size_var.get()  # 获取选定的图像尺寸
        self.main_window.output_window.output_window.deiconify()  # 弹出窗口
        show_tree = self.session_id is None
        if not prompt:
            return
        prompt = self.main_window.input_frame.input_text.get('1.0', 'end-1c')
        if option == "图片":
            new_data = Dialogue(
                role="user",
                message=prompt,
                img_path=None
            )
            self.set_dialog_images([new_data], True, False, self.session_id is None)
            self.root.after(100, lambda: self.main_window.output_window.output_window_canvas.yview_moveto(1.0))
        else:
            self.set_output_text_default_background()
            self.show_text_append(self.main_window, prompt, None, self.session_id is not None)
            self.main_window.output_window.output_text.yview(tk.END)
        selected_item_id = self.content_hierarchy_tree_manager.get_selected_item_id()
        self.set_prompt_input_focus()
        self.main_window.input_frame.input_text.delete('1.0', tk.END)
        if option == "图片":
            image_data = self.img_generator.create_image_from_text(prompt, selected_size, 1, self.session_id is None)
            if image_data is None:
                return
            url = image_data[0]  # 从返回的数据中提取 URL
            #self.show_image(main_window, url, root)
            filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.png")
            file_path = Path(self.system_config.get("image_dir_path")) / filename
            img = self.download_img(url)
            img.save(file_path)
            dialogue_data = Dialogue(
                message=prompt,
                img_path=file_path
            )
            self.set_dialog_images([dialogue_data], True, True)
            self.session_id = self.content_service.save_img_record(self.session_id, selected_item_id, prompt, str(file_path))

        else:
            self.set_output_text_default_background()
            answer = self.txt_generator.generate_gpt_completion(prompt, self.session_id is None)
            if answer is None:
                return
            content = f"\n{constant.DISPLAY_USER_NAME}: {prompt}\n"
            content += f"\n{constant.DISPLAY_ASSISTANT_NAME}: {answer}\n"
            self.show_text_append(self.main_window, None, answer, True)
            self.session_id = self.content_service.save_txt_record(self.session_id, selected_item_id, prompt, answer)
        if show_tree:
            self.insert_tree_item(self.session_id)
        self.set_submit_button_state(True)
        self.set_prompt_input_focus()

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
        for widget in self.main_window.output_window.output_window_scrollbar_frame.winfo_children():
            widget.destroy()

    def set_dialog_images(self, data, append = False, only_img = False, first = False):

        self.main_window.output_window.output_window_canvas.yview_moveto(0)
        self.main_window.output_window.output_text.pack_forget()
        self.main_window.output_window.output_window_canvas.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        self.main_window.output_window.output_window.deiconify()  # 弹出窗口
        self.main_window.output_window.output_window_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        if first or not append:
            self.clear_output_window_canvas_data()
        # 创建显示区域的 Frame
        for index, item in enumerate(data):
            image_path = item.img_path
            frame_height = 400
            frame_width = 600
            img = None
            is_img = True
            if image_path is None or image_path == "":
                is_img = False
                frame_height = 80
            else:
                img = Image.open(image_path)
                original_width, original_height = img.size
                frame_height = (frame_width / original_width)*original_height

            frame = tk.Frame(self.main_window.output_window.output_window_scrollbar_frame, width=frame_width, height=frame_height, bg='#e8eaed')
            #frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            frame.pack_propagate(False)  # Prevent frame resizing
            frame.pack(side=tk.TOP, fill=tk.Y, padx=0, pady=10, anchor=tk.CENTER)

            txt = f"{item.message}\n"

            font_name = 'Helvetica'
            font_size = 15
            text_label = tk.Label(
                frame,
                text=txt,
                font=(font_name, font_size, 'bold'),
                bg='#e8eaed'  # Set background color
            )

            if image_path is None or image_path == "":
                font_height = self.calculate_font_height(font_name, font_size)
                vertical_offset = (frame_height + font_height) / 2
                text_label.place(relx=0.01, y=vertical_offset, anchor=tk.W)
                if append:
                    self.root.after(100, lambda: self.main_window.output_window.output_window_canvas.yview_moveto(1.0))
                continue

            img = full_cover_resize(img, (frame_width, frame_height))
            self.dialog_images.append(img)
            self.zoom_levels.append(1.0)  # 初始缩放级别为1.0

            img_label = tk.Label(frame,  bg='white')
            img_label.pack(side=tk.TOP, fill=tk.BOTH, expand=True)


            self.dialog_labels.append(img_label)
            self.dialog_frames.append(frame)

            self.update_dialog_images(len(self.dialog_labels) - 1)
            img_label.bind("<Button-1>", self.on_click_img)
            #img_label.bind("<Button-1>", self.on_mouse_click)
            img_label.bind("<Button-3>", lambda event: self.on_right_click(event, img))

            img_label.bind("<Leave>", self.on_mouse_leave_img)

            if append:
                self.root.after(100, lambda: self.main_window.output_window.output_window_canvas.yview_moveto(1.0))

    def calculate_font_height(self, font_name, font_size):
        # Create a Tkinter font object
        font = tkfont.Font(family=font_name, size=font_size)

        # Return the font height
        return font.metrics("linespace")

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

        if self.main_window.input_frame.option_var.get() == self.main_window.options[1]:
            self.show_tree()
            self.system_config.set(TYPE_OPTION_KEY,'1')
        else:
            self.show_tree()
            self.system_config.set(TYPE_OPTION_KEY,'0')
        self.close_output_window()


    def update_option(self):
        if self.main_window.input_frame.option_var.get() == self.main_window.options[1]:
            self.main_window.view_type = ViewType.IMG
            self.main_window.input_frame.size_menu.pack(side=tk.RIGHT, padx=5, pady=(0, 0), anchor=tk.S)
        else:
            self.main_window.view_type = ViewType.TXT
            self.main_window.input_frame.size_menu.pack_forget()  # 隐藏尺寸下拉列表

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
        window_width = self.main_window.output_window.output_window.winfo_width()
        window_height = self.main_window.output_window.output_window.winfo_height()

        # 计算窗口的 x 和 y 坐标，使其在屏幕中心
        x = root_x + width
        y = root_y

        # 设置窗口的大小和位置
        self.main_window.output_window.output_window.geometry(f"{window_width}x{window_height}+{x+5}+{y}")

    def on_size_option_change(self):
        """处理下拉列表选择变化事件。"""
        size_options = ["1024x1024", "1792x1024", "1024x1792"]
        for index, option in enumerate(size_options):
            if self.main_window.input_frame.size_var.get() == option:
                self.system_config.set(IMG_SIZE_OPTION_KEY, index)
                break


    def on_key_press(self, event, submit_button):
        """处理键盘按下事件，触发按钮点击事件并调用 on_submit。"""
        if event.keysym == 'Return' and event.state & 0x20000 == 0:
            submit_button.state(['pressed'])  # 按钮按下状态
            # 调用 on_submit 函数


    def on_key_release(self, event, main_window, root):
        # 打印当前状态以调试问题
        root.update_idletasks()
        """处理键盘按下事件，触发按钮点击事件并调用 on_submit。"""
        # 使用 after 方法稍微延迟状态检查，确保 Tkinter 更新完状态
        root.after(100, self.check_and_submit, event, main_window)

    def check_and_submit(self, event, main_window):
        """检查按钮状态并处理提交。"""
        s = "state"
        state = self.main_window.input_frame.submit_button["state"]
        if event.keysym == 'Return' and event.state & 0x20000 == 0 and not self.main_window.input_frame.submit_button_is_changed and str(state) == "normal":
            main_window.input_frame.submit_button.state(['!pressed'])  # 取消按钮按下状态
            self.thread_submit()

    def on_hit_submit_button(self):
        if not self.main_window.input_frame.submit_button_is_changed:
            self.thread_submit()
        else:
            if self.txt_generator:
                self.txt_generator.cancel_request()
            if self.img_generator:
                self.img_generator.cancel_request()
            self.set_submit_button_state(True)

    def set_prompt_input_focus(self):
        self.check_input_text()
        self.main_window.input_frame.input_text.focus_set()

    def thread_submit(self):
        self.set_submit_button_state(False)
        # 切换状态
        threading.Thread(target=lambda: self.submit_prompt()).start()

    def set_submit_button_state(self, init = False):
        self.main_window.input_frame.submit_button_is_changed = not init
        if init:
            # 恢复初始状态
            self.main_window.input_frame.submit_button.config(text=self.main_window.input_frame.submit_button_initial_text)
        else:
            # 改为 "⬛" 并修改样式
            self.main_window.input_frame.submit_button.config(text=self.main_window.input_frame.submit_button_changed_text)

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
        if not self.output_window_canvas_scroll_enabled:
            return
        if self.focus_dialog_index is not None or self.system_config.get(TYPE_OPTION_KEY) == constant.TYPE_OPTION_TXT_KEY: # only for img canvas and img focus
            return
        # Adjust the scroll speed by multiplying the delta value (on Windows, it's usually 120 per wheel notch)
        self.main_window.output_window.output_window_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_enter_output_window_canvas_canvas(self, event):
        self.output_window_canvas_scroll_enabled = True

    def on_leave_output_window_canvas_canvas(self, event):
        self.output_window_canvas_scroll_enabled = False

    def adjust_option_menu_width(self):
        """调整下拉列表宽度以匹配提交按钮的宽度。"""
        button_width = self.main_window.input_frame.submit_button.winfo_width()
        self.main_window.input_frame.option_menu.config(width=button_width // 10)  # 估算宽度基于字符数

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
        self.update_column_widths(main_window.display_frame.tree)


    def on_item_double_click(self, event, main_window, root):
        item = main_window.display_frame.tree.selection()[0]  # Get the selected item
        values = main_window.display_frame.tree.item(item, 'values')  # Get the values of the selected item
        #show_text(main_window, values[0], root)
        self.session_id = values[0]
        if main_window.view_type == ViewType.TXT:
            self.set_output_text_default_background()
            data = self.content_service.load_txt_dialogs(self.session_id)
            content = "\n".join(f"{item.role}: \n{item.message}\n" for item in data)
            self.txt_generator.clear_history()
            for item in data:
                self.txt_generator.add_history_message(item.role, item.message) # add session message

            self.show_text(main_window, data)
        elif main_window.view_type == ViewType.IMG:
            dialogs = self.content_service.load_img_dialogs(self.session_id)
            self.img_generator.clear_history()
            for item in dialogs:
                if item.role == "user":
                    self.img_generator.add_history_message("Prompt", item.message) # add session message, only prompt, because the img url will expire
            self.set_dialog_images(dialogs)

    def on_output_text_scroll_drag(self, event):
        self.text_inserter.set_follow_insert_state(False)

    def on_press_tree_item(self, event):
        self.close_output_window()

    def on_close_output_window(self):
        self.close_output_window()

    def close_output_window(self):
        self.main_window.output_window.output_window.withdraw()
        self.session_id = None
        self.img_generator.clear_history()
        self.txt_generator.clear_history()

    def on_text_change(self, event):
        self.main_window.input_frame.input_text.edit_modified(False)
        self.root.after(100, lambda: self.main_window.input_frame.input_text.see(tk.END))
        lines = self.main_window.input_frame.input_text.get('1.0', 'end-1c').split('\n')
        num_lines = len(lines)
        new_height = max(num_lines, 1)
        self.main_window.input_frame.input_text.config(height=new_height)

    def on_search_text_change(self, *args):
        self.main_window.input_frame.input_text.edit_modified(False)
        self.show_tree()

    def on_alt_return_press(self, event):
        """处理 Alt + Return 组合键，执行回车键效果。"""
        # 插入换行符
        self.main_window.input_frame.input_text.insert(tk.INSERT, "\n")
        return "break"  # 确保没有其他默认行为

    # Function to toggle icons on open/close event
    def toggle_folder_icon(self, event):
        # Get the currently focused item
        item_id = self.main_window.display_frame.tree.focus()
        # Check if the item is open or closed
        if self.main_window.display_frame.tree.item(item_id, 'open'):
            # Set open folder icon
            self.main_window.display_frame.tree.item(item_id, image=self.main_window.directory_tree.closed_folder_resized_icon)
        else:
            # Set closed folder icon
            self.main_window.display_frame.tree.item(item_id, image=self.main_window.directory_tree.closed_folder_resized_icon)

    def on_hierarchy_item_selected(self, event):
        selected_item_id = self.content_hierarchy_tree_manager.get_selected_item_id()
        self.show_tree()

    def on_close_main_window(self):
        for index, option in enumerate(self.main_window.options):
            if self.main_window.input_frame.option_var.get() == option:
                self.system_config.set(TYPE_OPTION_KEY,index, True)
                break
        for index, option in enumerate(self.main_window.input_frame.size_options):
            if self.main_window.input_frame.size_var.get() == option:
                self.system_config.set(IMG_SIZE_OPTION_KEY,index, True)
                break
        self.root.destroy()



    def check_input_text(self, event = None):
        # 检查 Text 小部件的内容
        if self.main_window.input_frame.input_text.get("1.0", tk.END).strip():
            self.main_window.input_frame.submit_button.config(state=tk.NORMAL)
        else:
            if not self.main_window.input_frame.submit_button_is_changed:
                self.main_window.input_frame.submit_button.config(state=tk.DISABLED)


    def bind_events(self):
        # 绑定事件
        self.root.bind("<Configure>", lambda e: self.on_resize(e, self.main_window))
        self.main_window.input_frame.option_var.trace("w", lambda *args: self.on_type_option_change())
        self.main_window.input_frame.size_var.trace("w", lambda *args: self.on_size_option_change())
        self.root.bind("<KeyPress>", lambda event: self.on_key_press(event, self.main_window.input_frame.submit_button))

        self.main_window.output_window.output_window.protocol("WM_DELETE_WINDOW", self.on_close_output_window)

        self.root.bind("<KeyRelease>", lambda e: self.on_key_release(e, self.main_window, self.root))


        self.main_window.input_frame.submit_button.config(command=lambda: self.on_hit_submit_button())
        self.main_window.output_window.output_window.bind("<MouseWheel>", self.on_mouse_wheel)
        # Bind double-click event to Treeview
        self.main_window.display_frame.tree.bind("<Double-1>", lambda event: self.on_item_double_click(event, self.main_window, self.root))
        self.main_window.output_window.output_window_canvas.bind_all("<MouseWheel>", self.on_output_window_canvas_mouse_wheel)
        self.main_window.input_frame.input_text.bind("<<Modified>>", self.on_text_change)

        # 绑定 Alt + Return 键事件到 on_alt_return_press 方法
        self.main_window.input_frame.input_text.bind("<Alt-Return>", self.on_alt_return_press)

        # 禁用单独 Return 键的默认行为
        self.main_window.input_frame.input_text.bind("<Return>", lambda event: "break")
        self.main_window.display_frame.search_input_entry_text.trace('w', self.on_search_text_change)  # 'w' 表示监听写操作


        # Bind event to toggle icons when items are opened or closed
        self.main_window.directory_tree.tree.bind('<<TreeviewOpen>>', self.toggle_folder_icon)
        self.main_window.directory_tree.tree.bind('<<TreeviewClose>>', self.toggle_folder_icon)

        self.main_window.directory_tree.tree.bind("<<TreeviewSelect>>", self.on_hierarchy_item_selected)
        self.main_window.directory_tree.tree.bind('<<TreeItemPress>>', self.on_press_tree_item)
        self.main_window.output_window.output_text.vbar.bind("<B1-Motion>", lambda event: self.on_output_text_scroll_drag(event))
        self.main_window.output_window.output_text.bind("<MouseWheel>", lambda event: self.on_output_text_scroll_drag(event))
        self.root.protocol("WM_DELETE_WINDOW", self.on_close_main_window)
        self.main_window.output_window.output_window_canvas.bind("<Enter>", self.on_enter_output_window_canvas_canvas)
        self.main_window.output_window.output_window_canvas.bind("<Leave>", self.on_leave_output_window_canvas_canvas)

        # 绑定 Text 小部件的事件
        self.main_window.input_frame.input_text.bind("<KeyRelease>", self.check_input_text)
        self.root.bind('<<SubmitRequest>>', self.thread_submit)
