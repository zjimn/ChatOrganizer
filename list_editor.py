from pkgutil import get_data
from tkinter import *
from tkinter import messagebox, ttk

import tkinter as tk

from db.content_data_access import ContentDataAccess
from db.models import ContentData
from record_manager import load_data, update_data


class ListEditor:
    def __init__(self, parent, tree = None):
        self.item_data = None
        self.parent = parent
        self.listbox = Listbox(parent)
        #self.listbox.pack(padx=20, pady=20)
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.tree = tree

        # 创建上下文菜单
        self.context_menu = Menu(parent, tearoff=0)
        self.context_menu.add_command(label="修改项目", command=self.modify_selected_item)
        self.context_menu.add_command(label="删除项目", command=self.remove_selected_item)

        # 绑定右键点击事件来显示上下文菜单
        self.tree.bind("<Button-3>", self.show_context_menu)

        # 记录最后的右键点击事件位置
        self.last_event = None

        self.enable_edit_button = False

    def show_context_menu(self, event):
        # 弹出菜单项
        iid = self.tree.identify_row(event.y)
        if iid:
            selected_item_ids = self.tree.selection()
            if len(selected_item_ids) <= 1:
                self.context_menu.entryconfig(0, state=NORMAL)
                self.tree.selection_set(iid)
            else:
                self.context_menu.entryconfig(0, state=DISABLED)
            self.context_menu.post(event.x_root, event.y_root)
            self.last_event = event

    def set_show_edit_button(self, enable):
        self.enable_edit_button = enable

    def get_data(self, content_id):
        data = load_data(content_id)
        return data

    def update_item_data(self, content_id, type, describe, content):
        update_data(content_id, type, describe, content)


    def modify_selected_item(self):
        if not self.last_event:
            return  # 如果没有右键事件，返回

        # 创建新窗口
        edit_window = Toplevel(self.parent)
        edit_window.title("编辑项")
        edit_window.geometry("400x600")  # 设置窗口大小

        # 将窗口定位到鼠标点击的位置
        edit_window.geometry(f"+{self.last_event.x_root}+{self.last_event.y_root}")


        # 确定与取消按钮
        button_frame = Frame(edit_window)
        button_frame.pack(side=BOTTOM, anchor=E, padx=10, pady=10)

        def on_confirm():
            id = self.item_data.id
            type = self.item_data.type
            describe = self.item_data.describe
            content = self.item_data.content
            self.update_item_data(id, type, describe_input.get(), content_input.get('1.0', END).strip())
            edit_window.destroy()  # 关闭窗口

        def on_cancel():
            edit_window.destroy()  # 关闭窗口

        confirm_button = Button(button_frame, text="确定", command=on_confirm)
        confirm_button.pack(side=LEFT, padx=5)

        cancel_button = Button(button_frame, text="取消", command=on_cancel)
        cancel_button.pack(side=LEFT, padx=5)


        description_frame = Frame(edit_window)
        description_frame.pack(side=TOP, anchor=E, padx=10, pady=10, fill=tk.X)

        # 描述标签
        description_label = Label(description_frame, text="描述:")
        description_label.pack(side=TOP, anchor=W)

        # 单行文本输入框

        #describe_input.pack(padx=10, pady=5, fill=X)

        self.style.configure("Custom.DESCRIBE.INPUT", padding=(3, 3))
        describe_input = tk.Text(description_frame, width=30, height=1, padx=5, pady=5)
        describe_input.pack(side=tk.TOP, fill=tk.X)
        describe_input.config(font=("Microsoft YaHei", 10))



        selected_item = self.tree.selection()[0]
        list_item_values = self.tree.item(selected_item, 'values')  # Get the values of the selected item
        content_id = list_item_values[0]
        data  = self.get_data(content_id)
        describe_input.insert("1.0", data.describe)
        self.item_data = data

        # 内容标签
        content_label = Label(edit_window, text="内容:")
        content_label.pack(side=TOP, anchor=W, padx=10, pady=5)

        self.set_dialogue_list(data.dialogues, edit_window)

    def set_dialogue_list(self, data, edit_window):
        for index in range(0, len(data), 2):

            # 对话内容
            content_frame = Frame(edit_window)
            content_frame.pack(side=TOP, anchor=W, fill=tk.X, padx=10, pady=(10, 30))
            # self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=(5, 20))

            content_left_frame = Frame(content_frame)
            content_left_frame.pack(side=LEFT, anchor=W, fill=tk.X, expand=True)

            # 内容标签
            user_label = Label(content_left_frame, text="")
            #user_label.pack(side=TOP, anchor=W)
            # 多行文本输入框


            self.style.configure("Custom.DIALOGUE.USER.INPUT", padding=(3, 3))
            dialogue_user_input = tk.Text(content_left_frame, width=30, height=1, padx=5, pady=5)
            dialogue_user_input.pack(side=tk.TOP, fill=tk.X, expand=True)
            dialogue_user_input.config(font=("Microsoft YaHei", 10))
            dialogue_user_input.insert("1.0", data[index].message)

            # 内容标签
            assistant_label = Label(content_left_frame, text="")
            assistant_label.pack(side=TOP, anchor=W)
            # 多行文本输入框
            dialogue_assistant__input = Text(content_left_frame, height=5, width=30, padx=5, pady=5)
            dialogue_assistant__input.pack(side=TOP, fill=BOTH, expand=True)
            dialogue_assistant__input.insert("1.0", data[index+1].message)

            select_item_button = Button(content_frame, text="保留")
            select_item_button.pack(side=TOP, anchor=NE, padx=10)

            delete_item_button = Button(content_frame, text="删除")
            delete_item_button.pack(side=BOTTOM, anchor=SE, padx=10)

    def remove_selected_item(self):
        selected_items = self.tree.selection()
        result = messagebox.askyesno("删除数据", "确定需要删除所选数据吗?")
        if result:
            with ContentDataAccess() as cda:
                for item in selected_items:
                    values = self.tree.item(item, 'values')
                    cda.delete_data(values[0])
                    self.tree.delete(item)




# 示例使用
if __name__ == "__main__":
    root = Tk()
    list_editor = ListEditor(root)
    root.mainloop()
