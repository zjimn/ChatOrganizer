import threading
import tkinter as tk
from io import BytesIO
from tkinter import font as tkfont, filedialog
from datetime import datetime
from pathlib import Path
from tkinter.ttk import Label

import requests
from PIL import Image, ImageTk
import math

from api.openai_image_api import OpenaiImageApi
from api.openai_text_api import OpenaiTextApi
from config import constant
from config.app_config import AppConfig
from config.constant import TYPE_OPTION_KEY_NAME, ASSISTANT_NAME, TYPE_OPTION_TXT_KEY, \
    TYPE_OPTION_IMG_KEY
from config.enum import ViewType
from db.models import Dialogue
from event.event_bus import event_bus
from service.content_service import ContentService
from ui.input_frame import InputFrame
from util import image_util
from util.ImageViewer import ImageViewer
from util.image_util import full_cover_resize
from util.text_inserter import TextInserter
from util.window_util import center_window


class OutputManager:
    def __init__(self, root, main_window):
        self.session_id = None
        self.main_window = main_window
        self.output_window = main_window.output_window
        self.root = root
        self.app_config = AppConfig()
        self.output_window_canvas_scroll_enabled = None
        self.image_viewer = ImageViewer(self.root)
        self.focus_dialog_index = None
        self.dialog_frames = []
        self.dialog_labels = []
        self.zoom_levels = []
        self.dialog_images = []
        self.set_output_window_pos()
        self.app_config = AppConfig()
        self.img_generator = OpenaiImageApi()
        self.txt_generator = OpenaiTextApi()
        self.content_service = ContentService()
        self.selected_tree_id = None
        self.bind_events()
        self.text_inserter = TextInserter(self.root, self.main_window.output_window.output_text)

    def show_text(self, main_window, data, append = False):
        """显示生成的文本内容。"""
        main_window.output_window.output_window.deiconify()  # 弹出窗口
        self.main_window.output_window.output_window_scrollbar.pack_forget()
        self.main_window.output_window.output_window_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.clear_output_window_canvas_data()
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
        if self.app_config.get(TYPE_OPTION_KEY_NAME, '0') == TYPE_OPTION_IMG_KEY:
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

        self.main_window.input_frame.frame.event_generate('<<RequestOpenaiBegin>>')

        if self.app_config.get(TYPE_OPTION_KEY_NAME, '0') == TYPE_OPTION_IMG_KEY:
            image_data = self.img_generator.create_image_from_text(prompt, selected_size, 1, self.session_id is None)
            if image_data is None:
                return
            url = image_data[0]  # 从返回的数据中提取 URL
            #self.show_image(main_window, url, root)
            filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.png")
            file_path = Path(self.app_config.get("image_dir_path")) / filename
            img = self.download_img(url)
            img.save(file_path)
            dialogue_data = Dialogue(
                message=prompt,
                img_path=file_path
            )
            self.set_dialog_images([dialogue_data], True, True)
            self.session_id = self.content_service.save_img_record(self.session_id, self.selected_tree_id, prompt, str(file_path))

        else:
            self.set_output_text_default_background()
            answer = self.txt_generator.generate_gpt_completion(prompt, self.session_id is None)
            if answer is None:
                return
            content = f"\n{constant.DISPLAY_USER_NAME}: {prompt}\n"
            content += f"\n{constant.DISPLAY_ASSISTANT_NAME}: {answer}\n"
            self.show_text_append(self.main_window, None, answer, True)
            self.session_id = self.content_service.save_txt_record(self.session_id, self.selected_tree_id, prompt, answer)
        if show_tree:
            self.insert_tree_item(self.session_id)
        self.main_window.input_frame.frame.event_generate('<<RequestOpenaiFinished>>')

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

            img_label.bind("<Double-Button-1>", lambda e: self.image_viewer.on_image_double_click(e, image_path, self.root))

            img_label.bind("<Leave>", self.on_mouse_leave_img)

            if append:
                self.root.after(100, lambda: self.main_window.output_window.output_window_canvas.yview_moveto(1.0))

    def on_output_text_scroll_drag(self, event):
        self.text_inserter.set_follow_insert_state(False)

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

    def on_output_window_canvas_mouse_wheel(self, event):
        if not self.output_window_canvas_scroll_enabled:
            return
        if self.focus_dialog_index is not None or self.app_config.get(TYPE_OPTION_KEY_NAME) == constant.TYPE_OPTION_TXT_KEY: # only for img canvas and img focus
            return
        # Adjust the scroll speed by multiplying the delta value (on Windows, it's usually 120 per wheel notch)
        self.main_window.output_window.output_window_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_enter_output_window_canvas_canvas(self, event):
        self.output_window_canvas_scroll_enabled = True

    def on_leave_output_window_canvas_canvas(self, event):
        self.output_window_canvas_scroll_enabled = False

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


    def set_output_text_default_background(self):
        pass
        self.text_inserter.clean_bg() # clean tag to reset bg color

    def calculate_font_height(self, font_name, font_size):
        # Create a Tkinter font object
        font = tkfont.Font(family=font_name, size=font_size)
        # Return the font height
        return font.metrics("linespace")

    def on_press_tree_item(self, tree_id):

        self.selected_tree_id = tree_id
        self.close_output_window()

    def on_close_output_window(self, event = None):
        self.close_output_window()

    def close_output_window(self):
        self.main_window.output_window.output_window.withdraw()
        self.session_id = None
        self.img_generator.clear_history()
        self.txt_generator.clear_history()


    def insert_tree_item(self, content_id):
        self.main_window.display_frame.tree.data = {"content_id": content_id}
        self.main_window.display_frame.tree.event_generate('<<InsertListItem>>')

    def clear_output_window_canvas_data(self):
        if self.dialog_labels is None:
            return
        # 清除所有图片和文本
        for label in self.dialog_labels:
            label.config(image=None)
        for frame in self.dialog_frames:
            frame.destroy()
        self.dialog_images.clear()
        self.zoom_levels.clear()
        self.dialog_labels.clear()
        self.dialog_frames.clear()
        self.focus_dialog_index = None
        for widget in self.main_window.output_window.output_window_scrollbar_frame.winfo_children():
            widget.destroy()

    def on_item_double_click(self, event, main_window, root):
        selected_items = main_window.display_frame.tree.selection()
        if len(selected_items) == 0:
            return 
        item = main_window.display_frame.tree.selection()[0]  # Get the selected item
        values = main_window.display_frame.tree.item(item, 'values')  # Get the values of the selected item
        # show_text(main_window, values[0], root)
        self.session_id = values[0]
        if self.app_config.get(TYPE_OPTION_KEY_NAME, TYPE_OPTION_TXT_KEY) == TYPE_OPTION_TXT_KEY:
            self.set_output_text_default_background()
            data = self.content_service.load_txt_dialogs(self.session_id)
            self.txt_generator.clear_history()
            for item in data:
                self.txt_generator.add_history_message(item.role, item.message)  # add session message

            self.show_text(main_window, data)
        elif main_window.view_type == ViewType.IMG:
            dialogs = self.content_service.load_img_dialogs(self.session_id)
            self.img_generator.clear_history()
            for item in dialogs:
                if item.role == "user":
                    self.img_generator.add_history_message("Prompt",
                                                           item.message)  # add session message, only prompt, because the img url will expire
            self.set_dialog_images(dialogs)

    def thread_submit(self, event = None):
        threading.Thread(target=lambda: self.submit_prompt()).start()

    def cancel_request(self, event):
        if self.txt_generator:
            self.txt_generator.cancel_request()
        if self.img_generator:
            self.img_generator.cancel_request()

    def bind_events(self):
        self.output_window.output_window.protocol("WM_DELETE_WINDOW", self.on_close_output_window)
        self.output_window.output_window.bind("<MouseWheel>", self.on_mouse_wheel)
        self.output_window.output_text.vbar.bind("<B1-Motion>", lambda event: self.on_output_text_scroll_drag(event))
        self.output_window.output_text.bind("<MouseWheel>", lambda event: self.on_output_text_scroll_drag(event))
        self.output_window.output_window_canvas.bind("<Enter>", self.on_enter_output_window_canvas_canvas)
        self.output_window.output_window_canvas.bind("<Leave>", self.on_leave_output_window_canvas_canvas)
        self.output_window.output_window_canvas.bind_all("<MouseWheel>", self.on_output_window_canvas_mouse_wheel)
        #self.main_window.output_window.output_window.bind('<<TreeItemPress>>', self.on_press_tree_item)
        event_bus.subscribe('TreeItemPress', self.on_press_tree_item)
        self.main_window.display_frame.tree.bind("<Double-1>", lambda event: self.on_item_double_click(event, self.main_window, self.root))
        self.root.bind('<<SubmitRequest>>', lambda event: self.thread_submit(event))
        self.root.bind('<<CancelRequest>>', lambda event: self.cancel_request(event))
        self.root.bind('<<CloseOutputWindow>>', lambda event: self.close_output_window())
