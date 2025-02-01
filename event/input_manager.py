import math
import tkinter as tk
from config.constant import LAST_TYPE_OPTION_KEY_NAME, IMG_SIZE_OPTION_KEY_NAME, TYPE_OPTION_TXT_KEY, TYPE_OPTION_IMG_KEY
from event.event_bus import event_bus
from util.config_manager import ConfigManager


class InputManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.input_frame = main_window.input_frame
        self.root = main_window.root
        self.config_manager = ConfigManager()
        self.init_option()
        self.bind_events()

    def on_type_option_change(self):
        self.update_option()
        if self.input_frame.option_var.get() == self.main_window.input_frame.type_options[1]:
            self.config_manager.set(LAST_TYPE_OPTION_KEY_NAME, TYPE_OPTION_IMG_KEY)
            type = TYPE_OPTION_IMG_KEY
        else:
            self.config_manager.set(LAST_TYPE_OPTION_KEY_NAME, TYPE_OPTION_TXT_KEY)
            type = TYPE_OPTION_TXT_KEY
        event_bus.publish('ChangeTypeUpdateList', type=type)

    def init_option(self):
        option_index = self.config_manager.get(LAST_TYPE_OPTION_KEY_NAME, TYPE_OPTION_TXT_KEY)
        size_option_index = self.config_manager.get(IMG_SIZE_OPTION_KEY_NAME, TYPE_OPTION_TXT_KEY)
        selected_type_option = self.input_frame.type_options[option_index]
        selected_size_option = self.input_frame.size_options[size_option_index]
        self.input_frame.option_var.set(selected_type_option)
        self.input_frame.size_var.set(selected_size_option)
        self.update_option()

    def update_option(self):
        self.input_frame.new_chat_button.pack_forget()
        if self.input_frame.option_var.get() == self.main_window.input_frame.type_options[1]:
            self.input_frame.size_menu.pack(side=tk.RIGHT, padx=5, anchor=tk.S)
        else:
            self.input_frame.size_menu.pack_forget()

    def on_size_option_change(self):
        size_options = ["1024x1024", "1792x1024", "1024x1792"]
        for index, option in enumerate(size_options):
            if self.input_frame.size_var.get() == option:
                self.config_manager.set(IMG_SIZE_OPTION_KEY_NAME, index)
                break

    def check_and_submit(self, event):
        state = self.input_frame.submit_button["state"]
        if event.keysym == 'Return' and event.state & 0x20000 == 0 and not self.input_frame.submit_button_is_changed and str(
                state) == "normal":
            self.set_submit_button_init_state(False)
            self.main_window.input_frame.submit_button.state(['!pressed'])
            self.root.event_generate('<<SubmitRequest>>')

    def on_click_submit_button(self):
        if not self.input_frame.submit_button_is_changed:
            self.set_submit_button_init_state(False)
            self.root.event_generate('<<SubmitRequest>>')
        else:
            self.root.event_generate('<<CancelRequest>>')
            self.set_submit_button_init_state(True)
            self.set_prompt_input_focus()

    def on_click_new_chat_button(self):
        event_bus.publish('NewChat')
        self.input_frame.new_chat_button.pack_forget()

    def on_close_output_window(self):
        self.input_frame.new_chat_button.pack_forget()

    def on_open_chat_detail(self):
        self.input_frame.new_chat_button.pack(side=tk.RIGHT, padx=(0, 10), anchor=tk.S)

    def set_prompt_input_focus(self):
        self.check_input_text()
        self.input_frame.input_text.focus_set()

    def set_submit_button_init_state(self, init=False):
        self.input_frame.submit_button_is_changed = not init
        if init:
            self.input_frame.submit_button.config(
                text=self.input_frame.submit_button_initial_text)
        else:
            self.input_frame.submit_button.config(
                text=self.input_frame.submit_button_changed_text)

    def adjust_option_menu_width(self):
        button_width = self.input_frame.submit_button.winfo_width()
        self.input_frame.option_menu.config(width=button_width // 10)

    def on_text_change(self, event):
        text = self.input_frame.input_text
        text.edit_modified(False)
        self.root.after(100, lambda: self.input_frame.input_text.see(tk.END))
        self.adjust_text_height(event)

    def adjust_text_height(self, event = None):
        text = self.input_frame.input_text
        line_count = text.count("0.0", "end", "displaylines")[0]
        new_height = min(15, max(line_count, 1))
        self.input_frame.input_text.config(height=new_height)

    def on_alt_return_press(self, event):
        self.input_frame.input_text.insert(tk.INSERT, "\n")
        return "break"

    def on_key_press(self, event, submit_button):
        if event.keysym == 'Return' and event.state & 0x20000 == 0:
            submit_button.state(['pressed'])

    def check_input_text(self, event=None):
        text = self.input_frame.input_text
        if text.get("1.0", tk.END).strip():
            self.input_frame.submit_button.config(state=tk.NORMAL)
        else:
            if not self.input_frame.submit_button_is_changed:
                self.input_frame.submit_button.config(state=tk.DISABLED)

    def on_key_release(self, event, root):
        root.update_idletasks()
        root.after(100, self.check_and_submit, event)

    def on_request_finished(self, event=None):
        self.set_submit_button_init_state(True)
        self.set_prompt_input_focus()

    def on_request_begin(self, event=None):
        self.main_window.input_frame.input_text.delete('1.0', tk.END)
        self.set_prompt_input_focus()

    def bind_events(self):
        self.root.bind("<KeyPress>", lambda event: self.on_key_press(event, self.main_window.input_frame.submit_button))
        self.root.bind("<KeyRelease>", lambda e: self.on_key_release(e, self.root))
        self.input_frame.option_var.trace("w", lambda *args: self.on_type_option_change())
        self.input_frame.size_var.trace("w", lambda *args: self.on_size_option_change())
        self.input_frame.submit_button.config(command=lambda: self.on_click_submit_button())
        self.input_frame.new_chat_button.config(command=lambda: self.on_click_new_chat_button())
        self.input_frame.input_text.bind("<<Modified>>", self.on_text_change)
        self.input_frame.input_text.bind("<Alt-Return>", self.on_alt_return_press)
        self.input_frame.input_text.bind("<Return>", lambda event: "break")
        self.input_frame.input_text.bind("<KeyRelease>", self.check_input_text)
        self.input_frame.frame.bind("<<RequestOpenaiFinished>>", self.on_request_finished)
        self.input_frame.frame.bind("<<RequestOpenaiBegin>>", self.on_request_begin)
        self.root.bind("<Configure>", lambda e: self.adjust_text_height(e))
        event_bus.subscribe("OpenChatDetail", self.on_open_chat_detail)
        event_bus.subscribe("CloseOutputWindow",self.on_close_output_window)

