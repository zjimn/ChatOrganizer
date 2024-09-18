import tkinter as tk
from tkinter import DISABLED, NORMAL
from PIL import Image, ImageTk
from config.constant import TYPE_OPTION_KEY_NAME, TYPE_OPTION_TXT_KEY
from config.app_config import AppConfig
from config.enum import ViewType
from event.event_bus import event_bus
from service.content_service import ContentService
from ui.syle.tree_view_style_manager import TreeViewStyleManager

from util.image_util import resize_image
from util.str_util import get_chars_by_count


class ListManager:
    def __init__(self, root, main_window):
        # Create Treeview
        self.total = None
        self.data = None
        self.current_page = 1
        self.per_page_count = 20
        self.per_page_count_txt = 20
        self.per_page_count_img = 10
        self.selected_tree_id = None
        self.main_window = main_window
        self.tree = main_window.display_frame.tree
        self.pagination_frame = main_window.display_frame.pagination_frame
        self.search_input_entry_text = main_window.display_frame.search_input_entry_text
        self.style_manager = TreeViewStyleManager(self.tree)

        self.image_list = []
        # Create context menu
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.content_service = ContentService()
        self.bind_events()
        self.app_config = AppConfig()

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

    def update_txt_data_items(self, txt, selected_content_hierarchy_child_id=None, content_id=None, item_id = None):
        page_number = self.current_page
        self.per_page_count = self.per_page_count_txt
        page_size = self.per_page_count
        self.style_manager.configure_text_style()
        # Load records and count

        if not content_id:
            records, count = self.content_service.load_txt_records_by_page(txt, selected_content_hierarchy_child_id,
                                                                           page_number, page_size, content_id)
            self.data = records
            self.total = count
            self.clear_treeview()
            # Insert records into the tree
            for index, record in enumerate(records):
                tag = self.get_tag(index)
                self.tree.insert("", tk.END, iid=record.id, values=(
                    record.id,
                    "",
                    "",
                    record.describe,
                    get_chars_by_count(record.content),
                    record.create_time.strftime('%Y-%m-%d %H:%M'),
                ), tags=(tag,))

            # Update the tree
            self.tree.update_idletasks()
            self.tree.update()

        # Update a single item if content_id is specified
        if content_id:
            records = self.content_service.load_txt_records(txt, selected_content_hierarchy_child_id, content_id)
            # Prepare new values for the item
            if len(records) > 0:
                record = records[0]
                new_values = (
                    record.id,
                    "",
                    "",
                    record.describe,
                    get_chars_by_count(record.content),
                    record.create_time.strftime('%Y-%m-%d %H:%M'),
                )
                self.update_single_item(item_id, new_values)

    def update_single_item(self, item_id, new_values, img = None):
        """
        Updates a specific item in the Treeview with new values and ensures it is visible.

        :param item_id: The unique identifier of the item to update.
        :param new_values: A tuple of new values for the item.
        """
        # Update the item with new values

        if img is None:
            self.tree.item(item_id, values=new_values)
        else:
            self.tree.item(item_id, image=img, values=new_values)
        # Ensure the item is visible
        self.tree.see(item_id)

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

    def update_data_items(self, content_id = None, item_id = None):
        self.set_column_width(self.main_window.output_window.output_frame)
        txt = self.search_input_entry_text.get()
        if self.app_config.get(TYPE_OPTION_KEY_NAME, TYPE_OPTION_TXT_KEY) == TYPE_OPTION_TXT_KEY:
            self.update_txt_data_items(txt, self.selected_tree_id, content_id = content_id, item_id = item_id)
        else:
            self.update_img_data_items(txt, self.selected_tree_id, content_id = content_id, item_id = item_id)

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

    def update_img_data_items(self, txt, selected_content_hierarchy_child_id=None, content_id = None, item_id = None):
        page_number = self.current_page
        self.per_page_count = self.per_page_count_img
        page_size = self.per_page_count
        self.style_manager.configure_image_style()

        if not content_id:
            self.clear_treeview()
            self.image_list.clear()
            records, count = self.content_service.load_img_records_by_page(txt, selected_content_hierarchy_child_id, page_number, page_size, content_id)
            self.data = records
            self.total = count

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

        # Update a single item if content_id is specified
        if content_id:
            records = self.content_service.load_img_records(txt, selected_content_hierarchy_child_id, content_id)
            # Prepare new values for the item
            if len(records) > 0:
                record = records[0]
                img_path = record.img_path
                img = Image.open(img_path)
                img = resize_image(img, (80, 80))
                img_tk = ImageTk.PhotoImage(img)

                self.image_list.append(img_tk)

                new_values = (
                    record.id,
                    "",
                    "",
                    record.describe,
                    record.img_path,
                    record.create_time.strftime('%Y-%m-%d %H:%M'),
                )

                self.update_single_item(item_id, new_values, img_tk)

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

    def on_update_list(self, event, *args):
        self.update_treeview()

    def on_insert_item(self, event):
        data = self.tree.data
        content_id = data.get("content_id")
        view_type = self.app_config.get(TYPE_OPTION_KEY_NAME, '0')
        self.set_column_width(self.main_window.output_window.output_frame)
        if self.app_config.get(TYPE_OPTION_KEY_NAME, '0') == TYPE_OPTION_TXT_KEY:
            self.insert_txt_data_item(content_id)
        elif view_type == ViewType.IMG:
            self.insert_img_data_item(content_id)

    def on_press_tree_item(self, tree_id):
        self.selected_tree_id = tree_id


    def update_list_single_item(self, content_id, item_id):
        self.update_data_items(content_id, item_id)

    def clear_treeview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)


    def update_treeview(self):
        self.update_data_items()

        if self.total <= self.per_page_count:

            self.pagination_frame.pack_forget()  # 隐藏分页控件
        else:
            # 分页显示数据
            self.pagination_frame.pack(side=tk.BOTTOM, fill=tk.X)
            # 显示分页控件
            self.main_window.display_frame.page_label.config(text=f"Page {self.current_page} of {self.total_pages()}")
            # 启用或禁用按钮
            self.main_window.display_frame.prev_button.config(state=tk.NORMAL if self.current_page > 1 else tk.DISABLED)
            self.main_window.display_frame.next_button.config(state=tk.NORMAL if self.current_page < self.total_pages() else tk.DISABLED)

            # self.paned_window.update_idletasks()  # Ensure layout is updated before placing sash
            # total_width = self.paned_window.winfo_width()  # Get the total width of the PanedWindow
            # self.paned_window.sash_place(0, 150, 0)  # Place the sash to 30% of the total width

    def total_pages(self):
        return (self.total + self.per_page_count - 1) // self.per_page_count

    def previous_page(self, event):
        if self.current_page > 1:
            self.current_page -= 1
            self.update_treeview()

    def next_page(self, event):
        if self.current_page < self.total_pages():
            self.current_page += 1
            self.update_treeview()

    def bind_events(self):
        self.tree.bind("<Motion>", self.on_mouse_move)
        self.tree.bind('<<InsertListItem>>', self.on_insert_item)
        self.tree.bind('<<UpdateList>>', self.on_update_list)
        self.search_input_entry_text.trace('w', self.on_update_list)
        self.main_window.directory_tree.tree.bind('<<TreeviewSelect>>', self.on_update_list)
        event_bus.subscribe('TreeItemPress', self.on_press_tree_item)
        event_bus.subscribe('UpdateListSingleItem', self.update_list_single_item)
        self.main_window.display_frame.prev_button.bind("<Button-1>", self.previous_page)
        self.main_window.display_frame.next_button.bind("<Button-1>", self.next_page)
