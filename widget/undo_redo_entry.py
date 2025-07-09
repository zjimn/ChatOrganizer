
import tkinter as tk
from tkinter import ttk

from util.logger import logger


class UndoRedoEntry(ttk.Entry):
    def __init__(self, master=None, placeholder="", **kwargs):
        super().__init__(master, **kwargs)
        self.history = [""]
        self.history_index = 0
        self.bind("<Control-z>", self.safe_undo)  # Ctrl+Z 撤销
        self.bind("<Control-Shift-Z>", self.safe_redo)  # Ctrl+Y 重做
        self.bind("<Key>", self.record_change)
        self.bind("<KeyRelease>", self.record_change)
        self.placeholder = placeholder
        self.insert(0, self.placeholder)
        self.bind("<Button-3>", self.show_context_menu)
        self.context_menu = tk.Menu(self, tearoff=0, bd=0, relief='flat')
        self.context_menu.add_command(label="剪切", command=self.cut, state=tk.DISABLED)
        self.context_menu.add_command(label="复制", command=self.copy, state=tk.DISABLED)
        self.context_menu.add_command(label="粘贴", command=self.paste, state=tk.DISABLED)
        # self.context_menu.add_command(label="关闭", command=self.on_close_output_window)
        self.context_menu.config(borderwidth=0, relief="flat")

    def show_context_menu(self, event):
        try:
            self.selection_get()
            self.context_menu.entryconfig("剪切", state="normal")
            self.context_menu.entryconfig("复制", state="normal")
        except tk.TclError:
            self.context_menu.entryconfig("剪切", state="disabled")
            self.context_menu.entryconfig("复制", state="disabled")
        if self.clipboard_get():
            self.context_menu.entryconfig("粘贴", state="normal")
        self.context_menu.post(event.x_root, event.y_root)

    def cut(self, event=None):
        try:
            selected_text = self.selection_get()
            self.clipboard_clear()
            self.clipboard_append(selected_text)
            self.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.update()
        except tk.TclError as tcle:
            logger.log("error", f"剪切失败: {tcle}")

    def copy(self, event=None):
        try:
            selected_text = self.selection_get()
            self.clipboard_clear()
            self.clipboard_append(selected_text)
            self.update()
        except tk.TclError as tcle:
            logger.log("error", f"复制失败: {tcle}")

    def paste(self, event=None):
        try:
            clipboard_content = self.clipboard_get()
            self.insert(tk.INSERT, clipboard_content)
            self.event_generate("<Key>")
            self.event_generate("<KeyRelease>")
            self.event_generate("<<CustomKey>>")
        except tk.TclError as tcle:
            logger.log("error", f"粘贴失败: {tcle}")

    def record_change(self, event=None):
        current_text = self.get()
        if current_text != self.history[self.history_index]:
            if len(self.history) > 100:
                self.history.pop(0)
                self.history_index -= 1
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