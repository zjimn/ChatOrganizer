import tkinter as tk
from tkinter import ttk


class SubmitButton:
    def __init__(self, root):
        # 初始化窗口
        self.root = root
        self.root.title("切换按钮状态")

        # 初始样式和状态
        self.initial_text = "获取回答"
        self.changed_text = "⬛"
        self.initial_fg = "black"
        self.initial_bg = "lightgray"
        self.changed_fg = "white"
        self.changed_bg = "blue"
        self.hover_bg = "lightblue"
        self.click_bg = "darkblue"
        self.is_changed = False

        # 创建样式
        self.style = ttk.Style()
        self.style.configure("TButton", foreground=self.initial_fg, background=self.initial_bg)
        self.style.theme_use('clam')
        # 创建框架和按钮
        self.bottom_frame = ttk.Frame(self.root)
        self.bottom_frame.pack(pady=20)
        self.submit_button = ttk.Button(self.bottom_frame, text=self.initial_text, command=self.on_button_click)
        self.submit_button.pack()

        # 绑定鼠标事件（悬停、点击、离开）
        self.submit_button.bind("<Enter>", self.on_hover)
        #self.submit_button.bind("<Leave>", self.on_leave)
        #self.submit_button.bind("<ButtonRelease-1>", self.on_release)

    def on_button_click(self):
        # 切换按钮状态和样式
        if self.is_changed:
            # 恢复初始状态
            self.submit_button.config(text=self.initial_text)
            self.style.configure("TButton", foreground=self.initial_fg, background=self.initial_bg)
        else:
            # 改为 "⬛" 并修改样式
            self.submit_button.config(text=self.changed_text)
            self.style.configure("TButton", foreground=self.changed_fg, background=self.changed_bg)

        # 切换状态
        self.is_changed = not self.is_changed

    def on_hover(self, event):
        # 鼠标悬停时改变背景颜色

        if self.is_changed:
            self.submit_button.config(style="Hover.TButton")
            self.style.configure("Hover.TButton", background="black", foreground="white")
        else:
            self.submit_button.config(style="Hover.TButton")
            self.style.configure("Hover.TButton", background="black", foreground="white")

    def on_leave(self, event):
        # 鼠标离开时恢复按钮的原始样式
        if self.is_changed:
            self.submit_button.config(style="TButton")
            self.style.configure("TButton", foreground=self.changed_fg, background=self.changed_bg)
        else:
            self.submit_button.config(style="TButton")
            self.style.configure("TButton", foreground=self.initial_fg, background=self.initial_bg)


    def on_release(self, event):
        # 鼠标释放时恢复到悬停状态或正常状态
        if self.is_changed:
            self.submit_button.config(style="TButton")
            self.style.configure("TButton", foreground=self.changed_fg, background=self.changed_bg)
        else:
            self.submit_button.config(style="Hover.TButton")
            self.style.configure("Hover.TButton", foreground=self.initial_fg, background=self.initial_bg)

    def set_submit_button_state(self, init = False):
        self.is_changed = init
        if init:
            # 恢复初始状态
            self.submit_button.config(text=self.initial_text)
            self.style.configure("TButton", foreground=self.initial_fg, background=self.initial_bg)
            self.is_changed = False
        else:
            # 改为 "⬛" 并修改样式
            self.submit_button.config(text=self.changed_text)
            self.style.configure("TButton", foreground=self.changed_fg, background=self.changed_bg)
            self.is_changed = True


# 运行应用程序
if __name__ == "__main__":
    root = tk.Tk()
    app = SubmitButton(root)
    root.mainloop()
