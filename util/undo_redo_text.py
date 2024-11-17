
import tkinter as tk
from tkinter import ttk

class UndoRedoText(tk.Text):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.history = [""]
        self.history_index = 0
        self.bind("<Control-z>", self.safe_undo)  # Ctrl+Z 撤销
        self.bind("<Control-Shift-Z>", self.safe_redo)  # Ctrl+Shift+Z 重做
        self.bind("<KeyRelease>", self.record_change)  # 记录每次输入

    def record_change(self, event=None):
        # 获取当前文本内容
        current_text = self.get("1.0", tk.END).strip()
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
        self.delete("1.0", tk.END)
        self.insert("1.0", text)

# 测试自定义组件
def main():
    root = tk.Tk()
    root.title("自定义UndoRedoText组件")

    # 使用自定义组件
    text_widget = UndoRedoText(root, font=("Microsoft YaHei", 10), wrap="word")
    text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # 启动主循环
    root.mainloop()

if __name__ == "__main__":
    main()