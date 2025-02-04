import tkinter as tk
from widget.searchable_scrolled_text import SearchableScrolledText


class TextHighlighter:
    def __init__(self, text_widget = None):
        if text_widget:
            self.text_widget = text_widget
            self.text_widget.tag_configure("highlight", foreground="white", background="black")
            self.text_widget.tag_configure("code", foreground="white", background="black")
        self.in_code_block = False
        self.in_highlight = False

        self.signs = []

        self.in_code_block_break = False

    def set_text_widget(self, text_widget):
        self.text_widget = text_widget
        self.set_tag()

    def set_tag(self):
        self.text_widget.tag_configure("highlight", foreground="white", background="black")
        self.text_widget.tag_configure("code", foreground="white", background="black")

    def insert_word(self, word):
        if word == "\n" and self.in_code_block and not self.in_code_block_break:
            self.in_code_block_break = True
            return

        if word == '`':
            self.signs.append(word)
            return

        if len(self.signs) == 1:
            self.in_highlight = not self.in_highlight
            self.signs.clear()

        if len(self.signs) == 3:
            self.in_code_block = not self.in_code_block
            self.in_code_block_break = not self.in_code_block
            self.signs.clear()

        if self.in_code_block and not self.in_code_block_break:
            return

        if self.in_code_block:
            self.text_widget.insert(tk.END, word, "code")
        elif self.in_highlight:
            self.text_widget.insert(tk.END, word, "highlight")
        else:
            self.text_widget.insert(tk.END, word)

    def insert_text(self, word_list):
        for word in word_list:
            self.insert_word(word)

if __name__ == "__main__":
    # 创建窗口
    root = tk.Tk()
    root.title("文本高亮工具")
    text_component = SearchableScrolledText(root, wrap=tk.WORD, state=tk.NORMAL)
    text_component.pack(fill=tk.BOTH, expand=True)
    text_widget = text_component.output_text
    text_widget.config(font=("Microsoft YaHei", 12), padx=10, pady=10)
    text_widget.pack()
    # 创建TextHighlighter实例
    highlighter = TextHighlighter()
    highlighter.set_text_widget(text_widget)

    # 示例单词列表，模拟逐个单词传入
    example_words = ["```", "普通文本", "\n", "这里是code",  "```", "这里", "是", "`包围的文本`", "，", "这里", "是", "代码块：", "```python```",
                     "print('Hello World')", "```", "继续文本", "```", "结束"]

    highlighter.insert_text(example_words)

    root.mainloop()