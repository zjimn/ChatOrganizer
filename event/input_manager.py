import tkinter as tk

from config import constant
from config.app_config import AppConfig
from config.constant import TYPE_OPTION_KEY_NAME, IMG_SIZE_OPTION_KEY_NAME, TYPE_OPTION_TXT_KEY, TYPE_OPTION_IMG_KEY
from config.enum import ViewType
from event.event_bus import event_bus


class InputManager:
    def __init__(self, root, main_window):
        self.main_window = main_window
        self.input_frame = main_window.input_frame
        self.root = root
        self.app_config = AppConfig()
        self.init_option()
        self.bind_events()

    def on_type_option_change(self):
        """处理下拉列表选择变化事件。"""
        self.update_option()
        if self.input_frame.option_var.get() == self.main_window.input_frame.type_options[1]:
            self.app_config.set(TYPE_OPTION_KEY_NAME, TYPE_OPTION_IMG_KEY)
            type = TYPE_OPTION_IMG_KEY
        else:
            self.app_config.set(TYPE_OPTION_KEY_NAME, TYPE_OPTION_TXT_KEY)
            type = TYPE_OPTION_TXT_KEY
        event_bus.publish('ChangeTypeUpdateList', type = type)

    def init_option(self):
        option_index = self.app_config.get(TYPE_OPTION_KEY_NAME, "0")
        size_option_index = self.app_config.get(IMG_SIZE_OPTION_KEY_NAME, "0")
        selected_type_option = self.input_frame.type_options[int(option_index)]
        selected_size_option = self.input_frame.size_options[int(size_option_index)]
        self.input_frame.option_var.set(selected_type_option)
        self.input_frame.size_var.set(selected_size_option)
        self.update_option()

    def update_option(self):
        if self.input_frame.option_var.get() == self.main_window.input_frame.type_options[1]:
            self.main_window.view_type = ViewType.IMG
            self.input_frame.size_menu.pack(side=tk.RIGHT, padx=5, pady=(0, 0), anchor=tk.S)
        else:
            self.main_window.view_type = ViewType.TXT
            self.input_frame.size_menu.pack_forget()

    def on_size_option_change(self):
        """处理下拉列表选择变化事件。"""
        size_options = ["1024x1024", "1792x1024", "1024x1792"]
        for index, option in enumerate(size_options):
            if self.input_frame.size_var.get() == option:
                self.app_config.set(IMG_SIZE_OPTION_KEY_NAME, str(index))
                break

    def check_and_submit(self, event):
        """检查按钮状态并处理提交。"""
        state = self.input_frame.submit_button["state"]
        if event.keysym == 'Return' and event.state & 0x20000 == 0 and not self.input_frame.submit_button_is_changed and str(state) == "normal":
            self.set_submit_button_init_state(False)
            self.main_window.input_frame.submit_button.state(['!pressed'])  # 取消按钮按下状态
            self.root.event_generate('<<SubmitRequest>>')

    def on_hit_submit_button(self):
        if not self.input_frame.submit_button_is_changed:
            self.set_submit_button_init_state(False)
            self.root.event_generate('<<SubmitRequest>>')
        else:
            self.root.event_generate('<<CancelRequest>>')
            self.set_submit_button_init_state(True)
            self.set_prompt_input_focus()

    def set_prompt_input_focus(self):
        self.check_input_text()
        self.input_frame.input_text.focus_set()


    def set_submit_button_init_state(self, init=False):
        self.input_frame.submit_button_is_changed = not init
        if init:
            # 恢复初始状态
            self.input_frame.submit_button.config(
                text=self.input_frame.submit_button_initial_text)
        else:
            # 改为 "⬛" 并修改样式
            self.input_frame.submit_button.config(
                text=self.input_frame.submit_button_changed_text)

    def adjust_option_menu_width(self):
        """调整下拉列表宽度以匹配提交按钮的宽度。"""
        button_width = self.input_frame.submit_button.winfo_width()
        self.input_frame.option_menu.config(width=button_width // 10)  # 估算宽度基于字符数


    def on_text_change(self, event):
        self.input_frame.input_text.edit_modified(False)
        self.root.after(100, lambda: self.input_frame.input_text.see(tk.END))
        lines = self.input_frame.input_text.get('1.0', 'end-1c').split('\n')
        num_lines = len(lines)
        new_height = max(num_lines, 1)
        self.input_frame.input_text.config(height=new_height)


    def on_alt_return_press(self, event):
        """处理 Alt + Return 组合键，执行回车键效果。"""
        # 插入换行符
        self.input_frame.input_text.insert(tk.INSERT, "\n")
        return "break"  # 确保没有其他默认行为

    def on_key_press(self, event, submit_button):
        """处理键盘按下事件，触发按钮点击事件并调用 on_submit。"""
        if event.keysym == 'Return' and event.state & 0x20000 == 0:
            submit_button.state(['pressed'])  # 按钮按下状态
            # 调用 on_submit 函数

    def check_input_text(self, event = None):
        # 检查 Text 小部件的内容
        if self.input_frame.input_text.get("1.0", tk.END).strip():
            self.input_frame.submit_button.config(state=tk.NORMAL)
        else:
            if not self.input_frame.submit_button_is_changed:
                self.input_frame.submit_button.config(state=tk.DISABLED)

    def on_key_release(self, event, root):
        root.update_idletasks()
        """处理键盘按下事件，触发按钮点击事件并调用 on_submit。"""
        # 使用 after 方法稍微延迟状态检查，确保 Tkinter 更新完状态
        root.after(100, self.check_and_submit, event)

    def on_request_finished(self, event = None):
        self.set_submit_button_init_state(True)
        self.set_prompt_input_focus()

    def on_request_begin(self, event = None):
        self.main_window.input_frame.input_text.delete('1.0', tk.END)
        self.set_prompt_input_focus()

    def bind_events(self):
        self.root.bind("<KeyPress>", lambda event: self.on_key_press(event, self.main_window.input_frame.submit_button))
        self.root.bind("<KeyRelease>", lambda e: self.on_key_release(e, self.root))
        self.input_frame.option_var.trace("w", lambda *args: self.on_type_option_change())
        self.input_frame.size_var.trace("w", lambda *args: self.on_size_option_change())
        self.input_frame.submit_button.config(command=lambda: self.on_hit_submit_button())
        self.input_frame.input_text.bind("<<Modified>>", self.on_text_change)
        self.input_frame.input_text.bind("<Alt-Return>", self.on_alt_return_press)
        self.input_frame.input_text.bind("<Return>", lambda event: "break")
        self.input_frame.input_text.bind("<KeyRelease>", self.check_input_text)
        self.input_frame.frame.bind("<<RequestOpenaiFinished>>", self.on_request_finished)
        self.input_frame.frame.bind("<<RequestOpenaiBegin>>", self.on_request_begin)
