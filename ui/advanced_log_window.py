
import tkinter as tk
from tkinter import ttk, font

from ttkbootstrap import Style

from config.constant import TOGGLE_BUTTON_CHECK_IMAGE_PATH, TOGGLE_BUTTON_UNCHECK_IMAGE_PATH
from widget.icon_toggle_button import IconToggleButton


class AdvancedLogWindow:
    def __init__(self, root):
        self.win_width = 270
        self.win_height = 250
        self.root = root
        self.main_window = None
        self._init()


    def _init(self):
        self.main_window = tk.Toplevel(self.root)
        self.main_window.title("高级")
        self.main_window.geometry(f"{self.win_width}x{self.win_height}")
        self.main_window.attributes('-topmost', True)
        self.main_window.resizable(False, False)

        self.main_frame = ttk.Frame(self.main_window, borderwidth=0, relief=tk.RAISED)

        check_image_path = TOGGLE_BUTTON_CHECK_IMAGE_PATH
        uncheck_image_path = TOGGLE_BUTTON_UNCHECK_IMAGE_PATH

        self.first_frame = ttk.Frame(self.main_frame, borderwidth=0, relief=tk.RAISED)
        self.second_frame = ttk.Frame(self.main_frame, borderwidth=0, relief=tk.RAISED)

        self.info_log_frame = ttk.Frame(self.first_frame, borderwidth=0, relief=tk.RAISED)
        info_log_label = ttk.Label(self.info_log_frame, text="信息", font=("Microsoft YaHei UI", 10))
        info_log_label.pack(side = tk.LEFT, padx=(10, 10), pady=5)
        self.info_log_toggle_button = IconToggleButton(self.info_log_frame, default_state= True, check_image_path = check_image_path, uncheck_image_path = uncheck_image_path, width=50, height=25)
        self.info_log_toggle_button.pack(side = tk.LEFT, fill=tk.X, padx=0, pady=5)
        self.info_log_toggle_button.set_state(True)
        # type_effect_express_label = ttk.Label(self.type_effect_frame, text="(逐字打印输出)", font=("Microsoft YaHei UI", 9))
        # type_effect_express_label.pack(side = tk.LEFT, padx=(10, 10), pady=5)

        self.warn_log_frame = ttk.Frame(self.first_frame, borderwidth=0, relief=tk.RAISED)
        warn_log_label = ttk.Label(self.warn_log_frame, text="警告", font=("Microsoft YaHei UI", 10))
        warn_log_label.pack(side = tk.LEFT, padx=(10, 10), pady=5)
        self.warn_log_toggle_button = IconToggleButton(self.warn_log_frame, default_state= True, check_image_path = check_image_path, uncheck_image_path = uncheck_image_path, width=50, height=25)
        self.warn_log_toggle_button.pack(side = tk.LEFT, fill=tk.X, padx=0, pady=5)
        self.warn_log_toggle_button.set_state(True)
        # type_effect_express_label = ttk.Label(self.type_effect_frame, text="(逐字打印输出)", font=("Microsoft YaHei UI", 9))
        # type_effect_express_label.pack(side = tk.LEFT, padx=(10, 10), pady=5)

        self.error_log_frame = ttk.Frame(self.second_frame, borderwidth=0, relief=tk.RAISED)
        error_log_label = ttk.Label(self.error_log_frame, text="错误", font=("Microsoft YaHei UI", 10))
        error_log_label.pack(side = tk.LEFT, padx=(10, 10), pady=5)
        self.error_log_toggle_button = IconToggleButton(self.error_log_frame, default_state= True, check_image_path = check_image_path, uncheck_image_path = uncheck_image_path, width=50, height=25)
        self.error_log_toggle_button.pack(side = tk.LEFT, fill=tk.X, padx=0, pady=5)
        self.error_log_toggle_button.set_state(True)
        # type_effect_express_label = ttk.Label(self.type_effect_frame, text="(逐字打印输出)", font=("Microsoft YaHei UI", 9))
        # type_effect_express_label.pack(side = tk.LEFT, padx=(10, 10), pady=5)

        self.sql_log_frame = ttk.Frame(self.second_frame, borderwidth=0, relief=tk.RAISED)
        sql_log_label = ttk.Label(self.sql_log_frame, text="SQL", font=("Microsoft YaHei UI", 10))
        sql_log_label.pack(side = tk.LEFT, padx=(10, 10), pady=5)
        self.sql_log_toggle_button = IconToggleButton(self.sql_log_frame, default_state= True, check_image_path = check_image_path, uncheck_image_path = uncheck_image_path, width=50, height=25)
        self.sql_log_toggle_button.pack(side = tk.LEFT, fill=tk.X, padx=0, pady=5)
        self.sql_log_toggle_button.set_state(True)
        # type_effect_express_label = ttk.Label(self.type_effect_frame, text="(逐字打印输出)", font=("Microsoft YaHei UI", 9))
        # type_effect_express_label.pack(side = tk.LEFT, padx=(10, 10), pady=5)

        self.request_log_frame = ttk.Frame(self.main_frame, borderwidth=0, relief=tk.RAISED)
        request_log_label = ttk.Label(self.request_log_frame, text="请求", font=("Microsoft YaHei UI", 10))
        request_log_label.pack(side = tk.LEFT, padx=(10, 10), pady=5)
        self.request_log_toggle_button = IconToggleButton(self.request_log_frame, default_state= True, check_image_path = check_image_path, uncheck_image_path = uncheck_image_path, width=50, height=25)
        self.request_log_toggle_button.pack(side = tk.LEFT, fill=tk.X, padx=0, pady=5)
        self.request_log_toggle_button.set_state(True)
        request_log_express_label = ttk.Label(self.request_log_frame, text="(请求API文本)", font=("Microsoft YaHei UI", 9))
        request_log_express_label.pack(side = tk.LEFT, padx=(10, 10), pady=5)

        self.response_log_frame = ttk.Frame(self.main_frame, borderwidth=0, relief=tk.RAISED)
        response_log_label = ttk.Label(self.response_log_frame, text="返回", font=("Microsoft YaHei UI", 10))
        response_log_label.pack(side = tk.LEFT, padx=(10, 10), pady=5)
        self.response_log_toggle_button = IconToggleButton(self.response_log_frame, default_state= True, check_image_path = check_image_path, uncheck_image_path = uncheck_image_path, width=50, height=25)
        self.response_log_toggle_button.pack(side = tk.LEFT, fill=tk.X, padx=0, pady=5)
        self.response_log_toggle_button.set_state(True)
        response_log_express_label = ttk.Label(self.response_log_frame, text="(API返回文本)", font=("Microsoft YaHei UI", 9))
        response_log_express_label.pack(side = tk.LEFT, padx=(10, 10), pady=5)


        self.main_frame.pack(side = tk.TOP, fill=tk.X, padx=10, pady=(10, 10))

        self.info_log_frame.pack(side = tk.LEFT, fill=tk.X, padx=10, pady=(0, 0))
        self.warn_log_frame.pack(side = tk.LEFT, fill=tk.X, padx=10, pady=(0, 0))
        self.first_frame.pack(side = tk.TOP, fill=tk.X, padx=0, pady=(0, 0))

        self.error_log_frame.pack(side = tk.LEFT, fill=tk.X, padx=10, pady=(0, 0))
        self.sql_log_frame.pack(side = tk.LEFT, fill=tk.X, padx=10, pady=(0, 0))
        self.second_frame.pack(side = tk.TOP, fill=tk.X, padx=0, pady=(0, 0))

        self.request_log_frame.pack(side = tk.TOP, fill=tk.X, padx=10, pady=(0, 0))
        self.response_log_frame.pack(side = tk.TOP, fill=tk.X, padx=10, pady=(0, 0))

        self.log_frame = ttk.Frame(self.main_frame, borderwidth=0, relief=tk.RAISED)


        button_frame = ttk.Frame(self.main_window)
        button_frame.pack(side = tk.BOTTOM, fill=tk.X, padx=15, pady=(0, 30))

        self.confirm_button = ttk.Button(button_frame, text="确定", width=7)
        self.confirm_button.pack(side="right", padx=(5,10))
        self.cancel_button = ttk.Button(button_frame, text="取消", width=7)
        self.cancel_button.pack(side="right", padx=5)

        self.main_window.withdraw()
        # self.main_window.iconbitmap("res/icon/setting.ico")

def main():
    root = tk.Tk()
    root.title("主窗口")
    root.geometry("300x200")
    style = Style(theme='superhero')
    advanced_log_window = AdvancedLogWindow(root)

    open_button = tk.Button(root, text="打开设置窗口")
    open_button.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()