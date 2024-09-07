import tkinter as tk
from ui import create_ui
from events import bind_events, adjust_option_menu_width, on_resize


def main():
    root = tk.Tk()
    root.title("GPT Completion Tool")
    root.geometry("800x600")


    # 创建 UI 元素
    input_text, option_var, output_text, output_image, size_var, submit_button, size_menu, option_menu = create_ui(root)

    # 绑定事件
    bind_events(root, input_text, option_var, output_text, output_image, size_var, submit_button, size_menu)

    # 调整下拉列表宽度
    adjust_option_menu_width(submit_button, option_menu)

    root.bind("<Configure>", lambda e: on_resize(e, submit_button, option_menu))

    root.mainloop()

if __name__ == "__main__":
    main()
