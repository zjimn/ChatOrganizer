
import tkinter as tk

from PIL.ImageOps import expand
from ttkbootstrap import Style

from config.constant import TOGGLE_BUTTON_CHECK_IMAGE_PATH, TOGGLE_BUTTON_UNCHECK_IMAGE_PATH
from event.event_bus import event_bus
from util.logger import Logger, logger
from util.window_util import center_window
from widget.custom_text_button import CustomTextButton
from widget.searchable_scrolled_text import SearchableScrolledText
from widget.undo_redo_entry import UndoRedoEntry
from widget.custom_slider import CustomSlider
from widget.icon_toggle_button import IconToggleButton


class HelpWindow:

    def __init__(self, root):
        self.root = root
        self.main_window = None
        self.win_width = 800
        self.win_height = 600
        event_bus.subscribe("OpenHelpWindow", self.open_help_window)

        md_text = self.read_help_file()
        if md_text:
            styled_lines = self.convert_markdown_to_text(md_text)

            # 创建新窗口显示帮助
            self.main_window = tk.Toplevel(root)
            self.main_window.title("帮助")
            self.main_window.geometry("800x600")
            self.main_window.attributes('-topmost', True)
            # 创建带滚动条的 ScrolledText 小部件来显示文本内容
            text_widget = SearchableScrolledText(self.main_window, wrap=tk.WORD, font=("Microsoft YaHei UI", 12), padx=10,
                                                 pady=10)

            # 配置标签
            text_widget.output_text.tag_configure("title1", font=("Microsoft YaHei UI", 16, "bold"))
            text_widget.output_text.tag_configure("title2", font=("Microsoft YaHei UI", 14, "bold"))
            text_widget.output_text.tag_configure("title3", font=("Microsoft YaHei UI", 12, "bold"))
            text_widget.output_text.tag_configure("list", font=("Microsoft YaHei UI", 12, "normal"))
            text_widget.output_text.tag_configure("normal", font=("Microsoft YaHei UI", 12, "normal"))

            # 将转换后的内容添加到 Text 小部件
            self.add_text_to_widget(text_widget, styled_lines)

            text_widget.output_text.config(state=tk.DISABLED)  # 允许编辑和选择文本
            text_widget.pack(fill=tk.BOTH, expand=True)


            self.main_window.withdraw()
            self.main_window.iconbitmap("res/icon/help.ico")
        self.main_window.protocol("WM_DELETE_WINDOW", self.on_cancel)

    def open_help_window(self):
        self.open()

    def open(self):
        center_window(self.main_window, self.root, self.win_width, self.win_height)
        self.main_window.deiconify()
        self.main_window.grab_set()

    def on_cancel(self):
        self.main_window.grab_release()
        self.main_window.withdraw()

    # 读取 help.md 文件内容
    def read_help_file(self):
        try:
            with open("res/doc/help.md", "r", encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError:
            logger.log('error', 'help.md 文件未找到')
            return ""

    
    # 根据 Markdown 格式调整字体粗细与大小
    def convert_markdown_to_text(self, md_text):
        lines = md_text.splitlines()
        result = []
    
        for line in lines:
            if line.startswith("# "):  # 一级标题
                result.append(('title1', line[2:]))  # 去掉 '# ' 并加粗显示
            elif line.startswith("## "):  # 二级标题
                result.append(('title2', line[3:]))  # 去掉 '## ' 并稍微小一点的粗体
            elif line.startswith("### "):  # 三级标题
                result.append(('title3', line[4:]))  # 更小的标题
            elif line.startswith("- "):  # 列表项
                result.append(('list', line[2:]))  # 列表项
            else:
                result.append(('normal', line))  # 普通文本
    
        return result
    
    
    # 将 markdown 内容添加到 Text 小部件，并根据样式调整字体
    def add_text_to_widget(self, text_widget, styled_lines):
        for style, line in styled_lines:
            if style == 'title1':  # 一级标题
                text_widget.output_text.insert(tk.END, line + "\n", "title1")
            elif style == 'title2':  # 二级标题
                text_widget.insert(tk.END, line + "\n", "title2")
            elif style == 'title3':  # 三级标题
                text_widget.output_text.insert(tk.END, line + "\n", "title3")
            elif style == 'list':  # 列表项
                text_widget.output_text.insert(tk.END, "• " + line + "\n", "list")
            else:  # 普通文本
                text_widget.output_text.insert(tk.END, line + "\n", "normal")


def main():
    root = tk.Tk()
    root.title("主窗口")
    root.geometry("300x300")
    style = Style(theme='superhero')

    open_button = tk.Button(root, text="打开设置窗口")
    open_button.pack(pady=20)
    help_window = HelpWindow(root)
    help_window.open_help_window()
    root.mainloop()

if __name__ == "__main__":
    main()


