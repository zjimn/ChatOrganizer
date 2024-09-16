import tkinter as tk
from idlelib.searchengine import get_selection
from tkinter import ttk, simpledialog, messagebox
from typing import Optional

from db.content_hierarchy_access import ContentHierarchyDataAccess


class HierarchyTreeManager:
    def __init__(self, main_window):
        self.current_item = None
        self.pre_selected_item = None
        self.main_window = main_window
        self.tree_view = main_window.dir_tree
        self.update_tree_from_db()
        self._setup_context_menu()
        self.style = ttk.Style()
        self.set_style()
        self.tree_view.bind("<Motion>", self.on_mouse_move)
        self.tree_view.bind("<Leave>", self.on_mouse_leave)

        # 绑定事件
        self.tree_view.bind('<ButtonPress-1>', self.on_item_press)
        self.tree_view.bind('<B1-Motion>', self.on_drag)
        self.tree_view.bind('<ButtonRelease-1>', self.on_drop)
        self.tree_item_press_event = "<<TreeItemPress>>"

        self.dragged_item = None
        self.floating_label = None
        self.start_drag = False  # 标记是否开始拖动


    def set_style(self):
        self.style.map('Tree.Treeview', background=[('selected', '#add8e6')])
        self.style.map('Tree.Treeview', foreground=[('selected', 'white')])
        self.style.configure('Tree.Treeview',
                        rowheight=40, font=("Arial", 12),
                        padding=(5, 10, 5, 10),
                        fieldbackground = 'white',
                        background='white',  # Background color for the entire treeview
                        foreground='#0d0d0d',  # Font color
                        bordercolor = '#cccccc',  # 设置列之间的竖线颜色
                        borderwidth = 10,
                        highlightthickness=1,  # 设置高亮边框厚度
                        bd=1,  # 设置边框宽度
                        #relief = 'solid'  # 使用 solid 来显示边框
                             )
        self.tree_view.tag_configure('normal', background='white', foreground='#0d0d0d')
        self.tree_view.tag_configure('hover', background='#e8eaed', foreground='#0d0d0d')
        self.style.map('Tree.Treeview', background=[('selected', '#e8f0fe')])
        self.style.map('Tree.Treeview', foreground=[('selected', '#1a73e8')])

    def _setup_context_menu(self):
        """Set up the context menu for the Treeview."""
        self.context_menu = tk.Menu(self.tree_view, tearoff=0,font=('Helvetica', 12))
        self.context_menu.add_command(label="添加", command=self.add_selected_item)
        self.context_menu.add_command(label="编辑", command=self.edit_selected_item)
        self.context_menu.add_command(label="删除", command=self.delete_selected_item)

        self.tree_view.bind("<Button-3>", self._show_context_menu)

    def _show_context_menu(self, event):
        """Show the context menu on right-click."""
        self.generate_press_event()
        item = self.tree_view.identify_row(event.y)
        self.tree_view.focus(item)
        self.tree_view.item(self.current_item, tags=("normal",))
        self.current_item = item
        if item:
            self.tree_view.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def edit_selected_item(self):
        selected_item = self.tree_view.focus()
        if selected_item:
            # Implement your edit logic here
            new_name = simpledialog.askstring("编辑节点", "输入新名称:")
            if new_name:
                self.update_item(selected_item, new_name)

    def delete_selected_item(self):
        selected_item = self.tree_view.focus()
        if selected_item:
            # Confirm deletion
            result = messagebox.askyesno("删除节点", "确定需要删除该节点及下级节点吗?")
            if result:
                # Find the previous sibling or parent to select after deletion
                previous_item_id = self.get_previous_sibling_or_parent(selected_item)

                # Delete the selected item
                self.delete_item(selected_item)

                # Automatically select the previous item if it exists
                if previous_item_id:
                    self.tree_view.selection_set(previous_item_id)
                    self.tree_view.focus(previous_item_id)
                    self.current_item = previous_item_id

    def get_previous_sibling_or_parent(self, item_id: str) -> Optional[str]:
        """Find the previous sibling of the item, or if none, the parent."""
        parent_id = self.tree_view.parent(item_id)
        if not parent_id:
            # If the item has no parent, it's the root node
            return None

        children = self.tree_view.get_children(parent_id)

        # Check if the current item is in the list of children
        if item_id not in children:
            return parent_id  # Return parent if current item is not found in children

        # Find the index of the current item in the parent's children
        current_index = children.index(item_id)

        # Iterate backwards to find a valid previous sibling
        for i in range(current_index - 1, -1, -1):
            previous_sibling_id = children[i]
            # Check if the previous sibling ID is valid (e.g., ensure it exists in the tree)
            if self.tree_view.exists(previous_sibling_id):
                return previous_sibling_id

        # No valid previous sibling found, return the parent
        return parent_id if parent_id else None

    def add_selected_item(self):
        """Handle the logic to add a new node."""
        selected_item = self.tree_view.focus()
        if not selected_item:
            messagebox.showinfo("Info", "Please select a node where you want to add a new node.")
            return

        new_node_name = simpledialog.askstring("输入", "输入新增的节点名称:")
        if new_node_name is None:
            # 用户点击了取消或关闭了对话框
            return
        if new_node_name:
            new_item_id = self._generate_new_item_id()
            self.tree_view.item(selected_item, tags=("normal",))
            self.insert_item(parent_id=selected_item, item_id=new_item_id, name=new_node_name,
                             level=self._get_node_level(selected_item) + 1)
        else:
            messagebox.showwarning("提示", "节点名称不能为空.")

    def _generate_new_item_id(self) -> int:
        """Generate a new unique item ID across all nodes in the Treeview."""

        def get_max_id() -> int:
            """Find the maximum existing item ID across all nodes."""
            max_id = 0  # Start with 0 if no items exist
            for item_id in self.tree_view.get_children():
                max_id = max(max_id, _get_max_id_from_subtree(item_id))
            return max_id

        def _get_max_id_from_subtree(item_id: str) -> int:
            """Recursively find the maximum item ID under the given item_id."""
            max_id = int(item_id)  # Start with the current item's ID
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
        """Get the level of a given node."""
        level = 0
        parent = self.tree_view.parent(item_id)
        while parent:
            level += 1
            parent = self.tree_view.parent(parent)
        return level

    def set_focus_to_first_item(self):
        """设置焦点至顶层第一个项（如果没有选中项的话）"""
        # 检查是否已有选中的项
        selected_items = self.tree_view.selection()
        if not selected_items:
            # 如果没有选中的项，则获取顶层第一个子项
            first_item = self.tree_view.get_children()[0]
            # 选择并设置焦点
            self.tree_view.selection_set(first_item)
            self.tree_view.focus(first_item)

    def _insert_tree_item(self, parent_id: Optional[int], item_id: int, text: str):
        """Insert an item into the Treeview."""
        parent_item = parent_id if parent_id else ""
        self.tree_view.insert(parent_item, 'end', iid=item_id, text="  " + text, image = self.main_window.closed_folder_resized_icon)

    def insert_item(self, parent_id: Optional[int], item_id: int, name: str, level: int):
        """Insert an item into the Treeview and database."""
        self._insert_tree_item(parent_id, item_id, name)
        with ContentHierarchyDataAccess() as cha:
            cha.insert_data(parent_id=parent_id, child_id=item_id, name=name, level=level)
        # Expand all parent nodes of the newly added item
        self.expand_ancestors(item_id)

        # Automatically select and focus the newly added item

        self.tree_view.selection_set(item_id)
        self.tree_view.focus(item_id)
        self.tree_view.see(item_id)

    def expand_ancestors(self, item_id: int):
        """Expand all ancestor nodes of the given item."""
        parent_id = self.tree_view.parent(item_id)
        while parent_id:
            # Expand the parent node
            if not self.tree_view.item(parent_id, 'open'):
                self.tree_view.item(parent_id, open=True)
            # Move up to the next ancestor
            parent_id = self.tree_view.parent(parent_id)

    def update_item(self, item_id: int, name: str) -> None:
        """Update an item in the Treeview and database."""
        self.tree_view.item(item_id, text=name)

        with ContentHierarchyDataAccess() as cha:
            cha.update_data(child_id=item_id, name=name)

    def update_item_enhanced(self, item_id: int, new_text: str, new_parent_id: Optional[int] = None,
                             new_hierarchy_level: Optional[int] = None):
        """Update the text of an existing item in the Treeview and database."""
        if self.tree_view.exists(item_id):
            self.tree_view.item(item_id, text="  " + new_text)
        else:
            print(f"Item with ID {item_id} does not exist.")

        with ContentHierarchyDataAccess() as cha:
            cha.update_data(child_id=item_id, parent_id=new_parent_id, level=new_hierarchy_level)

    def update_tree_from_db(self):
        """Update the Treeview with data from the database."""
        with ContentHierarchyDataAccess() as cha:
            data_list = cha.get_all_data()

        self.tree_view.delete(*self.tree_view.get_children())
        item_map = {}

        for item in data_list:
            parent_id = item.parent_id if item.parent_id is not None else ''
            self._insert_tree_item(parent_id, item.child_id, item.name)
            item_map[item.child_id] = parent_id
        self.set_focus_to_first_item()

    def delete_item(self, item_id: int) -> None:
        """Delete an item from the Treeview and database."""
        self.tree_view.delete(item_id)

        with ContentHierarchyDataAccess() as cha:
            cha.delete_data(child_id=item_id)

    def find_item_by_name(self, name: str) -> Optional[str]:
        """Find an item by its name."""
        for item_id in self.tree_view.get_children():
            found_id = self._search_item(item_id, name)
            if found_id:
                return found_id
        return None

    def _search_item(self, item_id: str, name: str) -> Optional[str]:
        """Recursively search items for a matching name."""
        if self.tree_view.item(item_id, 'text') == name:
            return item_id
        for child in self.tree_view.get_children(item_id):
            found_id = self._search_item(child, name)
            if found_id:
                return found_id
        return None

    def get_selected_item_id(self) -> int | None:
        """Get the ID of the currently selected item in the Treeview."""
        selected_item_id = self.tree_view.focus()
        if selected_item_id:
            print(f"Selected item ID: {selected_item_id}")
            return int(selected_item_id)
        else:
            print("No item is selected.")
            return None

            
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



    def on_item_press(self, event):
        selected_item = self.get_selected_item_id()
        self.generate_press_event()
        # 获取被点击的项目
        self.dragged_item = self.tree_view.identify_row(event.y)
        self.start_drag = False  # 重置拖动状态
        self.destroy_floating_label()

    def generate_press_event(self):
        self.tree_view.event_generate(self.tree_item_press_event, data=self.dragged_item)

    def on_drag(self, event):
        # 检查是否有项目被点击
        if self.dragged_item and not self.start_drag:
            # 开始拖动，创建浮动标签
            item_text = self.tree_view.item(self.dragged_item, 'text')
            if item_text:  # 确保 item_text 不为空
                self.floating_label = tk.Label(self.main_window.root, text=item_text, bg='lightgrey', relief='flat')
                self.start_drag = True  # 更新拖动状态

        # 拖动过程中移动浮动标签
        if self.floating_label and self.start_drag:
            # 更新浮动标签的位置
            self.floating_label.place(x=event.x_root - self.main_window.root.winfo_rootx() + 10,
                                      y=event.y_root - self.main_window.root.winfo_rooty() + 10)

    def on_drop(self, event):
        # 获取目标位置
        target_item = self.tree_view.identify_row(event.y)

        if self.dragged_item and target_item:
            # 如果目标不是自己，也不是自己的子项
            if target_item != self.dragged_item and not self.is_direct_child(self.dragged_item, target_item):
                # Move the dragged item to the new position in the Treeview
                self.tree_view.move(self.dragged_item, target_item, 'end')

                # Get new parent ID and level
                new_parent_id = target_item  # Assuming text contains the ID
                new_level = self._get_node_level(target_item) + 1

                # 获取拖拽项的ID
                dragged_item_id = self.dragged_item  # Assuming text contains the ID

                # Update the item in Treeview and database
                self.update_item_enhanced(dragged_item_id, self.tree_view.item(self.dragged_item, 'text').strip(),
                                          new_parent_id=new_parent_id, new_hierarchy_level=new_level)

        # 删除浮动标签
        if self.floating_label:
            self.destroy_floating_label()

        # 重置拖动项目
        self.dragged_item = None
        self.start_drag = False

    def is_child(self, child, parent):
        # 检查是否是子项
        while child:
            parent_of_child = self.tree_view.parent(child)
            if parent_of_child == parent:
                return True
            child = parent_of_child
        return False

    def is_direct_child(self, child, parent):
        # 获取子项的直接父项
        parent_of_child = self.tree_view.parent(child)

        # 检查该父项是否是目标父项
        if parent_of_child == parent:
            return True
        return False

    def destroy_floating_label(self):
        if self.floating_label is not None:
            self.floating_label.destroy()
            self.floating_label = None


            
# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    tree = ttk.Treeview(root, show='tree')
    tree.pack(expand=True, fill='both')

    manager = HierarchyTreeManager()
    manager.update_tree_from_db()
    root.mainloop()
