import tkinter as tk
from tkinter import ttk
from tkinter import font

from util.logger import logger


class CustomSlider:
    def __init__(self, parent, label_text=None, from_=0, to=20, default=0, font_family="Microsoft YaHei UI",
                 font_size=10, command=None):
        self.line_spacing_var = tk.IntVar(value=default)
        self.line_spacing_text_var = tk.IntVar(value=default)
        self.from_ = from_
        self.to = to
        self.parent = parent
        self.command = command
        self.main_frame = ttk.Frame(parent, borderwidth=0, relief=tk.RAISED)

        if label_text:
            self.spacing_label = ttk.Label(self.main_frame, text=label_text, font=(font_family, font_size))
            self.spacing_label.pack(side=tk.LEFT, anchor="w", padx=(0, 10), pady=5)

        custom_font = font.Font(family=font_family, size=font_size)

        self.line_spacing_text = ttk.Entry(
            self.main_frame,
            textvariable=self.line_spacing_text_var,
            width=len(str(to)),
            # state="readonly",
            font=custom_font,
            validate="key",
            validatecommand = (self.parent.register(self.validate_input), '%P')
        )
        self.line_spacing_text.pack(side=tk.LEFT, padx=5, pady=5)
        self.line_spacing_text.bind("<FocusOut>", lambda event: self.validate_input_result(event))
        self.line_spacing_text.bind("<Return>", lambda event: self.validate_input_result(event))


        self.slider = ttk.Scale(
            self.main_frame,
            from_=from_,
            to=to,
            orient="horizontal",
            variable=self.line_spacing_var,
            command=self.on_line_spacing_change
        )

        self.spacing_slider_start_num_label = ttk.Label(self.main_frame, text=str(from_), font=(font_family, font_size))
        self.spacing_slider_end_num_label = ttk.Label(self.main_frame, text=str(to), font=(font_family, font_size))

        self.spacing_slider_start_num_label.pack(side=tk.LEFT, fill=tk.X, padx=5, pady=(0, 2))
        self.slider.pack(side=tk.LEFT, fill=tk.X, padx=0, pady=5, expand=True)
        self.spacing_slider_end_num_label.pack(side=tk.LEFT, fill=tk.X, padx=(5, 0), pady=(0, 2))

    def validate_input(self, new_value):
        is_digit = new_value.isdigit()
        in_range = False
        if new_value == "":
            return True
        if is_digit:
            in_range = float(new_value) <= self.to
        return is_digit and in_range

    def validate_input_result(self, event):
        try:
            value = int(self.line_spacing_text_var.get())
            if self.from_ <= value <= self.to:
                self.slider.set(value)
                self.remove_focus(event)
                return True
            elif value > self.to:
                self.line_spacing_var.set(self.to)
            elif value < self.from_:
                self.line_spacing_var.set(self.from_)
        except ValueError:
            logger.log('error', f"input validate error")
        value = self.line_spacing_var.get()
        self.line_spacing_text_var.set(value)
        self.slider.set(value)
        self.remove_focus(event)

    def config(self, command):
        self.command = command

    def remove_focus(self, event):
        event.widget.master.focus_set()
        return "break"

    def on_line_spacing_change(self, event):
        spacing = self.line_spacing_var.get()
        self.line_spacing_text_var.set(spacing)
        if self.command:
            self.command(spacing)

    def pack(self, **kwargs):
        self.main_frame.pack(**kwargs)

    def pack_forget(self):
        self.main_frame.pack_forget()

    def get(self):
        return self.line_spacing_var.get()

    def set(self, value):
        self.line_spacing_var.set(value)
        self.line_spacing_text_var.set(value)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("自定义滑杆组件示例")

    slider = CustomSlider(root, label_text="行间距", from_=0, to=20, default=5)
    slider.pack(padx=10, pady=10, fill=tk.X)


    def print_value():
        print("当前滑杆值:", slider.get())


    btn = ttk.Button(root, text="获取值", command=print_value)
    btn.pack(pady=10)

    root.mainloop()