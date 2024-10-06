import tkinter as tk
from datetime import datetime
from tkinter import *
from tkinter import messagebox, ttk, font
from PIL import ImageTk
from config.app_config import AppConfig
from config.constant import USER_NAME, ASSISTANT_NAME, LAST_TYPE_OPTION_KEY_NAME, TYPE_OPTION_TXT_KEY, \
    LAST_SELECTED_TREE_ID_NAME
from db.content_data_access import ContentDataAccess
from db.dialogue_data_access import DialogueDataAccess
from db.models import Dialogue
from event.editor_tree_manager import EditorTreeManager
from event.event_bus import event_bus
from service.content_service import ContentService
from ui.editor_directory_tree import EditorDirectoryTree
from ui.scrollable_frame import ScrollableFrame
from util import image_util
from util.image_viewer import ImageViewer
from util.window_util import center_window


class ListEditor:
    def __init__(self, main_window=None):
        self.top = None
        self.button_frame = None
        self.cancel_button = None
        self.submit_button = None
        self.tree = None
        self.selected_item_id = None
        self.describe_input = None
        self.description_frame = None
        self.edit_window = None
        self.item_data = None
        self.parent = main_window.root
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.main_window = main_window
        self.list_tree = main_window.display_frame.tree
        self.content_service = ContentService()
        self.app_config = AppConfig()
        self.context_menu = Menu(self.parent, tearoff=0)
        self.context_menu.add_command(label="复制到", command=lambda: self.move_or_copy_selected_item(is_move=False))
        self.context_menu.add_command(label="移动到", command=lambda: self.move_or_copy_selected_item(is_move=True))
        self.context_menu.add_command(label="修改项", command=self.modify_selected_item)
        self.context_menu.add_command(label="删除项", command=self.remove_selected_item)
        self.dialogue_frames = []
        self.dialogue_image_labels = []
        self.bind_events()
        self.last_event = None
        self.enable_edit_button = False

    def bind_events(self):
        self.list_tree.bind("<Button-3>", self.show_context_menu)
        event_bus.subscribe('ChangeTypeUpdateList', self.on_change_type_update_list)

    def bind_tree_events(self):
        self.list_tree.bind("<Button-3>", self.show_context_menu)

    def on_change_type_update_list(self, **args):
        self.list_tree = self.main_window.display_frame.tree
        self.bind_tree_events()

    def show_context_menu(self, event):
        iid = self.list_tree.identify_row(event.y)
        if iid:
            selected_item_ids = self.list_tree.selection()
            if len(selected_item_ids) <= 1:
                self.context_menu.entryconfig(2, state=NORMAL)
                self.list_tree.selection_set(iid)
                self.selected_item_id = iid
            else:
                self.context_menu.entryconfig(2, state=DISABLED)
            self.context_menu.post(event.x_root, event.y_root)
            self.last_event = event

    def set_show_edit_button(self, enable):
        self.enable_edit_button = enable

    def get_data(self, content_id):
        data = self.content_service.load_data(content_id)
        return data

    def update_item_data(self, content_id, type, describe, content):
        self.content_service.update_data(content_id, type, describe, content)

    def center_window(self, window, width, height):
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        x = parent_x + (parent_width // 2) - (width // 2)
        y = parent_y + (parent_height // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")

    def close_window(self):
        self.dialogue_frames.clear()
        self.item_data = []
        if self.edit_window:
            self.edit_window.destroy()

    def copy_selected_item(self):
        pass

    def move_or_copy_selected_item(self, is_move):
        self.close_and_clear_data()
        self.top = tk.Toplevel(self.parent)
        if is_move:
            self.top.title("选择移动到的层级")
        else:
            self.top.title("选择复制到的层级")
        self.top.geometry("300x300")
        self.top.grab_set()
        center_window(self.top, 300, 300)
        editor_directory_tree = EditorDirectoryTree(self.top)
        self.tree = editor_directory_tree.tree
        button_frame = tk.Frame(self.top)
        button_frame.pack(side=tk.BOTTOM, anchor='se', pady=10)
        cancel_button = tk.Button(button_frame, text="取消", width=6, command=self.close_and_clear_data)
        cancel_button.pack(side=tk.RIGHT, padx=5)
        content_ids, tree_id = self.get_selected_list_content_ids_and_tree_id()
        self.submit_button = tk.Button(button_frame, text="确定", width=6,
                                       command=lambda: self.move_or_copy_selected(is_move, content_ids, tree_id))
        self.submit_button.pack(side=tk.RIGHT, padx=5)
        top_id = self.tree.get_children()
        EditorTreeManager(self.parent, editor_directory_tree, top_id, tree_id)

    def move_or_copy_selected(self, is_move, content_ids, tree_id):
        selected_tree_items = self.tree.selection()
        if selected_tree_items:
            target_tree_id = selected_tree_items[0]
            if tree_id != target_tree_id:
                event_bus.publish("MoveToTargetTree", tree_id=target_tree_id)
                self.parent.after(300, lambda: event_bus.publish("InsertListItems", content_ids=content_ids))
                if is_move:
                    self.parent.after(530,
                                      lambda: self.content_service.move_to_target_tree(content_ids, target_tree_id))
                else:
                    self.parent.after(530,
                                      lambda: self.content_service.copy_to_target_tree(content_ids, target_tree_id))
            self.close_and_clear_data()
        else:
            messagebox.showwarning("警告", "请先选择一个层级。")

    def get_selected_list_content_ids_and_tree_id(self):
        selected_items = self.list_tree.selection()
        selected_tree_id = self.app_config.get(LAST_SELECTED_TREE_ID_NAME)
        result = []
        for item in selected_items:
            list_item_values = self.list_tree.item(item, 'values')
            if self.app_config.get(LAST_TYPE_OPTION_KEY_NAME, TYPE_OPTION_TXT_KEY) == TYPE_OPTION_TXT_KEY:
                content_id = list_item_values[0]
            else:
                content_id = list_item_values[1]
            result.append(content_id)
        return result, selected_tree_id

    def close_and_clear_data(self):
        if self.tree and self.tree.winfo_exists():
            for item in self.tree.get_children():
                self.tree.delete(item)
        if self.top:
            self.top.destroy()
            self.tree.destroy()

    def modify_selected_item(self):
        if not self.last_event:
            return
        self.close_window()
        edit_window = Toplevel(self.parent)
        edit_window.title("编辑项")
        edit_window.geometry("600x500")
        self.edit_window = edit_window
        self.center_window(edit_window, 600, 500)
        button_frame = Frame(edit_window)
        button_frame.pack(side=BOTTOM, anchor=E, padx=10, pady=10)

        def on_confirm():
            update_datas = []
            content_id = self.description_frame.widgets['content_id_label'].cget('text')
            describe = self.description_frame.widgets['describe_input'].get("1.0", tk.END).strip()
            first_img_path = ''
            for frame in self.dialogue_frames:
                delete_time = None
                if not frame.winfo_exists():
                    continue
                if not frame.winfo_exists() or not frame.winfo_ismapped():
                    delete_time = datetime.now()
                user_id = frame.widgets['user_id_label'].cget('text')
                assistant_id = frame.widgets['assistant_id_label'].cget('text')
                user_input_content = frame.widgets['user_input'].get("1.0", tk.END).strip()
                assistant_input_content = frame.widgets['assistant_input'].get("1.0", tk.END).strip()
                assistant_img_path = frame.widgets['assistant_image_path_label'].cget('text')
                if first_img_path == '':
                    first_img_path = assistant_img_path
                user_dialogue = Dialogue(
                    id=user_id,
                    role=USER_NAME,
                    message=user_input_content,
                    delete_time=delete_time
                )
                assistant_dialogue = Dialogue(
                    id=assistant_id,
                    role=ASSISTANT_NAME,
                    message=assistant_input_content,
                    img_path=assistant_img_path,
                    delete_time=delete_time
                )
                update_datas.append(user_dialogue)
                update_datas.append(assistant_dialogue)
            with ContentDataAccess() as cda:
                self.content_service.update_data(content_id, None, describe=describe, content=None,
                                                 img_path=first_img_path, dialogues=update_datas)
                with DialogueDataAccess() as dda:
                    self.content_service.batch_update_dialogue_data(update_datas)
            event_bus.publish("UpdateListSingleItem", content_id=content_id, item_id=self.selected_item_id)
            self.close_window()

        def on_cancel():
            self.close_window()

        confirm_button = Button(button_frame, text="确定", width=10, command=on_confirm)
        confirm_button.pack(side=LEFT, padx=5)
        cancel_button = Button(button_frame, text="取消", width=10, command=on_cancel)
        cancel_button.pack(side=LEFT, padx=5)
        self.description_frame = Frame(edit_window)
        self.description_frame.pack(side=TOP, anchor=E, padx=(10, 10), pady=10, fill=tk.X)
        label_font = font.Font(family="Helvetica", size=10, weight="bold")
        description_label = tk.Label(self.description_frame, text="描述:", font=label_font, fg="#333333")
        description_label.pack(side=TOP, anchor=W)
        selected_item = self.list_tree.selection()[0]
        list_item_values = self.list_tree.item(selected_item, 'values')
        if self.app_config.get(LAST_TYPE_OPTION_KEY_NAME, TYPE_OPTION_TXT_KEY) == TYPE_OPTION_TXT_KEY:
            content_id = list_item_values[0]
        else:
            content_id = list_item_values[1]
        hidden_content_id_label = Label(self.description_frame, text=content_id,
                                        fg=self.description_frame.cget('bg'))
        hidden_content_id_label.pack_forget()
        self.style.configure("Custom.DESCRIBE.INPUT", padding=(3, 3))
        self.describe_input = tk.Text(self.description_frame, height=1, padx=5, pady=5)
        self.describe_input.pack(side=tk.TOP, fill=tk.X)
        self.describe_input.config(font=("Microsoft YaHei", 10))
        self.description_frame.widgets = {
            'content_id_label': hidden_content_id_label,
            'describe_input': self.describe_input,
        }
        data = self.get_data(content_id)
        self.describe_input.insert("1.0", data.describe)
        self.item_data = data
        if data and len(data.dialogues) > 0:
            label_font = font.Font(family="Helvetica", size=10, weight="bold")
            content_label = tk.Label(edit_window, text="对话:", font=label_font, fg="#333333")
            content_label.pack(side=TOP, anchor=W, padx=10, pady=0)
            frame = ScrollableFrame(edit_window)
            self.set_dialogue_list(data.dialogues, frame.scrollable_frame)
            frame.pack(fill=tk.BOTH, expand=True)

    def set_dialogue_list(self, data, scrollable_frame):
        for index in range(0, len(data), 2):
            content_frame = Frame(scrollable_frame)
            content_frame.pack(side=TOP, anchor=W, fill=tk.X, padx=10, pady=(10, 30))
            self.dialogue_frames.append(content_frame)
            content_right_frame = Frame(content_frame)
            content_right_frame.pack(side=RIGHT, anchor=E, fill=tk.Y)
            select_item_button = Button(content_right_frame, text="保留", fg="#228B22",
                                        command=lambda cf=content_frame: self.keep_only(cf, select_item_button))
            select_item_button.pack(side=TOP, anchor=NE, padx=10)
            if len(data) < 4:
                select_item_button.config(state=tk.DISABLED)
            delete_item_button = Button(content_right_frame, text="删除", fg="#B22222",
                                        command=lambda cf=content_frame: self.delete_frame(cf, select_item_button))
            delete_item_button.pack(side=tk.BOTTOM, anchor=SE, padx=10)
            content_left_frame = Frame(content_frame)
            content_left_frame.pack(side=LEFT, anchor=W, fill=tk.X, expand=True)
            hidden_user_id_label = Label(content_frame, text=data[index].id)
            hidden_user_id_label.pack_forget()
            hidden_assistant_id_label = Label(content_frame, text=data[index + 1].id)
            hidden_assistant_id_label.pack_forget()
            self.style.configure("Custom.DIALOGUE.USER.INPUT", padding=(3, 3))
            dialogue_user_input = Text(content_left_frame, width=30, height=1, padx=5, pady=5)
            dialogue_user_input.pack(side=tk.TOP, fill=tk.X)
            dialogue_user_input.config(font=("Microsoft YaHei", 10))
            dialogue_user_input.insert("1.0", data[index].message)
            dialogue_assistant_input = Text(content_left_frame, height=5, width=30, padx=5, pady=5)
            dialogue_assistant_input.pack_forget()
            if data[index + 1].message is not None and data[index + 1].message != '':
                dialogue_assistant_input = Text(content_left_frame, height=5, width=30, padx=5, pady=5)
                dialogue_assistant_input.pack(side=TOP, fill=tk.X)
                dialogue_assistant_input.insert("1.0", data[index + 1].message)
            hidden_assistant_img_path_label = Label(content_frame, text=data[index + 1].img_path)
            hidden_assistant_img_path_label.pack_forget()
            if data[index + 1].img_path:
                img_path = data[index + 1].img_path
                img = image_util.resize_image_by_path(data[index + 1].img_path, (None, 100))
                photo = ImageTk.PhotoImage(img)
                image_label = Label(content_left_frame, image=photo)
                image_label.image = photo
                image_label.pack(side=LEFT, pady=5, fill=tk.BOTH)
                self.dialogue_image_labels.append(image_label)
                image_viewer = ImageViewer(self.parent)
                print(f"img_path before {img_path}")
                image_label.bind("<Double-Button-1>",
                                 lambda e, image_path=img_path: image_viewer.on_image_double_click(e, image_path,
                                                                                                   self.parent))
            content_frame.widgets = {
                'user_id_label': hidden_user_id_label,
                'assistant_id_label': hidden_assistant_id_label,
                'assistant_image_path_label': hidden_assistant_img_path_label,
                'user_input': dialogue_user_input,
                'assistant_input': dialogue_assistant_input
            }

    def get_valid_data_count(self):
        count = 0
        for frame in self.dialogue_frames:
            if not frame.winfo_exists():
                continue
            if frame.winfo_ismapped():
                count += 1
        return count

    def delete_frame(self, frame, select_item_button):
        frame.pack_forget()
        self.check_and_set_button_state(select_item_button)

    def check_and_set_button_state(self, select_item_button):
        valid_data_count = self.get_valid_data_count()
        if valid_data_count < 2:
            select_item_button.config(state=tk.DISABLED)

    def keep_only(self, frame_to_keep, select_item_button):
        select_item_button.config(state=tk.DISABLED)
        response = messagebox.askyesno(
            "Confirm",
            "确定需要保留该项删除其他项?",
            parent=self.edit_window
        )
        if response:
            for frame in self.dialogue_frames:
                if frame != frame_to_keep:
                    frame.pack_forget()
        else:
            pass

    def remove_selected_item(self):
        selected_items = self.list_tree.selection()
        result = messagebox.askyesno("删除数据", "确定需要删除所选数据吗?")
        if result:
            with ContentDataAccess() as cda:
                for item in selected_items:
                    values = self.list_tree.item(item, 'values')
                    cda.delete_data(values[0])
                    self.list_tree.delete(item)

