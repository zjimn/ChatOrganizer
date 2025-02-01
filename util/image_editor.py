
from tkinter import Tk, Canvas, Button
from PIL import Image, ImageTk, ImageEnhance

from util.image_util import resize_image


class ImageEditor:
    def __init__(self, root, image_path, width = 20, height = 20, default_brightness = 1, default_color = 1):
        self.root = root
        self.width = width
        self.height = height
        self.img = Image.open(image_path)
        self.photo = ImageTk.PhotoImage(self.img)
        self.default_brightness = default_brightness
        self.default_color = default_color
        self.canvas = Canvas(root, width=self.width, height=self.height)
        self.canvas.pack()
        self.image_id = self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
        self.root.after(200, self.adjust_brightness_color, default_brightness, default_color)

    def set_image(self, image_path):
        self.img = Image.open(image_path)

    def adjust_brightness(self, factor):
        enhancer = ImageEnhance.Brightness(self.img)
        img_adjusted = enhancer.enhance(factor)
        return self.update_image(img_adjusted)

    def adjust_color(self, factor):
        enhancer = ImageEnhance.Color(self.img)
        img_adjusted = enhancer.enhance(factor)
        # self.img = img_resized
        return self.update_image(img_adjusted)

    def adjust_brightness_color(self, brightness, color):
        enhancer = ImageEnhance.Brightness(self.img)
        img_adjusted = enhancer.enhance(brightness)
        enhancer = ImageEnhance.Color(img_adjusted)
        img_adjusted = enhancer.enhance(color)
        return self.update_image(img_adjusted)

    def refresh(self):
        return self.update_image(self.img)

    def update_image(self, new_img):
        img_resized = resize_image(new_img, (self.width, self.height))
        self.photo = ImageTk.PhotoImage(img_resized)
        if self.canvas is not None and self.canvas.winfo_exists():
            self.canvas.itemconfig(self.image_id, image=self.photo)
            return self.photo


if __name__ == "__main__":
    root = Tk()
    editor = ImageEditor(root, "../res/icon/toggle_on.png", width= 30, height= 30)
    editor.adjust_color(0.1)
    root.mainloop()