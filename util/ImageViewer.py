import tkinter as tk
from tkinter import Toplevel, Label
from PIL import Image, ImageTk

from util import image_util
from util.window_util import center_window


class ImageViewer:
    def __init__(self, parent):
        self.zoom_factor = None
        self.current_img = None
        self.parent = parent
        self.prev_width = None  # 用于存储上一次窗口的宽度
        self.prev_height = None  # 用于存储上一次窗口的高度

    def show_image_in_new_window(self, image_path, parent):
        """Creates a new window to show the image."""
        new_window = tk.Toplevel(parent)
        new_window.wm_attributes("-topmost", 1)
        new_window.title("图片详情")
        screen_width = new_window.winfo_screenwidth()
        screen_height = new_window.winfo_screenheight()


        img = Image.open(image_path)
        original_width, original_height = img.size
        min_width = min(original_width, screen_width)
        min_height = min(original_height, screen_height)

        min_rate = min(original_width / min_width, original_height / min_height)

        img_width = int(original_width * min_rate * 0.5)
        img_height = int(original_height * min_rate * 0.5)

        center_window(new_window, img_width, img_height)
        photo = ImageTk.PhotoImage(img)
        img_label = Label(new_window, image=photo)
        img_label.image = photo  # 保持引用防止垃圾回收
        img_label.pack()
        self.current_img = img
        self.zoom_factor = 1.0
        self.prev_width = 0
        def zoom_image(event):
            """Zoom the image based on mouse scroll."""
            if event.delta > 0:
                self.zoom_factor *= 1.1  # Zoom in
            else:
                self.zoom_factor /= 1.1  # Zoom out

            # Limit zoom factor to reasonable bounds
            self.zoom_factor = max(0.2, min(5, self.zoom_factor))

            # Resize the image with the new zoom factor
            new_width = int(img_width * self.zoom_factor)
            new_height = int(img_height * self.zoom_factor)
            img = image_util.resize_image_by_path(image_path, (new_width, new_height))
            photo = ImageTk.PhotoImage(img)
            img_label.config(image=photo)
            img_label.image = photo  # Keep a reference to prevent garbage collection
            # Center the image in the window
            center_image(new_width, new_height)

        def center_image(new_width, new_height):
            """Centers the image inside the window."""
            window_width = new_window.winfo_width()
            window_height = new_window.winfo_height()
            x_offset = (window_width - new_width) // 2
            y_offset = (window_height - new_height) // 2
            img_label.place(x=x_offset, y=y_offset)

        def resize_image(event):
            """Resize the image to fit the new window size."""
            new_width = event.width
            new_height = event.height
            img = image_util.resize_image_by_path(image_path, (new_width, new_height))
            photo = ImageTk.PhotoImage(img)
            img_label.config(image=photo)
            img_label.image = photo  # Keep a reference to prevent garbage collection
            center_image(new_width, new_height)

        def on_window_resize(event):
            """Check if window size has changed, and if so, call resize_image."""
            current_width = new_window.winfo_width()
            current_height = new_window.winfo_height()

            # 如果窗口尺寸发生了变化，则调用 resize_image 函数
            if self.prev_width != current_width or self.prev_height != current_height:
                resize_image(event)
                self.prev_width = current_width  # 更新宽度
                self.prev_height = current_height  # 更新高度

        new_window.bind("<Configure>", on_window_resize)
        # Bind mouse scroll events for zooming
        new_window.bind("<MouseWheel>", zoom_image)  # For Windows and MacOS
        new_window.bind("<Button-4>", zoom_image)    # For Linux scroll up
        new_window.bind("<Button-5>", zoom_image)    # For Linux scroll down



    def on_image_double_click(self ,event, img_path, parent):
        """Handler for double-clicking the image."""
        self.show_image_in_new_window(img_path, parent)
