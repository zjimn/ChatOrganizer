
import tkinter as tk
from tkinter import ttk

class UndoRedoEntry(ttk.Entry):
    def __init__(self, master=None, placeholder="", **kwargs):
        super().__init__(master, **kwargs)
        self.history = [""]
        self.history_index = 0
        self.bind("<Control-z>", self.safe_undo)  # Ctrl+Z 撤销
        self.bind("<Control-Shift-Z>", self.safe_redo)  # Ctrl+Y 重做
        self.bind("<Key>", self.record_change)  # 记录每次输入
        self.placeholder = placeholder
        # self.bind("<FocusIn>", self.on_focus)
        self.bind("<FocusOut>", self.on_focus_out)
        self.insert(0, self.placeholder)
        # self.config(foreground='lightgrey')  # 浅色提示文字

    def record_change(self, event=None):
        # 获取当前文本内容
        current_text = self.get()
        # 如果当前内容和历史记录中最新内容不同，则记录
        if current_text != self.history[self.history_index]:
            # 限制历史记录的长度，避免内存泄漏
            if len(self.history) > 100:
                self.history.pop(0)  # 移除最旧的记录
                self.history_index -= 1  # 保证history_index不超出范围
            self.history = self.history[:self.history_index + 1]
            self.history.append(current_text)
            self.history_index += 1

    def safe_undo(self, event=None):
        if self.history_index > 0:
            self.history_index -= 1
            self.set_text(self.history[self.history_index])

    def safe_redo(self, event=None):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.set_text(self.history[self.history_index])

    def set_text(self, text):
        self.delete(0, tk.END)
        self.insert(0, text)

    # def on_focus(self, event):
    #     if self.get() == self.placeholder:
    #         #self.delete(0, tk.END)  # 清除提示文字
    #         # self.config(foreground='black')  # 设置为黑色字体

    def on_focus_out(self, event):
        if self.get() == "":
            self.insert(0, self.placeholder)  # 恢复提示文字
            # self.config(foreground='lightgrey')  # 恢复为浅色

    def update_placeholder(self, new_placeholder, clean_old = True):
        self.placeholder = new_placeholder
        if self.get() == "" or self.get() == self.placeholder or clean_old:
            self.delete(0, tk.END)
            self.insert(0, self.placeholder)
            # self.config(foreground='lightgrey')
        self.event_generate('<<UpdatePlaceholder>>', when='tail')

# 测试自定义组件
def main():
    root = tk.Tk()
    root.title("自定义UndoRedoEntry组件")

    # 使用自定义组件
    entry_widget = UndoRedoEntry(root, font=("Microsoft YaHei", 10))
    entry_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # 启动主循环
    root.mainloop()

if __name__ == "__main__":
    main()