import tkinter as tk

class UndoRedoText(tk.Text):
    def __init__(self, master=None, **kwargs):
        kwargs['undo'] = True
        super().__init__(master, **kwargs)

        self.bind("<Control-z>", self.safe_undo)  # Ctrl+Z 撤销
        self.bind("<Control-Shift-Z>", self.safe_redo)  # Ctrl+Shift+Z 重做
        self.bind("<Control-y>", self.safe_redo)  # Ctrl+Y 重做

    def safe_undo(self, event=None):
        try:
            self.edit_undo()
        except tk.TclError:
            pass

    def safe_redo(self, event=None):
        try:
            self.edit_redo()
        except tk.TclError:
            pass

# 测试自定义组件
def main():
    root = tk.Tk()
    root.title("自定义UndoRedoText组件")

    # 使用自定义组件
    text_widget = UndoRedoText(root, width=40, height=10, padx=5, pady=5, font=("Microsoft YaHei", 10))
    text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # 启动主循环
    root.mainloop()

if __name__ == "__main__":
    main()
