import tkinter as tk
from tkinter import ttk
from typing import Optional
from config.constant import LAST_SELECTED_TREE_ID_NAME
from db.content_hierarchy_access import ContentHierarchyDataAccess
from event.event_bus import event_bus
from service.tree_service import TreeService
from util.config_manager import ConfigManager
from util.logger import logger
from widget.confirm_dialog import ConfirmDialog
from widget.custom_confirm_dialog import CustomConfirmDialog
from widget.input_dialog import InputDialog


class TreeManager:
    def __init__(self, main_window):
        self.root = main_window.root
        self.current_item = None
        self.main_window = main_window
        self.tree_view = main_window.directory_tree.tree
        self.config_manager = ConfigManager()
        self._setup_context_menu()
        self.update_tree_from_db()
        self.dragged_item = None
        self.floating_label = None
        self.start_drag = False
        self.tree_service = TreeService()
        self.bind_events()

    def _setup_context_menu(self):
        self.context_menu = tk.Menu(self.tree_view, tearoff=0)
        self.context_menu.add_command(label="添加节点", command=self.add_selected_item)
        self.context_menu.add_command(label="编辑节点", command=self.edit_selected_item)
        self.context_menu.add_command(label="删除节点", command=self.delete_selected_item)
        self.context_menu.add_command(label="清除预设", command=self.delete_dialogue_preset)
        self.tree_view.bind("<Button-3>", self._show_context_menu)

    def _show_context_menu(self, event):
        item = self.tree_view.identify_row(event.y)
        self.tree_view.focus(item)
        if self.current_item in self.tree_view.get_children():
            self.tree_view.item(self.current_item, tags=("normal",))
        self.current_item = item
        if item:
            is_top_node = self.tree_service.is_top_node(item)
            exist_preset = self.tree_service.exist_preset(item)
            if is_top_node:
                self.context_menu.entryconfig("删除节点", state=tk.DISABLED)
            else:
                self.context_menu.entryconfig("删除节点", state=tk.NORMAL)
            if not exist_preset:
                self.context_menu.entryconfig("清除预设", state=tk.DISABLED)
            else:
                self.context_menu.entryconfig("清除预设", state=tk.NORMAL)
            self.publish_press_event(item)
            self.tree_view.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def edit_selected_item(self):
        selected_item = self.tree_view.focus()
        tree_name  = self.tree_service.get_name_by_tree_id(selected_item)
        if selected_item:
            dialog = InputDialog(self.root, title="编辑节点", prompt="输入新名称", init_content=tree_name)
            if dialog.result:
                self.update_item(selected_item, dialog.input_content)

    def delete_selected_item(self):
        selected_item = self.tree_view.focus()
        is_top_node = self.tree_service.is_top_node(selected_item)
        if is_top_node:
            CustomConfirmDialog(parent=self.root, title="警告", message="不能删除顶层节点?")
            return
        if selected_item:
            dialog = ConfirmDialog(parent=self.root, title="删除节点", message="确定要删除该节点及下级节点吗?")
            if dialog.result:
                previous_item_id = self.get_previous_sibling_or_parent(selected_item)
                self.delete_item(selected_item)
                if previous_item_id:
                    self.tree_view.selection_set(previous_item_id)
                    self.tree_view.focus(previous_item_id)
                    self.current_item = previous_item_id

    def delete_dialogue_preset(self):
        selected_item = self.tree_view.focus()
        self.tree_service.delete_preset(selected_item)
        event_bus.publish("TreeDialoguePresetDeleted", tree_id = self.current_item)


    def get_previous_sibling_or_parent(self, item_id: str) -> Optional[str]:
        parent_id = self.tree_view.parent(item_id)
        if not parent_id:
            return None
        children = self.tree_view.get_children(parent_id)
        if item_id not in children:
            return parent_id
        current_index = children.index(item_id)
        for i in range(current_index - 1, -1, -1):
            previous_sibling_id = children[i]
            if self.tree_view.exists(previous_sibling_id):
                return previous_sibling_id
        return parent_id if parent_id else None

    def add_selected_item(self):
        selected_item = self.tree_view.focus()
        if not selected_item:
            CustomConfirmDialog(parent=self.root, title="提示", message="请先选择一个节点")
            return
        dialog = InputDialog(parent = self.root, title="新增节点", prompt="输入节点名称")
        if not dialog.result:
            return
        if dialog.input_content:
            new_item_id = self._generate_new_item_id()
            self.tree_view.item(selected_item, tags=("normal",))
            self.insert_item(parent_id=selected_item, item_id=new_item_id, name=dialog.input_content,
                             level=self._get_node_level(selected_item) + 1)
        else:
            CustomConfirmDialog(parent=self.root, title="提示", message="节点名称不能为空")

    def _generate_new_item_id(self) -> int:
        def get_max_id() -> int:
            max_id = 0
            for item_id in self.tree_view.get_children():
                max_id = max(max_id, _get_max_id_from_subtree(item_id))
            return max_id

        def _get_max_id_from_subtree(item_id: str) -> int:
            max_id = int(item_id)
            for child in self.tree_view.get_children(item_id):
                child_id = child
                try:
                    id_int = int(child_id)
                    max_id = max(max_id, id_int, _get_max_id_from_subtree(child_id))
                except ValueError:
                    pass
            return max_id

        max_existing_id = get_max_id()
        new_id = max_existing_id + 1
        return new_id

    def _get_node_level(self, item_id: str) -> int:
        level = 0
        parent = self.tree_view.parent(item_id)
        while parent:
            level += 1
            parent = self.tree_view.parent(parent)
        return level

    def set_focus_to_first_item(self):
        first_item = None
        last_selected_tree_id = self.config_manager.get(LAST_SELECTED_TREE_ID_NAME)
        if last_selected_tree_id is not None and self.tree_view.exists(last_selected_tree_id):
            first_item = last_selected_tree_id
        if first_item is None and len(self.tree_view.get_children()) > 0:
            first_item = self.tree_view.get_children()[0]
        self.tree_view.selection_set(first_item)
        self.tree_view.focus(first_item)
        self.tree_view.see(first_item)
        self.publish_press_event(first_item)

    def _insert_tree_item(self, parent_id: Optional[int], item_id: int, text: str):
        parent_item = parent_id if parent_id is not None else ''
        self.tree_view.insert(parent_item, 'end', iid=item_id, text="  " + text + "  ",
                              image=self.main_window.directory_tree.closed_folder_resized_icon)

    def insert_item(self, parent_id: Optional[int], item_id: int, name: str, level: int):
        self._insert_tree_item(parent_id, item_id, name)
        with ContentHierarchyDataAccess() as cha:
            cha.insert_data(parent_id=parent_id, child_id=item_id, name=name, level=level)
        self.expand_ancestors(item_id)
        self.publish_press_event(item_id)
        self.tree_view.selection_set(item_id)
        self.tree_view.focus(item_id)
        self.tree_view.see(item_id)

    def expand_ancestors(self, item_id: int):
        parent_id = self.tree_view.parent(item_id)
        while parent_id:
            if not self.tree_view.item(parent_id, 'open'):
                self.tree_view.item(parent_id, open=True)
            parent_id = self.tree_view.parent(parent_id)

    def update_item(self, item_id: int, name: str) -> None:
        self.tree_view.item(item_id, text="  " + name + "  ")
        with ContentHierarchyDataAccess() as cha:
            cha.update_data(child_id=item_id, name=name)

    def update_item_enhanced(self, item_id: int, new_text: str, new_parent_id: Optional[int] = None,
                             new_hierarchy_level: Optional[int] = None):
        if self.tree_view.exists(item_id):
            self.tree_view.item(item_id, text="  " + new_text + "  ")
        else:
            logger.log('warning', f"Item with ID {item_id} does not exist.")
        with ContentHierarchyDataAccess() as cha:
            cha.update_data(child_id=item_id, parent_id=new_parent_id, level=new_hierarchy_level)

    def update_tree_from_db(self):
        with ContentHierarchyDataAccess() as cha:
            data_list = cha.get_all_data()
        self.tree_view.delete(*self.tree_view.get_children())
        for item in data_list:
            parent_id = item.parent_id if item.parent_id is not None else ''
            self._insert_tree_item(parent_id, item.child_id, item.name)
        self.set_focus_to_first_item()

    def delete_item(self, item_id: int) -> None:
        self.tree_view.delete(item_id)
        with ContentHierarchyDataAccess() as cha:
            cha.delete_data(child_id=item_id)

    def find_item_by_name(self, name: str) -> Optional[str]:
        for item_id in self.tree_view.get_children():
            found_id = self._search_item(item_id, name)
            if found_id:
                return found_id
        return None

    def _search_item(self, item_id: str, name: str) -> Optional[str]:
        if self.tree_view.item(item_id, 'text') == name:
            return item_id
        for child in self.tree_view.get_children(item_id):
            found_id = self._search_item(child, name)
            if found_id:
                return found_id
        return None

    def get_selected_item_id(self) -> int | None:
        selected_item_id = self.tree_view.focus()
        if selected_item_id:
            return int(selected_item_id)
        else:
            logger.log('warning', f"No item is selected.")
            return None

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

    def on_item_press(self, event):
        dragged_item_temp = self.tree_view.identify_row(event.y)
        if not dragged_item_temp:
            return
        self.dragged_item = dragged_item_temp
        self.start_drag = False
        self.destroy_floating_label()
        self.publish_press_event(int(self.dragged_item))

    def publish_press_event(self, item):
        self.config_manager.set(LAST_SELECTED_TREE_ID_NAME, item)
        event_bus.publish("TreeItemPress", tree_id=int(item))

    def on_drag(self, event):
        if self.dragged_item and not self.start_drag:
            item_text = self.tree_view.item(self.dragged_item, 'text')
            if item_text:
                style = ttk.Style()
                style.configure("Custom.TLabel", background="#2c3e50", foreground="white", font=("Microsoft YaHei UI", 12))
                self.floating_label = ttk.Label(self.root, text=item_text)
                self.floating_label.configure(style="Custom.TLabel")
                self.start_drag = True
        if self.floating_label and self.start_drag:
            self.floating_label.place(x=event.x_root - self.root.winfo_rootx() + 10,
                                      y=event.y_root - self.root.winfo_rooty() + 10)

    def on_drop(self, event):
        target_item = self.tree_view.identify_row(event.y)
        if self.dragged_item and target_item and self.dragged_item != target_item:
            if not self.is_descendant(self.dragged_item, target_item):
                self.tree_view.move(self.dragged_item, target_item, 'end')
                new_parent_id = target_item
                new_level = self._get_node_level(target_item) + 1
                dragged_item_id = self.dragged_item
                self.update_item_enhanced(dragged_item_id, self.tree_view.item(self.dragged_item, 'text').strip(),
                                          new_parent_id=new_parent_id, new_hierarchy_level=new_level)
                self.tree_view.selection_set(dragged_item_id)
                self.tree_view.focus(dragged_item_id)
                self.tree_view.see(dragged_item_id)
                self.publish_press_event(dragged_item_id)
        if self.floating_label:
            self.destroy_floating_label()
        self.dragged_item = None
        self.start_drag = False

    def is_descendant(self, parent, child):
        children = self.tree_view.get_children(parent)
        for c in children:
            if c == child or self.is_descendant(c, child):
                return True
        return False

    def is_child(self, child, parent):
        while child:
            parent_of_child = self.tree_view.parent(child)
            if parent_of_child == parent:
                return True
            child = parent_of_child
        return False

    def is_direct_child(self, child, parent):
        parent_of_child = self.tree_view.parent(child)
        if parent_of_child == parent:
            return True
        return False

    def destroy_floating_label(self):
        if self.floating_label is not None:
            self.floating_label.destroy()
            self.floating_label = None

    def toggle_folder_icon(self, event):
        item_id = self.tree_view.focus()
        if not self.tree_view.item(item_id, 'open'):
            self.tree_view.item(item_id, image=self.main_window.directory_tree.open_folder_resized_icon)
        else:
            self.tree_view.item(item_id, image=self.main_window.directory_tree.closed_folder_resized_icon)

    def on_move_to_target_tree(self, tree_id):
        self.tree_view.selection_set(tree_id)
        self.tree_view.focus(tree_id)
        self.tree_view.see(tree_id)
        self.publish_press_event(tree_id)

    def on_dialog_preset_changed(self, preset_id, sys_messages):
        selected_item = self.tree_view.focus()
        self.tree_service.update_preset(selected_item, preset_id)

    def bind_events(self):
        self.tree_view.bind('<<TreeviewOpen>>', self.toggle_folder_icon)
        self.tree_view.bind('<<TreeviewClose>>', self.toggle_folder_icon)
        event_bus.subscribe('MoveToTargetTree', self.on_move_to_target_tree)
        event_bus.subscribe('DialogPresetChanged', self.on_dialog_preset_changed)
        self.tree_view.bind('<ButtonPress-1>', self.on_item_press)
        self.tree_view.bind('<B1-Motion>', self.on_drag)
        self.tree_view.bind('<ButtonRelease-1>', self.on_drop)
        self.tree_view.bind("<Motion>", self.on_mouse_move)
        self.tree_view.bind("<Leave>", self.on_mouse_leave)

