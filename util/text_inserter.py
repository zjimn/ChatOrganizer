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

    def insert_text(self, content_txt="", duration_ms=1000, follow=True):
        self.prepare_for_start(content_txt, duration_ms, follow)
        self.insert()

    def insert_text_batch(self, content_txt="", duration_ms=1000, follow=True):
        self.prepare_for_start(content_txt, duration_ms, follow)
        self.insert_batch()

    def prepare_for_start(self, content_txt="", duration_ms=1000, follow=True):
        self.index = 0
        self.follow_insert = follow
        self.content = content_txt
        self.duration = duration_ms
        insert_index = self.text.index(tk.END + "-1c")
        self.begin_line_number = insert_index.split(".")[0]
        self.interval = self.calculate_interval()
        self.parse_special_sections(content_txt)

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

    def parse_special_sections(self, content):
        self.sections = []
        matches = re.finditer(r"```(?:python)?(.*?)```|-\s`([^`]+)`", content, re.DOTALL)
        last_end = 0
        for match in matches:
            start = match.start()
            end = match.end()
            self.sections.append((last_end, start, self.normal_tag_name))
            if match.group(1):
                special_content_start = match.start(1)
                special_content_end = match.end(1)
                self.sections.append((special_content_start, special_content_end, self.code_tag_name))
            elif match.group(2):
                special_content_start = match.start(2)
                special_content_end = match.end(2)
                self.sections.append((special_content_start, special_content_end, self.code_tag_name))
            last_end = end
        if last_end < len(content) - 1:
            self.sections.append((last_end, len(content), self.normal_tag_name))
        return self.sections

    def start_inserting(self):
        self.insert()

    def insert(self):
        self.text.config(state=tk.NORMAL)
        while self.index < len(self.content):
            current_char = self.content[self.index]
            insert_index = self.text.index(tk.END + "-1c")
            line_number, index_number = insert_index.split(".")
            for start, end, tag in self.sections:
                if start <= self.index < end:
                    self.text.insert(tk.END, current_char)
                    self.text.tag_add(tag, f"{line_number}.{index_number}")
                    break
            if self.follow_insert:
                self.text.yview(tk.END)
            self.index += 1
            if self.duration > 0:
                self.root.after(self.interval, self.insert)
                break
        else:
            self.text.config(state=tk.DISABLED)

    def insert_batch(self):
        self.text.config(state=tk.NORMAL)
        index = 0
        for start, end, tag in self.sections:
            index += 1
            text_segment = self.content[start:end]
            self.text.insert(tk.END, text_segment, tag)
            if index > len(self.sections):
                start_index = self.text.index(tk.END + f"-{len(text_segment)}c")
                start_line_number, start_index_number = start_index.split(".")
        if self.follow_insert:
            self.text.yview(tk.END)
        self.text.config(state=tk.DISABLED)

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
