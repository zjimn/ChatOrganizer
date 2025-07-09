import tkinter as tk
from widget.searchable_scrolled_text import SearchableScrolledText


class TextHighlighter:
    def __init__(self, text_widget = None):
        if self.__initialized:
            return
        self.follow_insert = True
        self.in_code_block = False
        self.in_highlight = False
        self.title_tag_name = "user_input"
        self.normal_tag_name = "normal"
        self.code_tag_name = "code"
        self.special_block_tag_name = "special_block"
        self.assistant_tag_name = "assistant_response"
        if text_widget:
            self.text_widget = text_widget
            self.set_tag()
        self.signs = []
        self.in_code_block_break = False

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(TextHighlighter, cls).__new__(cls)
            cls._instance.__initialized = False
        return cls._instance

    def clean_bg(self):
        self.text_widget.tag_remove(self.normal_tag_name, "1.0", tk.END)

    def set_color(self, background_color=None, foreground_color=None):
        if foreground_color is not None:
            self.text_widget.tag_configure(self.normal_tag_name, foreground=foreground_color)
        if background_color is not None:
            self.text_widget.tag_configure(self.normal_tag_name, background=background_color)
        if background_color is not None and foreground_color is not None:
            self.text_widget.tag_configure(self.normal_tag_name, background=background_color, foreground=foreground_color)
        self.text_widget.tag_raise("sel")

    def set_text_widget(self, text_widget):
        self.text_widget = text_widget
        self.set_tag()

    def set_tag(self):
        self.text_widget.tag_configure(self.title_tag_name, foreground="black", background="white")
        self.text_widget.tag_configure(self.normal_tag_name, foreground="black", background="#e6e6e6")
        self.text_widget.tag_configure(self.code_tag_name, foreground="white", background="#1e2f3f")
        self.text_widget.tag_configure(self.special_block_tag_name, foreground="white", background="#1e2f3f")
        self.text_widget.tag_configure(self.assistant_tag_name, foreground="black", background="#e6e6e6")
        self.text_widget.tag_raise(self.special_block_tag_name)
        self.text_widget.tag_raise(self.code_tag_name)
        self.text_widget.tag_raise("sel")

    def insert_word(self, word):
        if len(self.signs) == 3:
            self.in_code_block = not self.in_code_block
            self.in_code_block_break = not self.in_code_block
            self.signs.clear()

        if word == "\n" and self.in_code_block and not self.in_code_block_break:
            self.in_code_block_break = True
            return
        if word == '`':
            self.signs.append(word)
            return

        if len(self.signs) == 1:
            self.in_highlight = not self.in_highlight
            self.signs.clear()



        if self.in_code_block and not self.in_code_block_break:
            return

        if self.in_code_block:
            self.text_widget.insert(tk.END, word, self.code_tag_name)
        elif self.in_highlight:
            self.text_widget.insert(tk.END, word, self.special_block_tag_name)
        else:
            self.text_widget.insert(tk.END, word, self.normal_tag_name)
        if self.follow_insert:
            self.text_widget.yview(tk.END)

    def batch_insert_word(self, word_list):
        for word in word_list:
            self.insert_word(word)

    def tag_to_line_end(self):
        line_end = self.text_widget.index(tk.END + " -2c")
        tags_at_end = self.text_widget.tag_names(line_end)
        insert_index = self.text_widget.index(tk.END + "-1c")
        line_number, index_number = insert_index.split(".")
        self.text_widget.tag_add(tags_at_end[0], f"{line_number}.{index_number}")

    def set_follow_insert_state(self, follow):
        self.follow_insert = follow


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
    name = '''以下是符合正常语速的字幕格式文本：  

    ```
    0:00:00.000 --> 0:00:02.500  
    大家好，我是 Jane。  

    0:00:02.500 --> 0:00:06.000  
    今天想和大家分享一下我开发的 AI 对话管理软件。  

    0:00:06.000 --> 0:00:10.500  
    首先，ChatGPT 已经发布有两三年了，  
    大家可能已经熟悉并且广泛使用它，  
    无论是在工作上还是学习中，  
    都有很大的帮助。  

    0:00:10.500 --> 0:00:14.500  
    但在实际使用过程中，大家可能也会遇到一些不太方便的地方，  
    尤其是在操作上。  

    0:00:14.500 --> 0:00:19.000  
    比如说，无论是在手机端的 APP 还是在线对话网站上，  
    用户往往无法很方便地管理对话内容。  

    0:00:19.000 --> 0:00:24.000  
    你可能想把一些特定的对话，  
    比如编程助手或翻译内容，归类到一个单独的文件夹中，  
    方便查看和管理。  

    0:00:24.000 --> 0:00:28.000  
    但目前的工具并没有提供很好的解决方案，  
    也无法支持对话内容的编辑、修改和删除。  

    0:00:28.000 --> 0:00:32.000  
    为了解决这些问题，我开发了这款软件，  
    下面我来给大家介绍一下它的功能和界面。  

    0:00:32.000 --> 0:00:36.500  
    【软件界面说明】  

    0:00:36.500 --> 0:00:41.000  
    1. **左侧面板**：这里是一个类似树形结构的面板，  
    你可以在这里添加和管理不同的节点。  

    0:00:41.000 --> 0:00:46.000  
    2. **中间展示区**：这是软件的主要信息展示区，  
    可以看到对话内容的列表，  
    双击即可打开详细记录。  

    0:00:46.000 --> 0:00:51.000  
    3. **顶部工具栏**：  
    提供常用功能，包括对话分类管理和 AI 模型配置。  

    0:00:51.000 --> 0:00:56.000  
    4. **设置界面**：  
    可选择不同的服务模式，配置 API 和模型。  

    0:00:56.000 --> 0:01:00.000  
    5. **日志记录**：  
    可用于调试和查找问题，记录详细操作信息。  

    0:01:00.000 --> 0:01:05.000  
    6. **高级设置**：  
    提供更多自定义选项，如日志输出和格式调整。  

    0:01:05.000 --> 0:01:10.000  
    7. **输入区**：  
    用于输入待处理文本，历史记录也会持续更新。  

    0:01:10.000 --> 0:01:14.500  
    【核心功能】  

    0:01:14.500 --> 0:01:18.500  
    1. **对话管理**：  
    支持历史记录的排序、搜索和分类保存。  

    0:01:18.500 --> 0:01:22.500  
    2. **节点和文件夹管理**：  
    可编辑、删除及重命名节点，并添加备注。  

    0:01:22.500 --> 0:01:27.500  
    3. **翻译和文本处理**：  
    可预设常用翻译指令或任务模板，提高效率。  

    0:01:27.500 --> 0:01:31.500  
    4. **搜索功能**：  
    快速查找对话内容，精准定位所需信息。  

    0:01:31.500 --> 0:01:35.500  
    5. **图像和文件管理**：  
    支持图片和文件的上传、查看、下载及注释。  

    0:01:35.500 --> 0:01:40.000  
    【后续计划】  

    0:01:40.000 --> 0:01:45.000  
    未来将不断优化，增加更多功能，  
    如支持更多 AI 模型、语音识别、文本转语音等。  

    0:01:45.000 --> 0:01:50.000  
    总的来说，这款软件旨在提高 AI 对话管理效率，  
    让你更轻松地分类、整理和操作对话内容。  

    0:01:50.000 --> 0:01:55.000  
    如果你有任何反馈，欢迎随时交流！  

    0:01:55.000 --> 0:01:58.000  
    谢谢大家的支持，期待你的体验和反馈！  
    ```

    这个字幕格式符合常规语速（约 150 字/分钟），确保观众能清楚理解。你可以将其直接导入视频编辑软件进行字幕同步。'''

    print(name)
    list_word = list(name)
    highlighter.batch_insert_word(list_word)

    root.mainloop()