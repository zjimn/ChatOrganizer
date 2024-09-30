import tkinter as tk
from tkinter import ttk
from typing import Optional
from config.app_config import AppConfig
from config.constant import LAST_SELECTED_TREE_ID_NAME
from db.content_hierarchy_access import ContentHierarchyDataAccess
from ui.syle.tree_view_style_manager import TreeViewStyleManager


class EditorTreeManager:
    def __init__(self, root, edit_tree, default_selected_item=None, expand_item=None):
        self.root = root
        self.current_item = None
        self.edit_tree = edit_tree
        self.tree_view = edit_tree.tree
        self.app_config = AppConfig()
        self.style = ttk.Style()
        self.style_manager = TreeViewStyleManager(self.tree_view)
        self.style_manager.set_list_editor_tree_style()
        self.update_tree_from_db()
        self.set_default_selected(default_selected_item, expand_item)
        self.bind_events()

    def set_default_selected(self, item, expand_item):
        if item and self.tree_view.exists(item):
            if expand_item:
                self.expand_ancestors(expand_item)
                self.tree_view.selection_set(item)
                self.tree_view.focus(item)
                self.tree_view.see(item)

    def set_focus_to_first_item(self):
        selected_items = self.tree_view.selection()
        first_item = None
        last_selected_tree_id = self.app_config.get(LAST_SELECTED_TREE_ID_NAME)
        if last_selected_tree_id is not None and self.tree_view.exists(last_selected_tree_id):
            first_item = last_selected_tree_id
        if first_item is None and len(self.tree_view.get_children()) > 0:
            first_item = self.tree_view.get_children()[0]
        self.tree_view.selection_set(first_item)
        self.tree_view.focus(first_item)
        self.tree_view.see(first_item)

    def _insert_tree_item(self, parent_id: Optional[int], item_id: int, text: str):
        parent_item = parent_id if parent_id else ""
        self.tree_view.insert(parent_item, 'end', iid=item_id, text="  " + text,
                              image=self.edit_tree.closed_folder_resized_icon)

    def expand_ancestors(self, item_id: int):
        parent_id = self.tree_view.parent(item_id)
        while parent_id:
            if not self.tree_view.item(parent_id, 'open'):
                self.tree_view.item(parent_id, open=True)
            parent_id = self.tree_view.parent(parent_id)

    def update_tree_from_db(self):
        with ContentHierarchyDataAccess() as cha:
            data_list = cha.get_all_data()
        self.tree_view.delete(*self.tree_view.get_children())
        for item in data_list:
            parent_id = item.parent_id if item.parent_id is not None else ''
            self._insert_tree_item(parent_id, item.child_id, item.name)
        self.set_focus_to_first_item()

    def on_mouse_move(self, event):
        item = self.tree_view.identify_row(event.y)
        if item != self.current_item:
            if self.current_item:
                self.tree_view.item(self.current_item, tags=("normal",))
            self.current_item = item
            if self.current_item:
                self.tree_view.item(self.current_item, tags=("hover",))

    def on_mouse_leave(self, event):
        if self.current_item:
            self.tree_view.item(self.current_item, tags=("normal",))
            self.current_item = None

    def toggle_folder_icon(self, event):
        item_id = self.tree_view.focus()
        if not self.tree_view.item(item_id, 'open'):
            self.tree_view.item(item_id, image=self.edit_tree.open_folder_resized_icon)
        else:
            self.tree_view.item(item_id, image=self.edit_tree.closed_folder_resized_icon)

    def on_move_to_target_tree(self, tree_id):
        self.tree_view.selection_set(tree_id)
        self.tree_view.focus(tree_id)
        self.tree_view.see(tree_id)

    def bind_events(self):
        self.tree_view.bind('<<TreeviewOpen>>', self.toggle_folder_icon)
        self.tree_view.bind('<<TreeviewClose>>', self.toggle_folder_icon)
        self.tree_view.bind("<Motion>", self.on_mouse_move)
        self.tree_view.bind("<Leave>", self.on_mouse_leave)