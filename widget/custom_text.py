
import tkinter as tk
from tkinter import ttk

from config.constant import DEFAULT_FONT


class CustomText(tk.Text):
    def __init__(self, master=None, highlight_color = "lightgray", **kwargs):
        super().__init__(master, **kwargs)
        self.history = [""]
        self.history_index = 0
        self.bind("<Control-z>", self.safe_undo)
        self.bind("<Control-Z>", self.safe_undo)
        self.bind("<Control-Shift-z>", self.safe_redo)
        self.bind("<Control-Shift-Z>", self.safe_redo)
        self.bind("<<Modified>>", self.record_change)
        self.highlight_tag = "highlight"
        self.blinking = False
        self.remaining_blinks = 0
        self.highlight_color = highlight_color
        self.bind("<Button-3>", self.show_context_menu)
        self.context_menu = tk.Menu(self, tearoff=0, bd=0, relief='flat')
        self.context_menu.add_command(label="剪切", command=self.cut, state=tk.DISABLED)
        self.context_menu.add_command(label="复制", command=self.copy, state=tk.DISABLED)
        self.context_menu.add_command(label="粘贴", command=self.paste)
        self.context_menu.add_command(label="清空", command=self.clean_text)
        self.context_menu.add_command(label="消标", command=self.clear_added_removed_unchanged_tag)
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

        empty = self.get_data()
        if empty is not None and empty != "":
            self.context_menu.entryconfig("清空", state=tk.NORMAL)
        else:
            self.context_menu.entryconfig("清空", state=tk.DISABLED)
        exist_tag = self.exist_tag(["added", "removed", "unchanged"])
        if exist_tag:
            self.context_menu.entryconfig("消标", state=tk.NORMAL)
        else:
            self.context_menu.entryconfig("消标", state=tk.DISABLED)

        self.context_menu.post(event.x_root, event.y_root)

    def exist_menu_item(self, name):
        menu_items = [self.context_menu.entryconfig(i) for i in range(self.context_menu.index("end"))]
        for item in menu_items:
            if name in item.get("label"):
                return True
        return False
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
        except tk.TclError:
            pass

    def exist_tag(self, tags):
        for tag in tags:
            if self.tag_ranges(tag):
                return tag
        return None

    def clean_text(self):
        state = self.cget('state') == tk.NORMAL
        if not state:
            self.config(state = tk.NORMAL)
        self.delete("1.0", tk.END)
        if not state:
            self.config(state=tk.DISABLED)

    def clear_added_removed_unchanged_tag(self):
        self.clear_tag("added")
        self.clear_tag("removed")
        self.clear_tag("unchanged")

    def record_change(self, event=None):
        current_text = self.get_data()
        if len(self.history) == 0 or current_text != self.history[self.history_index]:
            if len(self.history) > 200:
                self.history.pop(1)
                self.history_index -= 1
            self.history = self.history[:self.history_index + 1]
            self.history.append(current_text)
            self.history_index += 1
        if len(self.history) > 1:
            self.event_generate("<<ModifyText>>")
        self.edit_modified(False)

    def cancel_listen_modified_event(self):
        self.unbind("<<Modified>>")

    def listen_modified_event(self):
        self.bind("<<Modified>>", self.record_change)

    def safe_undo(self, event=None):
        if self.history_index > 0:
            self.history_index -= 1
            self.set_text(self.history[self.history_index])

    def safe_redo(self, event=None):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.set_text(self.history[self.history_index])

    def set_text(self, text):
        curor_position = self.index(tk.INSERT)
        curr_position = self.yview()[0]
        self.delete("1.0", tk.END)
        self.insert("1.0", text)
        self.yview_moveto(curr_position)
        self.mark_set(tk.INSERT, curor_position)
        self.see(curor_position)

    def is_modified(self):
        data = self.get_data()
        return not (len(self.history) == 0 or (len(self.history) > 0 and self.history[0] == data))

    def freeze_history(self):
        self.history = []
        self.history_index = -1

    def highlight_line(self, line_num, frequency=500, times=5):
        self.stop_blinking()
        self.tag_configure(self.highlight_tag, background= self.highlight_color)
        self.remaining_blinks = times * 2
        self.blinking = True
        self._start_blinking(line_num, frequency)

    def _start_blinking(self, line_num, frequency):
        if self.blinking and self.remaining_blinks > 0:
            self._toggle_highlight(line_num)
            self.remaining_blinks -= 1
            self.after(frequency, self._start_blinking, line_num, frequency)
        else:
            self.stop_blinking()

    def _toggle_highlight(self, line_num):
        self.sign_tag(line_num,self.highlight_tag)

    def sign_tag(self, line_num, tag, remove_exist_tag = False, remove_all_tag = False):
        if remove_exist_tag:
            self.tag_remove(tag, "1.0", tk.END)
        if remove_all_tag:
            current_tags = self.tag_names(f"{line_num}.0")
            for t in current_tags:
                self.tag_remove(t, f"{line_num}.0", f"{line_num + 1}.0")
        self.tag_add(tag, f"{line_num}.0", f"{line_num + 1}.0")

    def clear_tag(self, tag):
        self.tag_remove(tag, "1.0", tk.END)

    def clear_all_tags(self):
        all_tags = self.tag_names()
        for tag in all_tags:
            self.tag_remove(tag, "1.0", "end")

    def stop_blinking(self):
        self.blinking = False
        self.remaining_blinks = 0
        self.tag_remove(self.highlight_tag, "1.0", "end")

    def get_data(self):
        text = self.get("1.0", tk.END)
        if text.endswith("\n"):
            # Return the text without the last newline
            return text[:-1]
        return text

def main():
    root = tk.Tk()
    root.title("自定义Text组件")

    text_widget = CustomText(root, highlight_color="yellow", font=(DEFAULT_FONT, 10), wrap="word")
    text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    for i in range(1, 21):
        text_widget.insert("end", f"这是第 {i} 行文本\n")

    text_widget.highlight_line(20, frequency=300, times=6)
    root.mainloop()

if __name__ == "__main__":
    main()
