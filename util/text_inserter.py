import tkinter as tk
import re

from sqlalchemy.dialects.mysql import insert


class TextInserter:
    def __init__(self, root, text, content = "", duration = 1000):
        """
        初始化 TextInserter 对象。

        :param content: 要插入的文本内容
        :param duration: 总持续时间（毫秒）
        """
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
        # 根据内容长度和持续时间计算每个字符的插入间隔
        self.interval = self.calculate_interval()

        # 创建 Text 小部件
        self.text = text
        self.text.pack(fill="both", expand=True)
        self.set_color()


    def insert_text(self, content_txt = "", duration_ms = 1000, follow = True):
        self.prepare_for_start(content_txt, duration_ms, follow)
        self.insert()


    def insert_text_batch(self, content_txt = "", duration_ms = 1000, follow = True):
        self.prepare_for_start(content_txt, duration_ms, follow)
        self.insert_batch()

    def prepare_for_start(self, content_txt = "", duration_ms = 1000, follow = True):
        self.index = 0
        self.follow_insert = follow
        self.content = content_txt
        self.duration = duration_ms
        insert_index = self.text.index(tk.END + "-1c")  # 获取最新插入字符的位置
        self.begin_line_number = insert_index.split(".")[0]
        self.interval = self.calculate_interval()
        self.parse_special_sections(content_txt)

    def calculate_interval(self):
        """根据内容长度和持续时间计算每个字符的插入间隔时间。"""
        if len(self.content) == 0:
            return self.duration  # 避免除零错误，返回持续时间
        return max(1, self.duration // len(self.content))  # 防止间隔时间小于 1 毫秒


    def get_follow_insert_state(self):
        return self.follow_insert

    def set_follow_insert_state(self, state):
        self.follow_insert = state

    def clean_bg(self):
        self.text.tag_remove(self.normal_tag_name, "1.0", tk.END)


    def set_color(self, background_color = None, foreground_color = None):
        if foreground_color is not None:
            self.text.tag_configure(self.normal_tag_name, foreground=foreground_color)
        if background_color is not None:
            self.text.tag_configure(self.normal_tag_name, background=background_color)
        if background_color is not None and foreground_color is not None:
            self.text.tag_configure(self.normal_tag_name, background=background_color, foreground=foreground_color)
        self.text.tag_configure(self.code_tag_name, background="#0d0d0d", foreground="white")
        self.text.tag_raise("sel")

    def parse_special_sections(self, content):
        """解析内容，找到所有 ```...``` 段落和 - `...` 开头的文本并标记起始和结束位置"""
        self.sections = []  # 初始化 sections 列表
        # 使用正则表达式匹配 ```...``` 或 - `...` 两种模式
        matches = re.finditer(r"```(?:python)?(.*?)```|-\s`([^`]+)`", content, re.DOTALL)
        last_end = 0

        for match in matches:
            start = match.start()
            end = match.end()

            # 添加前面的普通文本部分
            self.sections.append((last_end, start, self.normal_tag_name))

            # 处理 ```...``` 和 - `...` 两种模式，删除多余的符号
            if match.group(1):  # ```...``` 模式
                special_content_start = match.start(1)  # 去掉 ```python
                special_content_end = match.end(1)  # 去掉 ```
                self.sections.append((special_content_start, special_content_end, self.code_tag_name))
            elif match.group(2):  # - `...` 模式
                special_content_start = match.start(2)  # 去掉 - `
                special_content_end = match.end(2)  # 去掉 `
                self.sections.append((special_content_start, special_content_end, self.code_tag_name))

            last_end = end  # 更新 last_end 为当前匹配结束的位置
        #for i in range(len(self.sections) - 1):
        #    self.sections[i] = (self.sections[i][0], self.sections[i + 1][0], self.sections[i][2])

        # 添加最后的普通文本部分（如果存在）
        if last_end < len(content) - 1:
            self.sections.append((last_end, len(content), self.normal_tag_name))

        return self.sections


    def start_inserting(self):
        """启动字符插入过程。"""
        self.insert()

    def insert(self):
        """逐字插入文本并应用相应的标签。"""
        self.text.config(state=tk.NORMAL)

        while self.index < len(self.content):
            # 获取当前插入字符
            current_char = self.content[self.index]

            # 获取最新插入字符的位置
            insert_index = self.text.index(tk.END + "-1c")
            line_number, index_number = insert_index.split(".")

            # 获取当前字符应应用的标签 (通过判断 self.index 所处的区间)
            for start, end, tag in self.sections:
                if start <= self.index < end:
                    self.text.insert(tk.END, current_char)
                    # 添加标签，确保每个字符都有对应的样式
                    self.text.tag_add(tag, f"{line_number}.{index_number}")
                    break

            # 如果启用 follow_insert，滚动视图到底部
            if self.follow_insert:
                self.text.yview(tk.END)

            # 移动到下一个字符
            self.index += 1

            # 按照间隔暂停插入，退出循环，并稍后调用自身继续插入
            if self.duration > 0:
                self.root.after(self.interval, self.insert)
                break
        else:
            self.text.config(state=tk.DISABLED)

    def insert_batch(self):
        """按 self.sections 遍历插入文本并应用相应的标签。"""
        self.text.config(state=tk.NORMAL)

        index = 0
        for start, end, tag in self.sections:
            index += 1
            # 获取需要插入的文本片段
            text_segment = self.content[start:end]

            # 插入文本片段
            self.text.insert(tk.END, text_segment, tag)

            if index > len(self.sections):
                start_index = self.text.index(tk.END + f"-{len(text_segment)}c")
                start_line_number, start_index_number = start_index.split(".")

                #self.text.tag_add(self.normal_tag_name, f"{start_line_number}.0", f"{start_line_number}.end")

        # 如果启用 follow_insert，滚动视图到底部
        if self.follow_insert:
            self.text.yview(tk.END)

        # 禁用文本框以防止用户修改内容
        self.text.config(state=tk.DISABLED)

    def insert_normal(self, content, font):
        self.text.tag_configure(self.title_tag_name, font = font)
        self.text.insert(tk.END, content, self.title_tag_name)

if __name__ == "__main__":
    #创建 Tkinter 根窗口
    root = tk.Tk()

    # 要插入的文本内容
    content = ("\nDanger Will ```dfdfdf```"
               "Robinson!\n"
               " You have to manage th\ne priority of tagsto get th\ne right effe\nddddddddddddddddddddddddddddddddddd\ndddddddddddddddddddddct.")
    content = ('''```
# 输入两个数
num1 = int(input("请输入第一个数："))
num2 = int(input("请输入第二个数："))

# 计算两数之和并输出
sum = num1 + num2
print("两数之和为：", sum)
```''')
    # 定义持续时间（毫秒），例如：5000 毫秒（5 秒）
    duration = 5000
    # 创建 Text 小部件
    text = tk.Text(root, height=10, wrap="word")
    text.pack(fill="both", expand=True)
    # 创建 TextInserter 对象，插入字符并在指定持续时间内完成
    text_inserter = TextInserter(root,text, content, duration)
    # 启动字符插入
    text_inserter.set_color("#ebebeb")

    text_inserter.insert_text_batch("\n" + content, 0, False)
    print(text_inserter.sections)
    text_inserter.insert_text_batch(content, 0, False)
    # 运行 Tkinter 主循环
    root.mainloop()