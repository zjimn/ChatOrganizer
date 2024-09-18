def center_window(window, width, height):
    # 获取屏幕宽度和高度
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # 计算居中位置
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    if y < 0:
        y = 50
    # 设置窗口大小和位置
    window.geometry(f"{width}x{height}+{x}+{y}")