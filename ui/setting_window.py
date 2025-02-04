
import tkinter as tk
from tkinter import ttk, font

from ttkbootstrap import Style

from config.constant import TOGGLE_BUTTON_CHECK_IMAGE_PATH, TOGGLE_BUTTON_UNCHECK_IMAGE_PATH
from widget.undo_redo_entry import UndoRedoEntry
from widget.custom_slider import CustomSlider
from widget.icon_toggle_button import IconToggleButton


class SettingsWindow:
    def __init__(self, root):
        self.max_token_var = tk.IntVar()
        self.max_history_count_var = tk.IntVar()
        self.root = root
        self.main_window = None
        self.font_size_combobox = None
        self.alignment_combobox = None
        self.theme_combobox = None
        self.font_options = font.families()
        self.font_options = self.font_options
        self.font_size_options = ["超小号", "小号", "中号", "大号", "超大号"]
        self.font_var = tk.StringVar(value = "font")
        self.font_size_var = tk.StringVar(value = "超小号")
        self.line_spacing_text_var = tk.IntVar(value=1)
        self.model_options = []
        self.model_var = tk.StringVar(value="")
        self.win_width = 470
        self.win_height = 380

        self.custom_setting = {}
        self._init()


    def _init(self):
        self.main_window = tk.Toplevel(self.root)
        self.main_window.title("设置")
        self.main_window.geometry(f"{self.win_width}x{self.win_height}")
        self.main_window.attributes('-topmost', True)
        self.main_window.resizable(False, False)

        self.main_frame = ttk.Frame(self.main_window, borderwidth=0, relief=tk.RAISED)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)


        self.model_server_frame = ttk.Frame(self.main_frame, borderwidth=0, relief=tk.RAISED)


        model_server_label = ttk.Label(self.model_server_frame, text="模型服务", font=("Microsoft YaHei UI", 10))
        model_server_label.pack(side = tk.LEFT, padx=(10, 10), pady=5)
        self.model_server_combobox = ttk.Combobox(self.model_server_frame, textvariable = self.model_var, values=self.model_options, state="readonly")
        self.model_server_combobox.pack(side = tk.LEFT, padx=(10, 10), pady=5)


        self.api_frame = ttk.Frame(self.main_frame, borderwidth=0, relief=tk.RAISED)
        self.api_label = ttk.Label(self.api_frame, text="API Key ", font=("Microsoft YaHei UI", 10))
        self.api_label.pack(side = tk.LEFT, padx=(10, 10), pady=5, expand = True)
        self.test_api_key_button = ttk.Button(self.api_frame, text="测试", state=tk.DISABLED)
        self.test_api_key_button.pack(side="right", padx=(5, 10))
        self.style = Style(theme="flatly")

        self.api_input_text_var = tk.StringVar()
        self.style.configure("Custom.TEntry")
        self.api_input_text = UndoRedoEntry(self.api_frame, width=50, style="Custom.TEntry",
                                           textvariable=self.api_input_text_var)
        self.api_input_text.pack(side=tk.LEFT, fill=tk.X, padx=10, pady=(0, 0), expand = True)

        self.separator_frame = ttk.Frame(self.main_frame, borderwidth=0, relief=tk.RAISED)
        self.separator = ttk.Separator(self.separator_frame, orient="horizontal")
        self.separator.pack(side="left", fill="x", padx=10, expand = True)

        self.type_effect_frame = ttk.Frame(self.main_frame, borderwidth=0, relief=tk.RAISED)
        type_effect_label = ttk.Label(self.type_effect_frame, text="打字效果", font=("Microsoft YaHei UI", 10))
        type_effect_label.pack(side = tk.LEFT, padx=(10, 10), pady=5)
        check_image_path = TOGGLE_BUTTON_CHECK_IMAGE_PATH
        uncheck_image_path = TOGGLE_BUTTON_UNCHECK_IMAGE_PATH
        self.type_effect_toggle_button = IconToggleButton(self.type_effect_frame, default_state= True, check_image_path = check_image_path, uncheck_image_path = uncheck_image_path, width=50, height=25)
        self.type_effect_toggle_button.pack(side = tk.LEFT, fill=tk.X, padx=0, pady=5)
        self.type_effect_toggle_button.set_state(True)

        type_effect_express_label = ttk.Label(self.type_effect_frame, text="(逐字打印输出)", font=("Microsoft YaHei UI", 9))
        type_effect_express_label.pack(side = tk.LEFT, padx=(10, 10), pady=5)

        self.max_token_frame = ttk.Frame(self.main_frame, borderwidth=0, relief=tk.RAISED)

        self.max_token_slider = CustomSlider(self.max_token_frame, label_text="", from_=1, to=20000,
                                           default=self.max_token_var.get())
        limit_max_token_label = ttk.Label(self.max_token_frame, text="限制字符", font=("Microsoft YaHei UI", 10))
        limit_max_token_label.pack(side = tk.LEFT, padx=(10, 10), pady=15)

        self.main_frame.pack(side = tk.TOP, fill=tk.X, padx=10, pady=5)
        self.model_server_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        self.api_frame.pack(side = tk.TOP, fill=tk.X, padx=10, pady=5)

        self.separator_frame.pack(side = tk.TOP, fill=tk.X, padx=10, pady=(5, 0))

        check_image_path = TOGGLE_BUTTON_CHECK_IMAGE_PATH
        uncheck_image_path = TOGGLE_BUTTON_UNCHECK_IMAGE_PATH
        self.max_token_toggle_button = IconToggleButton(self.max_token_frame, default_state= True, check_image_path = check_image_path, uncheck_image_path = uncheck_image_path, width=50, height=25)
        self.max_token_toggle_button.pack(side = tk.LEFT, fill=tk.X, padx=0, pady=0)
        self.max_token_express_label = ttk.Label(self.max_token_frame, text="(最大发送字符数)", font=("Microsoft YaHei UI", 9))
        self.max_token_express_label.pack(side = tk.LEFT, padx=(10, 10), pady=5)
        self.max_token_slider.pack(side=tk.LEFT, fill=tk.X, padx=0, pady=0)

        self.type_effect_frame.pack(side = tk.TOP, fill=tk.X, padx=10, pady=(10,0))
        self.max_token_frame.pack(side = tk.TOP, fill=tk.X, padx=10, pady=5)





        self.img_frame = ttk.Frame(self.main_frame, borderwidth=0, relief=tk.RAISED)

        img_label = ttk.Label(self.img_frame, text="图片存储", font=("Microsoft YaHei UI", 10))
        img_label.pack(side = tk.LEFT, padx=(10, 10), pady=(5, 5))

        self.img_entry = UndoRedoEntry(self.img_frame, width=15, style="Custom.TEntry")
        self.img_entry.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand = True)
        self.select_img_folder_button = ttk.Button(self.img_frame, text="选择目录", width=7)
        self.select_img_folder_button.pack(side=tk.RIGHT, padx=(5, 10))
        self.img_frame.pack(side = tk.TOP, fill=tk.X, padx=(10, 10), pady=5)


        self.log_frame = ttk.Frame(self.main_frame, borderwidth=0, relief=tk.RAISED)

        log_label = ttk.Label(self.log_frame, text="日志记录", font=("Microsoft YaHei UI", 10))
        log_label.pack(side = tk.LEFT, padx=(10, 10), pady=(5,5), anchor=tk.E)

        check_image_path = TOGGLE_BUTTON_CHECK_IMAGE_PATH
        uncheck_image_path = TOGGLE_BUTTON_UNCHECK_IMAGE_PATH
        self.log_toggle_button = IconToggleButton(self.log_frame, default_state= True, check_image_path = check_image_path, uncheck_image_path = uncheck_image_path, width=50, height=25)
        self.log_toggle_button.pack(side = tk.LEFT, fill=tk.X, padx=0, pady=0)

        self.log_entry = UndoRedoEntry(self.log_frame, width=15, style="Custom.TEntry")
        self.log_entry.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand = True)

        self.advanced_button = ttk.Button(self.log_frame, text="高级", width=4)

        self.select_log_folder_button = ttk.Button(self.log_frame, text="选择目录", width=7)
        self.advanced_button.pack(side=tk.RIGHT, padx=(5,10))
        self.select_log_folder_button.pack(side=tk.RIGHT, padx=(0, 0))
        self.log_frame.pack(side = tk.TOP, fill=tk.X, padx=(10, 10), pady=5)


        button_frame = ttk.Frame(self.main_window)
        button_frame.pack(side = tk.BOTTOM, fill=tk.X, padx=18, pady=(5, 20))

        self.confirm_button = ttk.Button(button_frame, text="确定", width=7)
        self.confirm_button.pack(side="right", padx=(5,10))
        self.cancel_button = ttk.Button(button_frame, text="取消", width=7)
        self.cancel_button.pack(side="right", padx=5)

        self.main_window.withdraw()
        # self.main_window.iconbitmap("res/icon/setting.ico")

def main():
    root = tk.Tk()
    root.title("主窗口")
    root.geometry("300x300")
    style = Style(theme='superhero')
    settings_window = SettingsWindow(root)

    open_button = tk.Button(root, text="打开设置窗口")
    open_button.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()