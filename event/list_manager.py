import threading
import tkinter as tk
from tkinter import DISABLED, NORMAL
import _tkinter
from config.app_config import AppConfig
from config.constant import LAST_TYPE_OPTION_KEY_NAME, TYPE_OPTION_TXT_KEY, LAST_LIST_ORDER_BY_COLUMN, \
    LAST_LIST_SORT_ORDER_BY, PER_PAGE_COUNT_TXT, PER_PAGE_COUNT_IMG
from event.event_bus import event_bus
from event.list_editor import ListEditor
from service.content_service import ContentService
from util.image_util import open_img_replace_if_error
from util.logger import logger
from util.str_util import get_chars_by_count


class ListManager:
    def __init__(self, main_window):
        self.delay_id = None
        self.total = None
        self.data = None
        self.current_page = 1
        self.per_page_count = 20
        self.per_page_count_txt = PER_PAGE_COUNT_TXT
        self.per_page_count_img = PER_PAGE_COUNT_IMG
        self.selected_tree_id = None
        self.main_window = main_window
        self.tree = main_window.display_frame.tree
        self.app_config = AppConfig()
        self.set_tree_by_type_option()
        self.pagination_frame = main_window.display_frame.pagination_frame
        self.search_input_entry_text = main_window.display_frame.search_input_entry_text
        self.search_button = main_window.display_frame.search_button
        self.image_list = []
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.content_service = ContentService()
        self.bind_events()
        ListEditor(main_window)
        self.order_by_column = "create_time"
        self.sort_order_by = "desc"
        self.sort_reverse = {
            "id": False,
            "describe": False,
            "content": False,
            "create_time": True
        }

    def load_last_sort_order_by(self):
        order_by_column = self.app_config.get(LAST_LIST_ORDER_BY_COLUMN)
        sort_order_by = self.app_config.get(LAST_LIST_SORT_ORDER_BY)
        if order_by_column:
            self.order_by_column = order_by_column
        if sort_order_by:
            self.sort_order_by = sort_order_by

    def show_context_menu(self, event):
        iid = self.tree.identify_row(event.y)
        if iid:
            selected_item_ids = self.tree.selection()
            if len(selected_item_ids) <= 1:
                self.context_menu.entryconfig(0, state=NORMAL)
                self.tree.selection_set(iid)
            else:
                self.context_menu.entryconfig(0, state=DISABLED)
            self.context_menu.post(event.x_root, event.y_root)

    def update_txt_data_items(self, txt, selected_content_hierarchy_child_id=None, content_id=None, item_id=None,
                              sort_by=None, sort_order="asc"):
        page_number = self.current_page
        self.per_page_count = self.per_page_count_txt
        page_size = self.per_page_count
        if not content_id:
            records, count = self.content_service.load_txt_records_by_page(txt, selected_content_hierarchy_child_id,
                                                                           page_number, page_size, content_id, sort_by,
                                                                           sort_order)
            self.total = count
            self.clear_treeview()
            for index, record in enumerate(records):
                tag = self.get_tag(index)
                content = get_chars_by_count(record.content, 30)
                describe = get_chars_by_count(record.describe, 30)
                self.tree.insert("", tk.END, iid=record.id, values=(
                    record.id,
                    describe,
                    content,
                    record.create_time.strftime('%Y-%m-%d %H:%M'),
                ), tags=(tag,))
        if content_id:
            records = self.content_service.load_txt_records(txt, selected_content_hierarchy_child_id, content_id)
            if len(records) > 0:
                record = records[0]
                content = get_chars_by_count(record.content, 30)
                describe = get_chars_by_count(record.describe, 30)
                new_values = (
                    record.id,
                    describe,
                    content,
                    record.create_time.strftime('%Y-%m-%d %H:%M'),
                )
                self.update_single_item(item_id, new_values)

    def update_single_item(self, item_id, new_values, img=None):
        if img is None:
            self.tree.item(item_id, values=new_values)
        else:
            self.tree.item(item_id, image=img, values=new_values)
        self.tree.see(item_id)

    def insert_txt_data_item(self, content_id):
        records = self.content_service.load_txt_records(content_id=content_id)
        last_item = None
        for index, record in enumerate(records):
            tag = self.get_tag(index)
            last_item = self.tree.insert("", tk.END, values=(
                record.id,
                record.describe,
                get_chars_by_count(record.content),
                record.create_time.strftime('%Y-%m-%d %H:%M'),
            ), tags=(tag,))
        if last_item:
            self.tree.see(last_item)
            self.tree.focus(last_item)
            self.tree.selection_set(last_item)

    def update_data_items(self, content_id=None, item_id=None, sort_by=None, sort_order="asc"):
        if not sort_by:
            sort_by = self.order_by_column
        if not sort_order:
            sort_by = self.sort_order_by
        txt = self.search_input_entry_text.get()
        if self.app_config.get(LAST_TYPE_OPTION_KEY_NAME, TYPE_OPTION_TXT_KEY) == TYPE_OPTION_TXT_KEY:
            self.update_txt_data_items(txt, self.selected_tree_id, content_id=content_id, item_id=item_id,
                                       sort_by=sort_by, sort_order=sort_order)
        else:
            self.update_img_data_items(txt, self.selected_tree_id, content_id=content_id, item_id=item_id,
                                       sort_by=sort_by, sort_order=sort_order)

    def get_tag(self, index):
        return 'odd' if index % 2 == 0 else 'even'

    def on_mouse_move(self, event):
        item = self.tree.identify_row(event.y)
        for row in self.tree.get_children():
            tag = self.get_tag(self.tree.index(row))
            self.tree.item(row, tags=(tag,))
        if item:
            self.tree.item(item, tags=('hover',))

    def add_item(self, record, index):
        prompt = record.describe
        item = None
        try:
            img_path = record.img_path
            img_tk = open_img_replace_if_error(img_path, '', (None, 80))
            tag = self.get_tag(index)
            item = self.tree.insert("", tk.END, text="", image=img_tk,
                                    values=(
                                        "",
                                        record.id,
                                        record.img_path,
                                        record.describe,
                                        record.create_time.strftime('%Y-%m-%d %H:%M'),
                                    ), tags=(tag,))
            self.image_list.append(img_tk)
        except Exception as e:
            logger.log('error', f'Error adding item with image {prompt}:{e}')
        return item

    def update_img_data_items(self, txt, selected_content_hierarchy_child_id=None, content_id=None, item_id=None,
                              sort_by=None, sort_order="asc"):
        page_number = self.current_page
        self.per_page_count = self.per_page_count_img
        page_size = self.per_page_count
        if not content_id:
            self.clear_treeview()
            self.image_list.clear()
            records, count = self.content_service.load_img_records_by_page(txt, selected_content_hierarchy_child_id,
                                                                           page_number, page_size, content_id, sort_by,
                                                                           sort_order)
            self.total = count
            index = 0
            for record in records:
                self.add_item(record, index)
                index += 1
            self.tree.update_idletasks()
            self.tree.update()
            children = self.tree.get_children()
            if len(children) == 0:
                return
            last_item = self.tree.get_children()[-1]
        if content_id:
            records = self.content_service.load_img_records(txt, selected_content_hierarchy_child_id, content_id)
            if len(records) > 0:
                record = records[0]
                img_path = record.img_path
                img_tk = open_img_replace_if_error(img_path, '', (None, 80))
                self.image_list.append(img_tk)
                new_values = (
                    record.id,
                    record.describe,
                    record.img_path,
                    record.create_time.strftime('%Y-%m-%d %H:%M'),
                )
                self.tree.item(item_id, image=img_tk, values=new_values)

    def insert_img_data_item(self, content_id):
        records = self.content_service.load_img_records(content_id=content_id)
        index = 0
        last_item = None
        for record in records:
            last_item = self.add_item(record, index)
            index += 1
        if last_item:
            self.tree.see(last_item)
            self.tree.focus(last_item)
            self.tree.selection_set(last_item)

    def set_column_width(self, output_frame):
        frame_width = output_frame.winfo_width()
        num_columns = len(self.tree["columns"])
        if num_columns > 0:
            column_width = frame_width // num_columns
            self.tree.column("#0", width=100)
            for col in self.tree["columns"]:
                if col != "#0":
                    self.tree.column(col, width=column_width)
        self.tree.update_idletasks()
        self.tree.update()

    def on_update_list(self, *args):
        self.current_page = 1
        self.thread_update_list()

    def on_change_search_text(self, *args):
        if self.delay_id:
            self.main_window.display_frame.search_input_text.after_cancel(self.delay_id)
        self.delay_id = self.main_window.display_frame.search_input_text.after(300, self.on_update_list)

    def on_click_search_button(self, *args):
        self.on_update_list()

    def thread_update_list(self):
        threading.Thread(target=lambda: self.update_treeview(self.order_by_column, self.sort_order_by)).start()

    def on_change_type_update_list(self, type=None):
        self.set_tree_by_type_option(type)
        self.bind_tree_events()
        self.thread_update_list()

    def set_tree_by_type_option(self, type=None):
        self.main_window.display_frame.tree.pack_forget()
        if type is None:
            type = self.app_config.get(LAST_TYPE_OPTION_KEY_NAME, TYPE_OPTION_TXT_KEY)
        if type == TYPE_OPTION_TXT_KEY:
            self.tree = self.main_window.display_frame.txt_tree
        else:
            self.tree = self.main_window.display_frame.img_tree
        self.main_window.display_frame.tree = self.tree
        self.tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def on_insert_items(self, content_ids):
        view_type = self.app_config.get(LAST_TYPE_OPTION_KEY_NAME, TYPE_OPTION_TXT_KEY)
        self.set_column_width(self.main_window.output_window.output_frame)
        for content_id in content_ids:
            if view_type == TYPE_OPTION_TXT_KEY:
                self.insert_txt_data_item(content_id)
            else:
                self.insert_img_data_item(content_id)
            self.total += 1
            self.update_pagination_view()

    def on_press_tree_item(self, tree_id):
        self.selected_tree_id = tree_id

    def update_list_single_item(self, content_id, item_id):
        self.update_data_items(content_id, item_id)

    def clear_treeview(self):
        for item in reversed(self.tree.get_children()):
            if self.tree.exists(item):
                try:
                    self.tree.delete(item)
                except _tkinter.TclError as e:
                    logger.log('error', f"Error deleting item {item}: {e}")

    def sort_column(self, col):
        self.sort_reverse[col] = not self.sort_reverse[col]
        sort_order = "desc" if self.sort_reverse[col] else "asc"
        self.order_by_column = col
        self.sort_order_by = sort_order
        self.thread_update_list()

    def on_treeview_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region == "heading":
            column = self.tree.identify_column(event.x)
            if self.app_config.get(LAST_TYPE_OPTION_KEY_NAME, TYPE_OPTION_TXT_KEY) == TYPE_OPTION_TXT_KEY:
                if column == "#1":
                    self.sort_column("describe")
                elif column == "#2":
                    self.sort_column("content")
                elif column == "#3":
                    self.sort_column("create_time")
            else:
                if column == "#1":
                    self.sort_column("describe")
                elif column == "#2":
                    self.sort_column("create_time")

    def update_scrollbar_visibility(self, event=None):
        if not self.tree.get_children():
            self.main_window.display_frame.tree_txt_scrollbar.pack_forget()
            self.main_window.display_frame.tree_img_scrollbar.pack_forget()
            return
        last_item = self.tree.get_children()[-1]
        bx = self.tree.bbox(last_item)
        if bx == '' or self.tree.winfo_height() < bx[3]:
            if self.app_config.get(LAST_TYPE_OPTION_KEY_NAME, TYPE_OPTION_TXT_KEY) == TYPE_OPTION_TXT_KEY:
                self.main_window.display_frame.tree_img_scrollbar.pack_forget()
                self.main_window.display_frame.tree_txt_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            else:
                self.main_window.display_frame.tree_txt_scrollbar.pack_forget()
                self.main_window.display_frame.tree_img_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        else:
            self.main_window.display_frame.tree_txt_scrollbar.pack_forget()
            self.main_window.display_frame.tree_img_scrollbar.pack_forget()

    def update_treeview(self, sort_by=None, sort_order="asc"):
        self.update_data_items(sort_by=sort_by, sort_order=sort_order)
        if self.total <= self.per_page_count:
            self.pagination_frame.pack_forget()
        else:
            self.pagination_frame.pack(side=tk.BOTTOM, fill=tk.X)
            self.main_window.display_frame.page_label.config(text=f" {self.current_page} / {self.total_pages()} ")
            self.main_window.display_frame.prev_button.config(state=tk.NORMAL if self.current_page > 1 else tk.DISABLED)
            self.main_window.display_frame.next_button.config(
                state=tk.NORMAL if self.current_page < self.total_pages() else tk.DISABLED)
            self.main_window.display_frame.total_label.config(text=f" 共 {self.total} 条")
        self.update_scrollbar_visibility()

    def update_pagination_view(self):
        if self.total <= self.per_page_count:
            self.pagination_frame.pack_forget()
        else:
            self.pagination_frame.pack(side=tk.BOTTOM, fill=tk.X)
            self.main_window.display_frame.page_label.config(text=f" {self.current_page} / {self.total_pages()} ")
            self.main_window.display_frame.prev_button.config(state=tk.NORMAL if self.current_page > 1 else tk.DISABLED)
            self.main_window.display_frame.next_button.config(
                state=tk.NORMAL if self.current_page < self.total_pages() else tk.DISABLED)
            self.main_window.display_frame.total_label.config(text=f" 共 {self.total} 条")
        self.update_scrollbar_visibility()

    def total_pages(self):
        return (self.total + self.per_page_count - 1) // self.per_page_count

    def previous_page(self, event):
        if self.current_page > 1:
            self.current_page -= 1
            self.thread_update_list()

    def next_page(self, event):
        if self.current_page < self.total_pages():
            self.current_page += 1
            self.thread_update_list()

    def bind_tree_events(self):
        self.tree.bind("<Motion>", self.on_mouse_move)
        self.tree.bind("<Button-1>", self.on_treeview_click)
        self.tree.bind("<Configure>", lambda event: self.update_scrollbar_visibility())

    def bind_events(self):
        self.bind_tree_events()
        event_bus.subscribe('ChangeTypeUpdateList', self.on_change_type_update_list)
        self.search_input_entry_text.trace_add('write', self.on_change_search_text)
        self.search_button.bind("<Button-1>", self.on_click_search_button)
        self.main_window.directory_tree.tree.bind('<<TreeviewSelect>>', self.on_update_list)
        event_bus.subscribe('InsertListItems', self.on_insert_items)
        event_bus.subscribe('TreeItemPress', self.on_press_tree_item)
        event_bus.subscribe('UpdateListSingleItem', self.update_list_single_item)
        self.main_window.display_frame.prev_button.bind("<Button-1>", self.previous_page)
        self.main_window.display_frame.next_button.bind("<Button-1>", self.next_page)
