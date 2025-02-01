from datetime import datetime
from tkinter import font, ttk
import tkinter as tk

from config.constant import LAST_TYPE_OPTION_KEY_NAME, TYPE_OPTION_IMG_KEY, TYPE_OPTION_TXT_KEY
from db.models import DialogueModel
from event.event_bus import event_bus
from service.DialogModelService import DialogueModelService
from util.config_manager import ConfigManager
from util.undo_redo_entry import UndoRedoEntry
from util.window_util import center_window


class ModelViewerManager:
    def __init__(self, parent, model_viewer):
        self.model_type = None
        self.config_manager = ConfigManager()
        self.selected_item = None
        self.title_name_text_var = None
        self.parent = parent
        self.model_viewer = model_viewer
        self.model_viewer_window = model_viewer.main_window
        self.bind_events()
        self.dialogue_model_service = DialogueModelService()
        self.dialogue_preset_data = []

    def bind_events(self):
        self.model_viewer_window.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.model_viewer.add_button.config(command = self.on_add)
        event_bus.subscribe("OpenModelViewer", self.open_model_viewer)

    def open_model_viewer(self):
        self.open()

    def get_system_fonts(self):
        values = font.families()
        return values

    def open(self):
        center_window(self.model_viewer_window, self.parent, self.model_viewer.win_width, self.model_viewer.win_height)
        self.model_viewer_window.deiconify()
        self.set_model_type()
        self.display_detail()

    def set_model_type(self):
        model_type = "text"
        if self.config_manager.get(LAST_TYPE_OPTION_KEY_NAME, TYPE_OPTION_TXT_KEY) == TYPE_OPTION_IMG_KEY:
            model_type = "img"
        self.model_type = model_type

    def on_add(self):
        self.display_detail()

    def display_detail(self):
        for item in self.model_viewer.input_body_frame.winfo_children():
            item.destroy()
        detail = self.dialogue_model_service.get_all_dialog_model_list(self.model_type)
        items = [self.model_viewer.top_frame, self.model_viewer.detail_label_frame, self.model_viewer.add_frame]
        self.parent.update()
        items_height = self.get_items_height(items)
        self.model_viewer.add_button.config(command= lambda window = self.model_viewer.main_window, parent = self.model_viewer.input_body_frame: self.add_item(items_height, parent))
        self.model_viewer.save_button.config(command= lambda window = self.model_viewer.main_window, dl = self.model_viewer.input_body_frame: self.save_model_detail(dl))
        self.load_detail(detail, self.model_viewer.main_window, items_height, self.model_viewer.input_body_frame)

    def load_detail(self, detail, window, items_height, input_body_frame):
        for item in detail:
            self.add_item(items_height, self.model_viewer.input_body_frame, item.id, item.name, True)
        self.parent.update()
        self.adjust_window_height_based_on_elements(items_height)


    def save_model_detail(self, detail_label):
        detail_list = []
        for widget in detail_label.winfo_children():
            if not widget:
                continue
            delete_time = None
            if not widget.winfo_exists() or not widget.winfo_ismapped():
                delete_time = datetime.now()
            dm = DialogueModel()
            if hasattr(widget, 'data_id'):
                data_id = widget.data_id
                dm.id = data_id
            name = widget.data_name.get()
            dm.name = name
            dm.delete_time = delete_time
            detail_list.append(dm)
        self.dialogue_model_service.update_or_insert_data(detail_list, self.model_type)
        event_bus.publish("DialogModelUpdated")
        self.model_viewer.main_window.withdraw()

    def delete_item(self, items_height, parent, item):
        item.pack_forget()
        item.update()
        total_height = parent.winfo_height()
        self.adjust_window_height_based_on_elements(items_height)

    def add_item(self, items_height, parent, data_id = None, text = "", adjust_height = True):
        input_frame = ttk.Frame(parent)
        input_frame.pack(side = tk.TOP, fill=tk.X, padx=(0, 0), pady=(5, 5))

        input_frame.input_text_var = tk.StringVar(value=text)
        input_text = UndoRedoEntry(input_frame, width=50, style="Custom.TEntry",
                                           textvariable=input_frame.input_text_var)
        delete_button = ttk.Button(input_frame, text="删除", state=tk.NORMAL)
        delete_button.pack(side=tk.RIGHT, padx=(10, 10))
        delete_button.config(command= lambda item = delete_button.master: self.delete_item(items_height, parent, input_frame))
        input_text.pack(side=tk.RIGHT, fill=tk.X, padx=10, pady=(0, 0), expand = True)
        input_frame.data_id = data_id
        input_frame.data_name = input_text
        parent.update()
        if adjust_height:
            self.adjust_window_height_based_on_elements(items_height)

    def adjust_window_height_based_on_elements(self, items_height):
        total_height = items_height
        self.model_viewer.input_body_frame.update()
        total_height += self.model_viewer.input_body_frame.winfo_height()
        current_width = self.model_viewer.main_window.winfo_width()
        height = self.model_viewer.input_body_frame.winfo_height()
        self.model_viewer.main_window.geometry(f"{current_width}x{total_height+85}")

    def get_items_height(self, items):
        total_height = 0
        for widget in items:
            total_height += widget.winfo_height()
        return total_height


    def on_cancel(self):
        self.model_viewer_window.withdraw()
