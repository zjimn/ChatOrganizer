import math
import threading
import time
import tkinter as tk
from datetime import datetime
from io import BytesIO
from pathlib import Path
from tkinter import font as tkfont, filedialog, messagebox
import requests
from PIL import Image, ImageTk

from config import constant
from config.constant import LAST_TYPE_OPTION_KEY_NAME, ASSISTANT_NAME, TYPE_OPTION_TXT_KEY, \
    TYPE_OPTION_IMG_KEY
from db.models import Dialogue
from event.event_bus import event_bus
from exception.chat_request_error import ChatRequestError
from exception.chat_request_warn import ChatRequestWarn
from util.text_highlighter import TextHighlighter
from widget.loading_spinner import LoadingSpinner
from util.cancel_manager import CancelManager
from util.chat_factory import ChatFactory
from util.config_manager import ConfigManager
from util.logger import logger
from service.content_service import ContentService
from util.image_viewer import ImageViewer
from util.image_util import full_cover_resize
from util.text_inserter import TextInserter
from widget.custom_confirm_dialog import CustomConfirmDialog


class OutputManager:
    def __init__(self, main_window):
        self.saved_geometry = None
        self.last_click_item_time = None
        self.session_id = None
        self.inited = False
        self.main_window = main_window
        self.output_window = main_window.output_window
        self.root = main_window.root
        self.config_manager = ConfigManager()
        self.output_window_canvas_scroll_enabled = None
        self.image_viewer = ImageViewer(self.root)
        self.focus_dialog_index = None
        self.dialog_frames = []
        self.dialog_labels = []
        self.zoom_levels = []
        self.dialog_images = []
        self.sys_messages = []
        self.set_output_window_pos()
        self.chat_factory = ChatFactory()
        self.content_service = ContentService()
        self.selected_tree_id = None
        self.bind_events()
        self.text_inserter = TextInserter(self.root, self.main_window.output_window.output_text)
        self.text_highlighter = TextHighlighter(self.main_window.output_window.output_text)
        self.reload_model()
        self.loading_spinner = LoadingSpinner(main_window.output_window.output_window)
        self.open_item_thread_ids = []

    def reload_model(self):
        event_bus.publish("ReloadDialogModel")

    def show_text(self, main_window, data, append=False):
        self.restore_window()
        self.main_window.output_window.output_window_scrollbar.pack_forget()
        self.main_window.output_window.output_window_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.clear_output_window_canvas_data()
        main_window.output_window.text_component.pack(fill=tk.BOTH, expand=True)
        main_window.output_window.text_component.output_text.config(state=tk.NORMAL)

        try:
            if not append:
                main_window.output_window.output_text.delete(1.0, tk.END)
            else:
                main_window.output_window.output_text.yview(tk.END)
            self.loading_spinner.stop()
            for index, item in enumerate(data):
                main_window.output_window.output_text.config(state=tk.NORMAL)
                role = item.role
                message = item.message
                if role == ASSISTANT_NAME:
                    char_list = list(message)
                    self.text_highlighter.follow_insert = False
                    self.text_highlighter.batch_insert_word(char_list)
                    self.text_highlighter.insert_word("\n")
                else:
                    if index == 0:
                        user_content = f"{message}\n\n"
                    else:
                        user_content = f"\n{message}\n\n"
                    font = ("Microsoft YaHei UI", 15, "bold")
                    self.text_inserter.insert_normal(user_content, font)
        except Exception as e:
            self.loading_spinner.stop()
            logger.log('error', e)
        self.open_item_thread_ids.clear()
        main_window.output_window.output_text.config(state=tk.DISABLED)

    def prepare_text(self):
        self.restore_window()
        self.main_window.output_window.output_window_scrollbar.pack_forget()
        self.main_window.output_window.output_window_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.clear_output_window_canvas_data()
        self.main_window.output_window.text_component.pack(fill=tk.BOTH, expand=True)
        self.main_window.output_window.text_component.output_text.config(state=tk.NORMAL)
        return self.main_window.output_window.text_component.output_text

    def show_text_append(self, main_window, user_message, response_message, append=False):
        self.restore_window()
        self.main_window.output_window.output_window_scrollbar.pack_forget()
        self.main_window.output_window.output_window_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.clear_output_window_canvas_data()
        main_window.output_window.text_component.pack(fill=tk.BOTH, expand=True)
        main_window.output_window.text_component.output_text.config(state=tk.NORMAL)
        if not append:
            main_window.output_window.output_text.delete(1.0, tk.END)
        else:
            main_window.output_window.output_text.yview(tk.END)
        if main_window.output_window.output_text.get('1.0', 'end-1c') == "":
            user_content = f"{user_message}\n\n"
        else:
            user_content = f"\n{user_message}\n\n"
        font = ("Microsoft YaHei UI", 15, "bold")
        if user_message is not None:
            self.text_inserter.insert_normal(user_content, font)

    def download_img(self, url):
        response = requests.get(url)
        image_data = BytesIO(response.content)
        return Image.open(image_data)

    def submit_prompt(self):
        self.store_window_geometry()
        self.loading_spinner.start()
        prompt = self.main_window.input_frame.input_text.get('1.0', 'end-1c').strip()
        option = self.main_window.input_frame.option_var.get()
        selected_size = self.main_window.input_frame.size_var.get()
        self.restore_window()
        show_tree = self.session_id is None
        if not prompt:
            self.main_window.input_frame.frame.event_generate('<<RequestOpenaiFinished>>')
            return
        prompt = self.main_window.input_frame.input_text.get('1.0', 'end-1c')
        if self.config_manager.get(LAST_TYPE_OPTION_KEY_NAME, TYPE_OPTION_TXT_KEY) == TYPE_OPTION_IMG_KEY:
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
        if self.config_manager.get(LAST_TYPE_OPTION_KEY_NAME, TYPE_OPTION_TXT_KEY) == TYPE_OPTION_IMG_KEY:
            image_data = None
            success = False
            try:
                model_server = self.chat_factory.create_model_server()
                image_data = model_server.create_image_from_text(prompt, selected_size)
                success = True
            except ChatRequestError as cre:
                thread_id = threading.get_ident()
                running = CancelManager.check_running_state(thread_id)
                if running:
                    CustomConfirmDialog(parent=self.main_window.output_window.output_window, title="错误", message=cre)
            except ChatRequestWarn as crw:
                CustomConfirmDialog(parent=self.main_window.output_window.output_window, title="警告", message=crw)
            except ValueError as ve:
                CustomConfirmDialog(parent=self.main_window.output_window.output_window, title="错误", message=ve)
            except NotImplementedError as nie:
                CustomConfirmDialog(parent=self.main_window.output_window.output_window, title="警告", message=nie)
            except Exception as e:
                logger.log('error', e)
                thread_id = threading.get_ident()
                running = CancelManager.check_running_state(thread_id)
                if running:
                    messagebox.showerror("错误", f"请求错误:\n{e}", parent=self.main_window.output_window.output_window)
            if not success or image_data is None:
                self.main_window.input_frame.frame.event_generate('<<RequestOpenaiFinished>>')
                self.loading_spinner.stop()
                return
            url = image_data[0]
            filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.png")
            file_path = Path(self.config_manager.get("img_folder")) / filename
            img = self.download_img(url)
            img.save(file_path)
            dialogue_data = Dialogue(
                message=prompt,
                img_path=file_path
            )
            self.set_dialog_images([dialogue_data], True, True)
            self.loading_spinner.stop()
            img_model_name = self.config_manager.get("img_model_name")
            img_model_id = self.config_manager.get("img_model_id")
            self.session_id = self.content_service.save_img_record(self.session_id, self.selected_tree_id, prompt,
                                                                   str(file_path), img_model_name, img_model_id)
        else:
            self.set_output_text_default_background()
            answer = None
            success = False
            try:
                text_widget = self.prepare_text()
                answer = self.chat_factory.chat_txt(prompt, self.sys_messages, text_widget, loading_spinner = self.loading_spinner)
                success = True
            except ChatRequestError as cre:
                thread_id = threading.get_ident()
                running = CancelManager.check_running_state(thread_id)
                if running:
                    CustomConfirmDialog(parent=self.main_window.output_window.output_window, title="错误", message=cre)
            except ChatRequestWarn as crw:
                CustomConfirmDialog(parent=self.main_window.output_window.output_window, title="警告", message=crw)
            except NotImplementedError as nie:
                CustomConfirmDialog(parent=self.main_window.output_window.output_window, title="错误", message=nie)
            except Exception as e:
                thread_id = threading.get_ident()
                running = CancelManager.check_running_state(thread_id)
                if running:
                    messagebox.showerror("错误", f"请求错误:\n{e}", parent=self.main_window.output_window.output_window)
                logger.log('error', e)
            if not answer or not success:
                self.loading_spinner.stop()
                self.main_window.input_frame.frame.event_generate('<<RequestOpenaiFinished>>')
                return
            self.loading_spinner.stop()
            self.main_window.output_window.output_text.config(state=tk.DISABLED)
            txt_model_name = self.config_manager.get("txt_model_name")
            txt_model_id = self.config_manager.get("txt_model_id")
            self.session_id = self.content_service.save_txt_record(self.session_id, self.selected_tree_id, prompt,
                                                                   answer, txt_model_name, txt_model_id)
        if show_tree:
            self.insert_tree_item(self.session_id)
        self.main_window.input_frame.frame.event_generate('<<RequestOpenaiFinished>>')

    def set_dialog_images(self, data, append=False, only_img=False, first=False):
        self.main_window.output_window.output_window_canvas.yview_moveto(0)
        self.main_window.output_window.text_component.pack_forget()
        self.main_window.output_window.output_window_canvas.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        self.restore_window()
        self.main_window.output_window.output_window_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        if first or not append:
            self.clear_output_window_canvas_data()
        for index, item in enumerate(data):
            image_path = item.img_path
            frame_width = 600
            img = None
            is_img = True
            if image_path is None or image_path == "":
                is_img = False
                frame_height = 80
            else:
                img = Image.open(image_path)
                original_width, original_height = img.size
                frame_height = (frame_width / original_width) * original_height
            frame = tk.Frame(self.main_window.output_window.output_window_scrollbar_frame, width=frame_width,
                             height=frame_height, bg='#e8eaed')
            frame.pack_propagate(False)
            frame.pack(side=tk.TOP, fill=tk.Y, padx=0, pady=10, anchor=tk.CENTER)
            txt = f"{item.message}\n"
            font_name = 'Microsoft YaHei UI'
            font_size = 15
            text_label = tk.Label(
                frame,
                text=txt,
                font=(font_name, font_size, 'bold'),
                bg='#e8eaed',
                wraplength=580
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
            self.zoom_levels.append(1.0)
            img_label = tk.Label(frame, bg='white')
            img_label.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            self.dialog_labels.append(img_label)
            self.dialog_frames.append(frame)
            self.update_dialog_images(len(self.dialog_labels) - 1)
            img_label.bind("<Button-1>", self.on_click_img)
            img_label.bind("<Button-3>", lambda event: self.on_right_click(event, img))
            img_label.bind("<Double-Button-1>",
                           lambda e: self.image_viewer.on_image_double_click(e, image_path, self.root))
            img_label.bind("<Leave>", self.on_mouse_leave_img)
            if append:
                self.root.after(100, lambda: self.main_window.output_window.output_window_canvas.yview_moveto(1.0))

    def on_output_text_scroll_drag(self, event):
        self.text_highlighter.set_follow_insert_state(False)

    def update_dialog_images(self, index):
        if 0 <= index < len(self.dialog_images):
            image = self.dialog_images[index]
            zoom_level = self.zoom_levels[index]
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
        if self.focus_dialog_index == self.dialog_labels.index(event.widget):
            self.focus_dialog_index = None

    def on_mouse_wheel(self, event):
        if self.focus_dialog_index is not None:
            if event.delta > 0:
                self.zoom_levels[self.focus_dialog_index] *= 1.1
            elif event.delta < 0:
                self.zoom_levels[self.focus_dialog_index] /= 1.1
            self.update_dialog_images(self.focus_dialog_index)

    def save_image(self, image):
        default_filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.png")
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            initialfile=default_filename,
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if file_path and image:
            try:
                image.save(file_path)
            except Exception as e:
                logger.log('error', f"Failed to save image: {e}")

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
        if self.focus_dialog_index is not None or self.config_manager.get(
                LAST_TYPE_OPTION_KEY_NAME) == constant.TYPE_OPTION_TXT_KEY:
            return
        self.main_window.output_window.output_window_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_enter_output_window_canvas_canvas(self, event):
        self.output_window_canvas_scroll_enabled = True

    def on_leave_output_window_canvas_canvas(self, event):
        self.output_window_canvas_scroll_enabled = False

    def set_output_window_pos(self):
        self.root.update()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        window_width = self.main_window.output_window.output_window.winfo_width()
        window_height = self.main_window.output_window.output_window.winfo_height()
        x = root_x + width
        y = root_y
        self.main_window.output_window.output_window.geometry(f"{window_width}x{window_height}+{x + 5}+{y}")

    def set_output_text_default_background(self):
        pass
        self.text_inserter.clean_bg()

    def calculate_font_height(self, font_name, font_size):
        font = tkfont.Font(family=font_name, size=font_size)
        return font.metrics("linespace")

    def on_press_tree_item(self, tree_id):
        self.selected_tree_id = tree_id
        if self.inited:
            self.close_output_window()

    def on_close_output_window(self, event=None):
        self.close_output_window()

    def store_window_geometry(self):
        self.saved_geometry = self.main_window.output_window.output_window.geometry()

    def close_output_window(self):
        self.store_window_geometry()
        self.main_window.output_window.output_window.withdraw()
        self.session_id = None
        model_server = self.chat_factory.create_model_server()
        CancelManager.remove_all_running()
        model_server.clear_history()
        event_bus.publish('CloseOutputWindow')
        self.main_window.input_frame.frame.event_generate('<<RequestOpenaiFinished>>')
        self.inited = True

    def restore_window(self):
        self.main_window.output_window.output_window.deiconify()
        if self.saved_geometry:
            self.main_window.output_window.output_window.geometry(self.saved_geometry)


    def on_change_type_update_list(self, **args):
        self.close_output_window()
        self.bind_tree_events()

    def insert_tree_item(self, content_id):
        event_bus.publish("InsertListItems", content_ids=[content_id])

    def clear_output_window_canvas_data(self):
        if self.dialog_labels is None:
            return
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
        if self.open_item_thread_ids and self.last_click_item_time and (time.time() - self.last_click_item_time) < 1:
            return
        self.last_click_item_time = time.time()
        self.open_item_thread_ids.clear()
        thread = threading.Thread(target=lambda: self.open_item(event, main_window, root))
        thread.start()
        thread_id = thread.ident
        self.open_item_thread_ids.append(thread_id)
        self.inited = True

    def open_item(self, event, main_window, root):
        self.store_window_geometry()
        self.loading_spinner.start()
        selected_items = main_window.display_frame.tree.selection()
        if len(selected_items) == 0:
            return
        item = main_window.display_frame.tree.selection()[0]
        values = main_window.display_frame.tree.item(item, 'values')
        if self.config_manager.get(LAST_TYPE_OPTION_KEY_NAME, TYPE_OPTION_TXT_KEY) == TYPE_OPTION_TXT_KEY:
            self.session_id = values[0]
            self.set_output_text_default_background()
            data = self.content_service.load_txt_dialogs(self.session_id)
            model_server = self.chat_factory.create_model_server()
            model_server.clear_history()
            for item in data:
                model_server.add_history_message(item.role, item.message)
            self.show_text(main_window, data)

        else:
            self.session_id = values[1]
            dialogs = self.content_service.load_img_dialogs(self.session_id)
            self.set_dialog_images(dialogs)
            self.open_item_thread_ids.clear()
        event_bus.publish("OpenChatDetail")
        self.loading_spinner.stop()

    def thread_submit(self, event=None):
        self.cancel_request()
        self.loading_spinner.stop()
        thread = threading.Thread(target=lambda: self.submit_prompt())
        thread.start()
        thread_id = thread.ident
        CancelManager.add_running(thread_id)
        event_bus.publish("OpenChatDetail")
        self.inited = True

    def cancel_request(self, event = None):
        CancelManager.remove_all_running()
        self.loading_spinner.stop()


    def on_press_cancel_request_hot_key(self, event = None):
        self.cancel_request()
        self.root.event_generate('<<HotKeyCancelRequest>>')

    def on_press_new_chat_hot_key(self, event = None):
        self.cancel_request()
        self.root.event_generate('<<HotKeyNewChat>>')

    def update_sys_messages(self, preset_id, sys_messages):
        self.sys_messages = sys_messages

    def on_dialog_model_changed(self, model_name):
        model_server = self.chat_factory.create_model_server()
        model_server.reload_model(model_name)

    def on_dialog_setting_changed(self):
        model_server = self.chat_factory.create_model_server()
        model_server.reload_config()

    def bind_tree_events(self):
        self.main_window.display_frame.tree.bind("<Double-1>",
                                                 lambda event: self.on_item_double_click(event, self.main_window,
                                                                                         self.root))

    def bind_events(self):
        self.bind_tree_events()
        self.output_window.output_window.protocol("WM_DELETE_WINDOW", self.close_output_window)
        self.output_window.output_window.bind("<MouseWheel>", self.on_mouse_wheel)
        self.output_window.output_text.vbar.bind("<B1-Motion>", lambda event: self.on_output_text_scroll_drag(event))
        self.output_window.output_text.bind("<MouseWheel>", lambda event: self.on_output_text_scroll_drag(event))
        self.output_window.output_window_canvas.bind("<Enter>", self.on_enter_output_window_canvas_canvas)
        self.output_window.output_window_canvas.bind("<Leave>", self.on_leave_output_window_canvas_canvas)
        self.output_window.output_window_canvas.bind_all("<MouseWheel>", self.on_output_window_canvas_mouse_wheel)
        event_bus.subscribe('TreeItemPress', self.on_press_tree_item)
        event_bus.subscribe('ChangeTypeUpdateList', self.on_change_type_update_list)
        event_bus.subscribe('NewChat', self.close_output_window)
        event_bus.subscribe('DialogPresetChanged', self.update_sys_messages)
        event_bus.subscribe('DialogPresetLoaded', self.update_sys_messages)
        event_bus.subscribe('DialogModelChanged', self.on_dialog_model_changed)
        event_bus.subscribe('DialogSettingChanged', self.on_dialog_setting_changed)
        self.root.bind('<<SubmitRequest>>', lambda event: self.thread_submit(event))
        self.root.bind('<<CancelRequest>>', lambda event: self.cancel_request(event))
        self.output_window.output_window.bind("<Control-Shift-O>", self.on_press_cancel_request_hot_key)
        self.output_window.output_window.bind("<Control-Shift-o>", self.on_press_cancel_request_hot_key)
        self.output_window.output_window.bind("<Control-Shift-N>", self.on_press_new_chat_hot_key)
        self.output_window.output_window.bind("<Control-Shift-n>", self.on_press_new_chat_hot_key)
