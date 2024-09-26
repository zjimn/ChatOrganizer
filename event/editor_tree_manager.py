import tkinter as tk
from idlelib.searchengine import get_selection
from tkinter import ttk, simpledialog, messagebox
from typing import Optional

from exceptiongroup import catch

from config.app_config import AppConfig
from config.constant import LAST_SELECTED_TREE_ID_NAME
from db.content_hierarchy_access import ContentHierarchyDataAccess
from event.event_bus import event_bus
from ui.syle.tree_view_style_manager import TreeViewStyleManager


class EditorTreeManager:
    def __init__(self, root, edit_tree, default_selected_item = None, expand_item = None):
        self.root = root
        self.current_item = None
        self.edit_tree = edit_tree
        self.tree_view = edit_tree.tree
        self.app_config = AppConfig()
        self.style = ttk.Style()
        self.style_manager = TreeViewStyleManager(self.tree_view)
        self.style_manager.set_list_editor_tree_style()
        self.tree_item_press_event = "<<TreeItemPress>>"
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
        """设置焦点至顶层第一个项（如果没有选中项的话）"""
        # 检查是否已有选中的项
        selected_items = self.tree_view.selection()
        first_item = None
        last_selected_tree_id = self.app_config.get(LAST_SELECTED_TREE_ID_NAME)
        if last_selected_tree_id is not None and self.tree_view.exists(last_selected_tree_id):
            first_item = last_selected_tree_id
        if first_item is None and len(self.tree_view.get_children()) > 0:
            # 如果没有选中的项，则获取顶层第一个子项
            first_item = self.tree_view.get_children()[0]
            # 选择并设置焦点
        self.tree_view.selection_set(first_item)
        self.tree_view.focus(first_item)
        self.tree_view.see(first_item)

    def _insert_tree_item(self, parent_id: Optional[int], item_id: int, text: str):
        """Insert an item into the Treeview."""
        parent_item = parent_id if parent_id else ""
        self.tree_view.insert(parent_item, 'end', iid=item_id, text="  " + text, image = self.edit_tree.closed_folder_resized_icon)

    def expand_ancestors(self, item_id: int):
        """Expand all ancestor nodes of the given item."""
        parent_id = self.tree_view.parent(item_id)
        while parent_id:
            # Expand the parent node
            if not self.tree_view.item(parent_id, 'open'):
                self.tree_view.item(parent_id, open=True)
            # Move up to the next ancestor
            parent_id = self.tree_view.parent(parent_id)

    def update_tree_from_db(self):
        """Update the Treeview with data from the database."""
        with ContentHierarchyDataAccess() as cha:
            data_list = cha.get_all_data()

        self.tree_view.delete(*self.tree_view.get_children())

        for item in data_list:
            parent_id = item.parent_id if item.parent_id is not None else ''
            self._insert_tree_item(parent_id, item.child_id, item.name)
            #item_map[item.child_id] = parent_id
        self.set_focus_to_first_item()


    def on_mouse_move(self, event):
        # Identify the item under the mouse cursor
        item = self.tree_view.identify_row(event.y)

        # If the mouse is over a different item, update the highlight
        if item != self.current_item:
            # Remove highlight from the previous item
            if self.current_item:
                self.tree_view.item(self.current_item, tags=("normal",))

            # Add highlight to the new item
            self.current_item = item
            if self.current_item:
                self.tree_view.item(self.current_item, tags=("hover",))

    def on_mouse_leave(self, event):
        # Reset the background of the last highlighted item when mouse leaves
        if self.current_item:
            self.tree_view.item(self.current_item, tags=("normal",))
            self.current_item = None

    # Function to toggle icons on open/close event
    def toggle_folder_icon(self, event):
        # Get the currently focused item
        item_id = self.tree_view.focus()
        # Check if the item is open or closed
        if not self.tree_view.item(item_id, 'open'):
            # Set open folder icon
            self.tree_view.item(item_id, image=self.edit_tree.open_folder_resized_icon)
        else:
            # Set closed folder icon
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
        # 绑定事件

# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    tree = ttk.Treeview(root, show='tree')
    tree.pack(expand=True, fill='both')

    manager = EditorTreeManager()
    manager.update_tree_from_db()
    root.mainloop()
