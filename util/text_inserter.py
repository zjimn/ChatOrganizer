import re
import tkinter as tk


class TextInserter:
    def __init__(self, root, text, content="", duration=1000):
        self.sections = None
        self.begin_line_number = None
        self.follow_insert = None
        self.content = content
        self.duration = duration
        self.root = root
        self.index = 0
        self.title_tag_name = "title"
        self.normal_tag_name = "normal"
        self.code_tag_name = "code"
        self.interval = self.calculate_interval()
        self.text = text
        self.text.pack(fill="both", expand=True)
        self.set_color()

    def calculate_interval(self):
        if len(self.content) == 0:
            return self.duration
        return max(1, self.duration // len(self.content))

    def get_follow_insert_state(self):
        return self.follow_insert

    def set_follow_insert_state(self, state):
        self.follow_insert = state

    def clean_bg(self):
        self.text.tag_remove(self.normal_tag_name, "1.0", tk.END)

    def set_color(self, background_color=None, foreground_color=None):
        if foreground_color is not None:
            self.text.tag_configure(self.normal_tag_name, foreground=foreground_color)
        if background_color is not None:
            self.text.tag_configure(self.normal_tag_name, background=background_color)
        if background_color is not None and foreground_color is not None:
            self.text.tag_configure(self.normal_tag_name, background=background_color, foreground=foreground_color)
        self.text.tag_configure(self.code_tag_name, background="#0d0d0d", foreground="white")
        self.text.tag_raise("sel")

    def insert_normal(self, content, font):
        self.text.tag_configure(self.title_tag_name, font=font)
        self.text.insert(tk.END, content, self.title_tag_name)


if __name__ == "__main__":
    root = tk.Tk()
    content = ('''hello''')
    duration = 5000
    text = tk.Text(root, height=10, wrap="word")
    text.pack(fill="both", expand=True)
    text_inserter = TextInserter(root, text, content, duration)
    text_inserter.set_color("#ebebeb")
    text_inserter.insert_text("\n" + content, 100, False)
    print(text_inserter.sections)
    root.mainloop()
