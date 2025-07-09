def center_window(window, parent, width, height):
    if parent:
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2
    else:
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
    if y < 0:
        y = 50
    window.geometry(f"{width}x{height}+{x}+{y}")

def right_window(window, parent, width, height, padx):
    parent_width = parent.winfo_width()
    parent_height = parent.winfo_height()
    parent_x = parent.winfo_x()
    parent_y = parent.winfo_y()
    x = parent_x + parent_width
    y = parent_y + (parent_height - height) // 2
    if y < 0:
        y = 50
    window.geometry(f"{width}x{height}+{x + padx}+{y}")
