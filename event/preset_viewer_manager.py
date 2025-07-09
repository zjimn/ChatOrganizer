from datetime import datetime
from tkinter import font, ttk, messagebox
import tkinter as tk

from config.constant import TOGGLE_BUTTON_CHECK_IMAGE_PATH, TOGGLE_BUTTON_UNCHECK_IMAGE_PATH
from db.models import DialoguePresetDetail
from event.event_bus import event_bus
from service.dialog_preset_service import DialoguePresetService
from util.logger import logger
from widget.undo_redo_entry import UndoRedoEntry
from util.window_util import center_window, right_window
from widget.confirm_dialog import ConfirmDialog
from widget.custom_slider import CustomSlider
from widget.icon_toggle_button import IconToggleButton


class PresetViewerManager:
    def __init__(self, parent, preset_viewer):
        self.max_history_express_label = None
        self.max_history_toggle_button = None
        self.max_history_slider = None
        self.max_history_count_var = tk.IntVar()
        self.pre_listbox_pos = None
        self.selected_item = None
        self.title_name_text_var = None
        self.parent = parent
        self.preset_viewer = preset_viewer
        self.preset_viewer_window = preset_viewer.main_window
        self.bind_events()
        self.dialogue_preset_service = DialoguePresetService()
        self.dialogue_preset_data = []
        self.detail_window = None
        self.context_menu = tk.Menu(self.parent, tearoff=0)
        self.context_menu.add_command(label="编辑", command=self.display_selected_item)
        self.context_menu.add_command(label="删除", command=self.delete_selected_item)

    def bind_events(self):
        self.preset_viewer_window.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.preset_viewer.add_button.config(command = self.on_add)
        self.preset_viewer.listbox.bind("<Double-1>", self.display_selected_item)
        event_bus.subscribe("OpenPresetViewer", self.open_preset_viewer)
        self.preset_viewer.listbox.bind("<Button-3>", self.show_context_menu)

    def open_preset_viewer(self):
        self.open()
        self.load_data()

    def load_data(self, id = None):
        self.preset_viewer.listbox.delete(0, tk.END)
        data = self.dialogue_preset_service.get_all_dialog_preset_list()
        self.dialogue_preset_data = data
        for index, item in enumerate(data):
            self.preset_viewer.listbox.insert(tk.END, item.name)
            if id == item.id:
                self.preset_viewer.listbox.selection_set(index)
        if self.pre_listbox_pos:
            self.preset_viewer.listbox.yview_moveto(self.pre_listbox_pos[0])


    def get_system_fonts(self):
        values = font.families()
        return values

    def open(self):
        center_window(self.preset_viewer_window, self.parent,self.preset_viewer.win_width, self.preset_viewer.win_height)
        self.preset_viewer_window.deiconify()
        if self.detail_window:
            self.detail_window.destroy()

    def show_context_menu(self, event):
        try:
            index = self.preset_viewer.listbox.nearest(event.y)
            self.preset_viewer.listbox.selection_clear(0, tk.END)
            self.preset_viewer.listbox.selection_set(index)
            self.selected_item = self.preset_viewer.listbox.get((index,))
            self.context_menu.post(event.x_root, event.y_root)
        except Exception as e:
            logger.log('error', f"Error showing context menu: {e}")

    def delete_selected_item(self):
        try:
            current_sel = self.preset_viewer.listbox.curselection()
            if current_sel and len(current_sel) > 0:
                dialog = ConfirmDialog(title="删除", message="确定删除所选?")
                if dialog.result:
                    self.preset_viewer.listbox.delete(current_sel[0])
                    self.dialogue_preset_service.delete_data(self.dialogue_preset_data[current_sel[0]].id)
                    event_bus.publish("DialogPresetUpdated")
        except Exception as e:
            logger.log('error', f"Can't delete: {e}")
            messagebox.showerror("删除失败", f"无法删除项: {e}")

    def display_selected_item(self, event = None):
        current_sel = self.preset_viewer.listbox.curselection()
        current_name = self.preset_viewer.listbox.get(current_sel)
        max_history_count = 0
        # max_history_count = self.dialogue_preset_data[current_sel[0]].max_history_count
        self.display_detail(self.dialogue_preset_data[current_sel[0]].id, current_name, max_history_count, title = "编辑预设")

    def on_add(self):
        self.display_detail(title = "添加预设")

    def display_detail(self, id = None, name = None, max_history_count = 0, title = None):
        win_width = self.preset_viewer.win_width
        win_height = self.preset_viewer.win_height
        if self.detail_window:
            self.detail_window.destroy()
        self.detail_window = tk.Toplevel(self.preset_viewer_window)
        self.detail_window.title(title)
        self.detail_window.geometry(f"{win_width}x{win_height}")
        self.detail_window.transient(self.preset_viewer_window)
        right_window(self.detail_window, self.preset_viewer_window, win_width, win_height, padx = 5)
        name =""
        dpd = DialoguePresetDetail()
        detail =[dpd]
        if id:
            name, max_history_count, detail = self.dialogue_preset_service.get_data_by_id(id)


        main_frame = ttk.Frame(self.detail_window, borderwidth=0, relief=tk.RAISED)


        top_frame = ttk.Frame(main_frame, borderwidth=0, relief=tk.RAISED)
        hidden_preset_id_label = ttk.Label(top_frame, text=id, font=("Microsoft YaHei UI", 10))
        hidden_preset_id_label.pack_forget()
        title_label = ttk.Label(top_frame, text="名称", font=("Microsoft YaHei UI", 10))
        title_label.pack(side = tk.LEFT, padx=(10, 5), pady=5)

        top_frame.title_name_text_var = tk.StringVar(value=name)
        title_name_text = UndoRedoEntry(top_frame, width=50, style="Custom.TEntry",
                                           textvariable=top_frame.title_name_text_var)
        save_button = ttk.Button(top_frame, text="保存", state=tk.NORMAL)


        save_button.pack(side=tk.RIGHT, padx=(10, 10))
        title_name_text.pack(side=tk.RIGHT, fill=tk.X, padx=(0, 10), pady=(0, 0), expand = True)
        top_frame.pack(side = tk.TOP, fill=tk.X, padx=(0, 0), pady=(10, 10))

        separator_frame = ttk.Frame(main_frame, borderwidth=0, relief=tk.RAISED)
        separator = ttk.Separator(separator_frame, orient="horizontal")
        separator.pack(side="left", fill="x", padx=0, expand = True)
        separator_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(5, 0))

        max_history_frame = ttk.Frame(main_frame, borderwidth=0, relief=tk.RAISED)
        limit_max_history_label = ttk.Label(max_history_frame, text="限制记忆数", font=("Microsoft YaHei UI", 10))
        limit_max_history_label.pack(side = tk.LEFT, padx=(0, 10), pady=15)
        self.max_history_slider = CustomSlider(max_history_frame, label_text="", from_=1, to=50, default=1)

        check_image_path = TOGGLE_BUTTON_CHECK_IMAGE_PATH
        uncheck_image_path = TOGGLE_BUTTON_UNCHECK_IMAGE_PATH
        self.max_history_toggle_button = IconToggleButton(max_history_frame, default_state= True, check_image_path = check_image_path, uncheck_image_path = uncheck_image_path, width=50, height=25)
        self.max_history_toggle_button.pack(side = tk.LEFT, fill=tk.X, padx=0, pady=0)
        self.max_history_slider.pack(side=tk.LEFT, fill=tk.X, padx=10, pady=5, anchor=tk.E)
        self.max_history_toggle_button.set_state(max_history_count > 0)
        self.max_history_toggle_button.bind("<<CheckboxToggled>>", self.on_max_history_toggle_change)

        self.max_history_express_label = ttk.Label(max_history_frame, text="(联系上下文对话条数)", font=("Microsoft YaHei UI", 9))
        self.max_history_express_label.pack(side = tk.LEFT, padx=(10, 10), pady=5)


        max_history_frame.pack(side = tk.TOP, fill=tk.X, padx=10, pady=0)


        detail_label_frame = ttk.Frame(main_frame)
        detail_label_frame.pack(side = tk.TOP, fill=tk.X, padx=(0, 0), pady=(0, 0))
        detail_label = ttk.Label(detail_label_frame, text="内容", font=("Microsoft YaHei UI", 10, "bold"))
        detail_label.pack(side = tk.LEFT, padx=(10, 10), pady=5)

        input_body_frame = ttk.Frame(main_frame)
        input_body_frame.pack(side = tk.TOP, fill=tk.X, padx=(0, 0), pady=(0, 10))

        add_frame = ttk.Frame(main_frame)
        add_frame.pack(side = tk.TOP, fill=tk.X, padx=(0, 0), pady=5)

        add_button = ttk.Button(add_frame, text="添加", state=tk.NORMAL)
        add_button.pack(side=tk.TOP, fill = tk.X, padx=(10, 10), expand=True)
        main_frame.pack(side='left', padx=(5, 5), pady=(0, 0), fill=tk.BOTH, expand=True)
        items = [top_frame, detail_label_frame, add_frame]
        items_height = self.get_items_height(items)
        add_button.config(command= lambda window = self.detail_window, parent = input_body_frame, add_fr = add_frame: self.add_item(window, items_height, input_body_frame, add_fr))
        save_button.config(command= lambda window = self.detail_window, il = hidden_preset_id_label, tl = title_name_text, dl = input_body_frame: self.save_preset_detail(window, il, tl, dl))
        self.load_detail(detail, self.detail_window, items_height, input_body_frame)
        self.display_max_history_slider(self.max_history_toggle_button.get_state(), max_history_count)
        self.detail_window.iconbitmap("res/icon/edit.ico")

    def on_max_history_toggle_change(self, event):
        state = self.max_history_toggle_button.get_state()
        self.display_max_history_slider(state, self.max_history_slider.get())

    def display_max_history_slider(self, state, max_history_count):
        if state:
            if max_history_count == 0:
                self.max_history_slider.set(1)
            else:
                self.max_history_slider.set(max_history_count)
            self.max_history_slider.pack(side=tk.LEFT, fill=tk.X, padx=10, pady=5, anchor=tk.E)
            self.max_history_express_label.pack_forget()
        else:
            self.max_history_slider.pack_forget()
            self.max_history_express_label.pack(side=tk.LEFT, padx=(10, 10), pady=5)

    def load_detail(self, detail, window, items_height, input_body_frame):
        for item in detail:
            self.add_item(window, items_height, input_body_frame, None, item.id, item.value, True)
        self.parent.update()
        self.adjust_window_height_based_on_elements(window, items_height, input_body_frame)


    def save_preset_detail(self, window, id_label, title_label, detail_label):
        detail_list = []
        for widget in detail_label.winfo_children():
            if not widget:
                continue
            delete_time = None
            if not widget.winfo_exists() or not widget.winfo_ismapped():
                delete_time = datetime.now()
            dpd = DialoguePresetDetail()
            if hasattr(widget, 'data_id'):
                data_id = widget.data_id
                dpd.id = data_id
            value = widget.data_value.get()

            dpd.value = value
            dpd.delete_time = delete_time
            detail_list.append(dpd)
        id = id_label.cget('text')
        title = title_label.get()
        max_history_count = self.max_history_slider.get()
        state = self.max_history_toggle_button.get_state()
        if not state:
            max_history_count = 0
        if not id:
            id = self.dialogue_preset_service.insert_data(title, max_history_count, detail_list)
        else:
            self.dialogue_preset_service.update_data(id, title, max_history_count, detail_list)
        self.pre_listbox_pos = self.preset_viewer.listbox.yview()
        self.load_data(id)
        event_bus.publish("DialogPresetUpdated")
        window.destroy()


    def delete_item(self, window, items_height, parent, item):
        item.pack_forget()
        item.update()
        total_height = parent.winfo_height()
        self.adjust_window_height_based_on_elements(window, items_height, parent)

        if len([child for child in parent.winfo_children() if child.winfo_ismapped()]) == 0:
            parent.pack_forget()

    def add_item(self, window, items_height, parent, add_fr, data_id = None, text = "", adjust_height = True):
        input_frame = ttk.Frame(parent)
        input_frame.pack(side = tk.TOP, fill=tk.X, padx=(0, 0), pady=(5, 5))

        input_frame.input_text_var = tk.StringVar(value=text)
        input_text = UndoRedoEntry(input_frame, width=50, style="Custom.TEntry",
                                           textvariable=input_frame.input_text_var)
        delete_button = ttk.Button(input_frame, text="删除", state=tk.NORMAL)
        delete_button.pack(side=tk.RIGHT, padx=(10, 10))
        delete_button.config(command= lambda item = delete_button.master: self.delete_item(window, items_height, parent, input_frame))
        input_text.pack(side=tk.RIGHT, fill=tk.X, padx=10, pady=(0, 0), expand = True)
        input_frame.data_id = data_id
        input_frame.data_value = input_text
        parent.update()
        if adjust_height:
            self.adjust_window_height_based_on_elements(window, items_height, parent)

        if add_fr:
            parent.pack(side=tk.TOP, fill=tk.X, padx=(0, 0), pady=(0, 10))
            add_fr.pack_forget()
            add_fr.pack(side=tk.TOP, fill=tk.X, padx=(0, 0), pady=5)

    def adjust_window_height_based_on_elements(self, window,items_height, input_body_frame):
        total_height = items_height
        total_height += input_body_frame.winfo_height()
        current_width = window.winfo_width()
        height = input_body_frame.winfo_height()
        window.geometry(f"{current_width}x{total_height+220}")

    def get_items_height(self, items):
        total_height = 0
        for widget in items:
            total_height += widget.winfo_height()
        return total_height


    def on_cancel(self):
        self.preset_viewer_window.withdraw()
