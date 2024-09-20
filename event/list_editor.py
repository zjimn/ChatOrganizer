import time
from datetime import datetime
from time import sleep
from tkinter import *
from tkinter import messagebox, ttk
from PIL import Image, ImageTk

import tkinter as tk

from config.app_config import AppConfig
from config.constant import USER_NAME, ASSISTANT_NAME, TYPE_OPTION_KEY_NAME, TYPE_OPTION_TXT_KEY, \
    LAST_SELECTED_TREE_ID_NAME
from db.content_data_access import ContentDataAccess
from db.dialogue_data_access import DialogueDataAccess
from db.models import Dialogue
from event.editor_tree_manager import EditorTreeManager
from event.event_bus import event_bus
from event.tree_manager import TreeManager
from service.content_service import ContentService
from ui.directory_tree import DirectoryTree
from ui.editor_directory_tree import EditorDirectoryTree
from ui.syle.tree_view_style_manager import TreeViewStyleManager
from util import image_util
from util.ImageViewer import ImageViewer
from util.window_util import center_window


class ListEditor:
    def __init__(self, parent, main_window = None):

        self.insert_finished = None
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
        self.parent = parent
        self.listbox = Listbox(parent)
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.main_window = main_window
        self.list_tree = main_window.display_frame.tree
        self.content_service = ContentService()
        self.app_config = AppConfig()
        # 创建上下文菜单
        self.context_menu = Menu(parent, tearoff=0)
        self.context_menu.add_command(label="复制到", command=lambda: self.move_or_copy_selected_item(is_move = False))
        self.context_menu.add_command(label="移动到", command=lambda: self.move_or_copy_selected_item(is_move = True))
        self.context_menu.add_command(label="修改项", command=self.modify_selected_item)
        self.context_menu.add_command(label="删除项", command=self.remove_selected_item)
        self.dialogue_frames = []
        self.dialogue_image_labels = []
        # 绑定右键点击事件来显示上下文菜单
        self.bind_events()

        # 记录最后的右键点击事件位置
        self.last_event = None

        self.enable_edit_button = False
        self.content_service = ContentService()

    def bind_events(self):
        self.list_tree.bind("<Button-3>", self.show_context_menu)
        event_bus.subscribe('ChangeTypeUpdateList', self.on_change_type_update_list)



    def bind_tree_events(self):
        self.list_tree.bind("<Button-3>", self.show_context_menu)

    def on_change_type_update_list(self, **args):
        self.list_tree = self.main_window.display_frame.tree
        self.bind_tree_events()


    def show_context_menu(self, event):

        # 弹出菜单项
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
        # Get the dimensions of the parent window
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()

        # Calculate the position to center the window within the parent window
        x = parent_x + (parent_width // 2) - (width // 2)
        y = parent_y + (parent_height // 2) - (height // 2)

        # Set the window geometry
        window.geometry(f"{width}x{height}+{x}+{y}")


    def close_window(self):
        self.dialogue_frames.clear()
        self.item_data = []
        if self.edit_window:
            self.edit_window.destroy()  # 关闭窗口

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
        # 创建一个底部框架用于放置按钮
        button_frame = tk.Frame(self.top)
        button_frame.pack(side=tk.BOTTOM, anchor='se', pady=10)  # 放在右下角

        cancel_button = tk.Button(button_frame, text="取消", width=6, command=self.close_and_clear_data)
        cancel_button.pack(side=tk.RIGHT, padx=5)

        content_ids, tree_id = self.get_selected_list_content_ids_and_tree_id()

        self.submit_button = tk.Button(button_frame, text="确定", width=6, command=lambda: self.move_or_copy_selected(is_move, content_ids, tree_id))

        self.submit_button.pack(side=tk.RIGHT, padx=5)  # 在确定按钮的左边


        EditorTreeManager(self.parent, editor_directory_tree,  1, tree_id)

    def move_or_copy_selected(self, is_move, content_ids, tree_id):
        """处理移动选择的项目"""

        selected_tree_items = self.tree.selection()
        if selected_tree_items:
            target_tree_id = selected_tree_items[0]
            if tree_id != target_tree_id:
                event_bus.publish("MoveToTargetTree", tree_id=target_tree_id)
                self.parent.after(300, lambda: event_bus.publish("InsertListItems", content_ids=content_ids))
                if is_move:
                    self.parent.after(530, lambda: self.content_service.move_to_target_tree(content_ids, target_tree_id))
                else:
                    self.parent.after(530, lambda: self.content_service.copy_to_target_tree(content_ids, target_tree_id))

            self.close_and_clear_data()
        else:
            messagebox.showwarning("警告", "请先选择一个层级。")

    def get_selected_list_content_ids_and_tree_id(self):
        selected_items = self.list_tree.selection()
        selected_tree_id = self.app_config.get(LAST_SELECTED_TREE_ID_NAME)
        result = []
        for item in selected_items:
            list_item_values = self.list_tree.item(item, 'values')  # Get the values of the selected item

            if self.app_config.get(TYPE_OPTION_KEY_NAME, TYPE_OPTION_TXT_KEY) == TYPE_OPTION_TXT_KEY:
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
            return  # 如果没有右键事件，返回
        self.close_window()
        # 创建新窗口
        edit_window = Toplevel(self.parent)
        edit_window.title("编辑项")
        edit_window.geometry("600x500")  # 设置窗口大小
        self.edit_window = edit_window
        self.edit_window.grab_set()
        # 将窗口定位到鼠标点击的位置
        self.center_window(edit_window, 600, 500)

        # 确定与取消按钮
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
                    delete_time = delete_time
                )
                assistant_dialogue = Dialogue(
                    id=assistant_id,
                    role=ASSISTANT_NAME,
                    message=assistant_input_content,
                    img_path=assistant_img_path,
                    delete_time = delete_time
                )
                update_datas.append(user_dialogue)
                update_datas.append(assistant_dialogue)
            with ContentDataAccess() as cda:
                self.content_service.update_data(content_id, None, describe = describe, content = None, img_path = first_img_path, dialogues = update_datas)
                with DialogueDataAccess() as dda:
                    self.content_service.batch_update_dialogue_data(update_datas)

            event_bus.publish("UpdateListSingleItem", content_id = content_id, item_id = self.selected_item_id)
            self.close_window()

        def on_cancel():
            self.close_window()

        confirm_button = Button(button_frame, text="确定", width=10, command=on_confirm)
        confirm_button.pack(side=LEFT, padx=5)

        cancel_button = Button(button_frame, text="取消",width=10,  command=on_cancel)
        cancel_button.pack(side=LEFT, padx=5)


        self.description_frame = Frame(edit_window)
        self.description_frame.pack(side=TOP, anchor=E, padx=(10, 20), pady=10, fill=tk.X)

        # 描述标签
        description_label = Label(self.description_frame, text="描述:")
        description_label.pack(side=TOP, anchor=W)

        # 单行文本输入框
        selected_item = self.list_tree.selection()[0]
        list_item_values = self.list_tree.item(selected_item, 'values')  # Get the values of the selected item

        if self.app_config.get(TYPE_OPTION_KEY_NAME, TYPE_OPTION_TXT_KEY) == TYPE_OPTION_TXT_KEY:
            content_id = list_item_values[0]
        else:
            content_id = list_item_values[1]

        # Hidden label to store data[index].id
        hidden_content_id_label = Label(self.description_frame, text=content_id,
                                     fg=self.description_frame.cget('bg'))  # Same color as background
        hidden_content_id_label.pack_forget()  # Hide the label, but it's still part of the frame

        self.style.configure("Custom.DESCRIBE.INPUT", padding=(3, 3))
        self.describe_input = tk.Text(self.description_frame, height=1, padx=5, pady=5)
        self.describe_input.pack(side=tk.TOP, fill=tk.X)
        self.describe_input.config(font=("Microsoft YaHei", 10))

        self.description_frame.widgets = {
            'content_id_label': hidden_content_id_label,
            'describe_input': self.describe_input,
        }

        data  = self.get_data(content_id)
        self.describe_input.insert("1.0", data.describe)
        self.item_data = data

        # 内容标签
        content_label = Label(edit_window, text="对话:")
        content_label.pack(side=TOP, anchor=W, padx=10, pady=5)

        self.set_dialogue_list(data.dialogues, edit_window)

    def set_dialogue_list(self, data, edit_window):
        for index in range(0, len(data), 2):
            # Create content_frame for each dialogue
            content_frame = Frame(edit_window)
            content_frame.pack(side=TOP, anchor=W, fill=tk.X, padx=10, pady=(10, 30))
            self.dialogue_frames.append(content_frame)  # Store the frame for later

            content_right_frame = Frame(content_frame)
            content_right_frame.pack(side=RIGHT, anchor=E, fill=tk.Y)

            # Buttons
            select_item_button = Button(content_right_frame, text="保留", fg="#228B22",  command=lambda cf=content_frame: self.keep_only(cf, select_item_button))
            select_item_button.pack(side=TOP, anchor=NE, padx=10)
            if len(data) < 4:
                select_item_button.config(state=tk.DISABLED)
            delete_item_button = Button(content_right_frame, text="删除", fg="#B22222", command=lambda cf=content_frame: self.delete_frame(cf, select_item_button))
            delete_item_button.pack(side=tk.BOTTOM, anchor=SE, padx=10)

            content_left_frame = Frame(content_frame)
            content_left_frame.pack(side=LEFT, anchor=W, fill=tk.X, expand=True)

            # Hidden label to store data[index].id
            hidden_user_id_label = Label(content_frame, text=data[index].id, fg=content_frame.cget('bg'))  # Same color as background
            hidden_user_id_label.pack_forget()  # Hide the label, but it's still part of the frame

            hidden_assistant_id_label = Label(content_frame, text=data[index + 1].id, fg=content_frame.cget('bg'))  # Same color as background
            hidden_assistant_id_label.pack_forget()  # Hide the label, but it's still part of the frame

            # User input text box
            self.style.configure("Custom.DIALOGUE.USER.INPUT", padding=(3, 3))
            dialogue_user_input = Text(content_left_frame, width=30, height=1, padx=5, pady=5)
            dialogue_user_input.pack(side=tk.TOP, fill=tk.X)
            dialogue_user_input.config(font=("Microsoft YaHei", 10))
            dialogue_user_input.insert("1.0", data[index].message)

            # Assistant input text box
            dialogue_assistant_input = Text(content_left_frame, height=5, width=30, padx=5, pady=5)
            dialogue_assistant_input.pack_forget()
            if data[index + 1].message is not None and data[index + 1].message != '':
                dialogue_assistant_input = Text(content_left_frame, height=5, width=30, padx=5, pady=5)
                dialogue_assistant_input.pack(side=TOP, fill=tk.X)
                dialogue_assistant_input.insert("1.0", data[index + 1].message)

            hidden_assistant_img_path_label = Label(content_frame, text=data[index + 1].img_path, fg=content_frame.cget('bg'))
            hidden_assistant_img_path_label.pack_forget()
            if data[index + 1].img_path:
                img_path = data[index + 1].img_path
                img = image_util.resize_image_by_path(data[index + 1].img_path, (None, 100))
                photo = ImageTk.PhotoImage(img)
                # 创建图片显示的 Label
                image_label = Label(content_left_frame, image=photo)
                image_label.image = photo  # 保持对图片的引用，防止被垃圾回收
                # 放置图片控件
                image_label.pack(side=LEFT, pady=5, fill=tk.BOTH)
                self.dialogue_image_labels.append(image_label)
                image_viewer = ImageViewer(self.parent)
                print(f"img_path before {img_path}")
                image_label.bind("<Double-Button-1>",lambda e, image_path = img_path:  image_viewer.on_image_double_click(e, image_path, self.parent))


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
        frame.pack_forget()  # Hide the frame
        self.check_and_set_button_state(select_item_button)

    def check_and_set_button_state(self, select_item_button):
        valid_data_count = self.get_valid_data_count()
        if valid_data_count < 2:
            select_item_button.config(state=tk.DISABLED)

    def keep_only(self, frame_to_keep, select_item_button):
        select_item_button.config(state=tk.DISABLED)
        # Remove all other frames except the one to keep
        response = messagebox.askyesno(
            "Confirm",
            "确定需要保留该项删除其他项?",
            parent=self.edit_window  # Specify the parent window

        )

        if response:  # User clicked 'Yes'
            # Proceed with keeping the selected item and deleting others
            for frame in self.dialogue_frames:
                if frame != frame_to_keep:
                    frame.pack_forget()

            # Optionally, you can also perform actions specific to the kept item
            # For example: self.perform_action_on_kept_item(content_frame)
        else:  # User clicked 'No'
            # Do nothing or perform any other action
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




# 示例使用
if __name__ == "__main__":
    root = Tk()
    list_editor = ListEditor(root)
    root.mainloop()
