
import tkinter as tk
from tkinter import ttk

class CustomListbox(tk.Listbox):
    def __init__(self, parent, padx=1, pady=1, enable_drag = True, **kwargs):
        super().__init__(parent, **kwargs)
        self.timer_id = None
        self.padx = padx
        self.pady = pady
        self.items = []
        self.bind('<Button-1>', self.on_start_click)
        self.bind('<B1-Motion>', self.on_drag_motion)
        self.bind('<ButtonRelease-1>', self.on_drop)
        self.enable_drag = enable_drag
        self.start_index = None
        self.drag_window = None
        self.dragging = False
        self.dragging_index = None

    def on_start_click(self, event):
        self.start_index = self.nearest(event.y)
        if self.enable_drag and self.start_index is not None:
            self.timer_id = self.after(400, self.create_drag_label, event)


    def create_drag_label(self, event):
        if not self.enable_drag or self.start_index is None:
            return
        self.dragging_index = self.start_index
        if self.timer_id:
            self.timer_id = None
            item_text = self.get((self.start_index, ))
            self.drag_window = tk.Toplevel(self.master)
            self.drag_window.overrideredirect(True)
            self.drag_window.geometry(f"+{event.x_root}+{event.y_root}")

            drag_label = ttk.Label(self.drag_window, text=item_text, relief="flat")

            drag_label.pack()

    def on_drag_motion(self, event):
        if not self.enable_drag:
            return
        if self.timer_id:
            self.after_cancel(self.timer_id)
            self.timer_id = None
        if self.dragging_index is None:
            return

        if self.drag_window:
            x = self.master.winfo_pointerx()
            y = self.master.winfo_pointery()
            self.drag_window.geometry(f"+{x}+{y}")
            self.dragging = True

    def on_drop(self, event):
        if not self.enable_drag:
            return
        target_index = self.nearest(event.y)
        if self.dragging_index is not None and self.drag_window:
            item_text = self.drag_window.winfo_children()[0].cget("text")
            self.selection_clear(0, tk.END)
            self.delete(self.dragging_index)
            self.insert(target_index, item_text)
            self.selection_set(target_index)
        if self.drag_window:
            self.drag_window.destroy()
            self.drag_window = None
        self.dragging_index = None
        self.start_index = None
        self.dragging = False

    def is_dragging_item(self):
        return self.dragging

    def insert(self, index, *elements):
        if index == tk.END:
            index = self.size()

        for element in elements:
            padded_item = f"{' ' * self.padx}{element}{' ' * self.padx}"
            super().insert(index, padded_item)
            self.items.insert(index, element)
            index += 1

    def set_padding(self, padx, pady):
        self.padx = padx
        self.pady = pady
        self.redraw_items()

    def redraw_items(self):
        for i in range(self.size()):
            original_item = self.items[i]
            self.delete(i)
            padded_item = f"{' ' * self.padx}{original_item}{' ' * self.padx}"
            self.insert(i, padded_item)

    def get(self, item, last=None):
        if not item or len(item) == 0:
            return None
        first = item[0]
        if last is None:
            return self.items[first]
        else:
            return tuple(self.items[i] for i in range(first, last))

    def delete(self, index, last=None):
        if last == tk.END:
            last = self.size() - 1
        if last is None:
            super().delete(index)
            del self.items[index]
        else:
            for i in range(index, last + 1):
                super().delete(index)
                del self.items[index]


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Draggable Listbox with Label")

    # 创建 Listbox
    listbox = CustomListbox(root, selectmode=tk.SINGLE, height=10)
    listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # 添加示例数据
    for i in range(1, 11):
        listbox.insert(tk.END, f"Item {i}")

    # 运行主循环
    root.mainloop()