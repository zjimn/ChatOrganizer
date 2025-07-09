
import tkinter as tk
from tkinter import ttk

class UndoRedoText(tk.Text):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.history = [""]
        self.history_index = 0
        self.bind("<Control-z>", self.safe_undo)  # Ctrl+Z 撤销
        self.bind("<Control-Shift-Z>", self.safe_redo)  # Ctrl+Shift+Z 重做
        self.bind("<Key>", self.record_change)
        self.bind("<KeyRelease>", self.record_change, add="+")
        self.bind("<Button-3>", self.show_context_menu)
        self.context_menu = tk.Menu(self, tearoff=0, bd=0, relief='flat')
        self.context_menu.add_command(label="剪切", command=self.cut, state=tk.DISABLED)
        self.context_menu.add_command(label="复制", command=self.copy, state=tk.DISABLED)
        self.context_menu.add_command(label="粘贴", command=self.paste)
        self.context_menu.config(borderwidth=0, relief="flat")

    def show_context_menu(self, event):
        if self.tag_ranges("sel"):
            self.context_menu.entryconfig("剪切", state=tk.NORMAL)
            self.context_menu.entryconfig("复制", state=tk.NORMAL)
        else:
            self.context_menu.entryconfig("剪切", state=tk.DISABLED)
            self.context_menu.entryconfig("复制", state=tk.DISABLED)
        state = self.cget('state') == tk.NORMAL
        if state:
            self.context_menu.entryconfig("粘贴", state=tk.NORMAL)
        else:
            self.context_menu.entryconfig("剪切", state=tk.DISABLED)
            self.context_menu.entryconfig("粘贴", state=tk.DISABLED)
        self.context_menu.post(event.x_root, event.y_root)

    def cut(self):
        self.event_generate("<<Cut>>")

    def copy(self):
        self.event_generate("<<Copy>>")

    def paste(self):
        try:
            if self.tag_ranges("sel"):
                self.delete("sel.first", "sel.last")
            clipboard_content = self.selection_get(selection="CLIPBOARD")
            self.insert("insert", clipboard_content)
            self.event_generate("<Key>")
            self.event_generate("<KeyRelease>")
            self.event_generate("<<CustomKey>>")
        except tk.TclError:
            pass

    def record_change(self, event=None):
        current_text = self.get("1.0", tk.END).strip()
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
        self.delete("1.0", tk.END)
        self.insert("1.0", text)

def main():
    root = tk.Tk()
    root.title("自定义UndoRedoText组件")

    text_widget = UndoRedoText(root, font=("Microsoft YaHei", 10), wrap="word")
    text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()