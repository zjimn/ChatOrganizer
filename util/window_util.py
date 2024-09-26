def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    if y < 0:
        y = 50
    window.geometry(f"{width}x{height}+{x}+{y}")
