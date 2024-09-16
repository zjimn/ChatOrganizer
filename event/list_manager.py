import re
import tkinter as tk
from tkinter import ttk, messagebox, DISABLED, NORMAL
from PIL import Image, ImageTk
import service.content_service
from config.constant import TYPE_OPTION_KEY
from config.app_config import AppConfig
from db.content_data_access import ContentDataAccess
from service.content_service import ContentService
from ui.list_editor import ListEditor
from ui.syle.tree_view_style_manager import TreeViewStyleManager

from util.image_utils import resize_image
from util.str_util import get_chars_by_count


class ListManager:
    def __init__(self, root, tree):
        # Create Treeview
        self.tree = tree
        self.style_manager = TreeViewStyleManager(self.tree)
        self.list_editor = ListEditor(root, self.tree)
        self.image_list = []
        # Create context menu
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.content_service = ContentService()
        self.bind_events()
        self.system_config = AppConfig()

    def bind_events(self):
        self.tree.bind("<Motion>", self.on_mouse_move)

    def show_context_menu(self, event):
        # Show context menu
        iid = self.tree.identify_row(event.y)
        if iid:
            selected_item_ids = self.tree.selection()
            if len(selected_item_ids) <= 1:
                self.context_menu.entryconfig(0, state=NORMAL)
                self.tree.selection_set(iid)
            else:
                self.context_menu.entryconfig(0, state=DISABLED)
            self.context_menu.post(event.x_root, event.y_root)

    def update_txt_data_items(self, txt, selected_content_hierarchy_child_id=None):
        self.style_manager.configure_text_style()
        self.clear_treeview()
        records = self.content_service.load_txt_records(txt, selected_content_hierarchy_child_id)
        for index, record in enumerate(records):
            tag = self.get_tag(index)
            self.tree.insert("", tk.END, values=(
                record.id,
                "",
                "",
                record.describe,
                get_chars_by_count(record.content),
                record.create_time.strftime('%Y-%m-%d %H:%M'),
            ), tags=(tag,))
        self.tree.update_idletasks()
        self.tree.update()
        children = self.tree.get_children()
        if len(children) == 0:
            return
        last_item = self.tree.get_children()[-1]
        # Scroll to the last row
        self.tree.see(last_item)

    def insert_txt_data_item(self, content_id):
        self.style_manager.configure_text_style()
        records = self.content_service.load_txt_records(content_id=content_id)
        last_item = None
        for index, record in enumerate(records):
            tag = self.get_tag(index)
            last_item = self.tree.insert("", tk.END, values=(
                record.id,
                "",
                "",
                record.describe,
                get_chars_by_count(record.content),
                record.create_time.strftime('%Y-%m-%d %H:%M'),
            ), tags=(tag,))
        # Scroll to the last row
        if last_item:
            self.tree.see(last_item)
            self.tree.focus(last_item)
            self.tree.selection_set(last_item)

    def update_data_items(self, txt=""):
        if self.system_config.get(TYPE_OPTION_KEY, '1') == 0:
            self.update_txt_data_items(txt)
        else:
            self.update_img_data_items(txt)

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
        prompt = record.describe
        item = None
        try:
            img_path = record.img_path
            img = Image.open(img_path)
            img = resize_image(img, (80, 80))
            img_tk = ImageTk.PhotoImage(img)
            tag = self.get_tag(index)
            item = self.tree.insert("", tk.END, text="", image=img_tk,
                             values=(
                                 record.id,
                                 "",
                                 "",
                                 record.describe,
                                 record.img_path,
                                 record.create_time.strftime('%Y-%m-%d %H:%M'),
                             ), tags=(tag,))

            self.image_list.append(img_tk)

        except Exception as e:
            print(f"Error adding item with image {prompt}: {e}")
        return item

    def update_img_data_items(self, txt, selected_content_hierarchy_child_id=None):
        self.style_manager.configure_image_style()
        self.clear_treeview()
        self.image_list.clear()
        records = self.content_service.load_img_records(txt, selected_content_hierarchy_child_id)
        index = 0
        for record in records:
            self.add_item(record, index)
            index += 1
        self.tree.update_idletasks()  # Force update to ensure styles are applied
        self.tree.update()
        children = self.tree.get_children()
        if len(children) == 0:
            return
        last_item = self.tree.get_children()[-1]
        # Scroll to the last row
        self.tree.see(last_item)

    def insert_img_data_item(self, content_id):
        self.style_manager.configure_image_style()
        records = self.content_service.load_img_records(content_id=content_id)
        index = 0
        last_item = None
        for record in records:
            last_item = self.add_item(record, index)
            index += 1
        # Scroll to the last row
        if last_item:
            self.tree.see(last_item)
            self.tree.focus(last_item)
            self.tree.selection_set(last_item)


    def set_column_width(self, output_frame):
        frame_width = output_frame.winfo_width()
        num_columns = len(self.tree["columns"])
        if num_columns > 0:
            # 设置列宽
            column_width = frame_width // num_columns
            self.tree.column("#0", width=100)  # 固定宽度的列
            for col in self.tree["columns"]:
                if col != "#0":
                    self.tree.column(col, width=column_width)

        self.tree.update_idletasks()  # Force update to ensure styles are applied
        self.tree.update()


    def on_button_click(self, index):
        print(f"Button clicked for item {index}")

    def clear_treeview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)


