import threading
import tkinter as tk
import math
from time import sleep
import time

from PIL import Image, ImageTk


class LoadingSpinner(tk.Frame):
    def __init__(self, master=None, image_path="res/icon/loading_circle.png", size=50, radius=40, speed=10, **kwargs):
        super().__init__(master, **kwargs)
        self.is_running = True
        self.master = master
        self.image_path = image_path
        self.size = size
        self.radius = radius
        self.speed = speed

        # 创建Canvas来显示旋转的图片
        self.canvas = tk.Canvas(self, width=self.size, height=self.size)
        self.canvas.pack()

        # 加载图片
        self.original_image = Image.open(self.image_path)
        self.image = ImageTk.PhotoImage(self.original_image)

        # 创建图像对象
        self.image_id = self.canvas.create_image(self.size / 2, self.size / 2, image=self.image)

        # 创建标签显示秒数
        self.time_label = tk.Label(self, text="0", font=("Arial", 6), fg="black", bg="white")
        self.time_label.place(relx=0.5, rely=0.5, anchor="center", height=6)
        self.time_label.place(x=-1, y=0)

        # 设置旋转角度和开始时间
        self.angle = 0
        self.start_time = time.time()  # 记录开始时间
        self.animate_spinner()

    def animate_spinner(self):
        if not self.is_running:
            return

        # 计算旋转角度
        self.angle = (self.angle + self.speed) % 360

        # 旋转图片
        rotated_image = self.original_image.rotate(self.angle)
        self.image = ImageTk.PhotoImage(rotated_image)

        # 更新Canvas上的图片
        self.canvas.itemconfig(self.image_id, image=self.image)

        # 更新秒数标签
        elapsed_time = int(time.time() - self.start_time)  # 计算经过的时间
        if elapsed_time < 60:
            self.time_label.config(text=str(elapsed_time))
        else:
            self.time_label.config(text=f"{int(elapsed_time/60)}m")


        # 每隔20毫秒更新一次旋转效果
        self.after(20, self.animate_spinner)

    def start(self):
        self.place(relx=0.5, rely=0.5, anchor='center')
        self.is_running = True
        self.start_time = time.time()  # 重新记录开始时间
        self.animate_spinner()

    def stop(self):
        self.place_forget()
        self.is_running = False


# 示例：在窗口中使用加载组件
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Loading Spinner Component")
    root.geometry("300x300")

    # 创建并添加LoadingSpinner组件
    spinner = LoadingSpinner(root, image_path="../res/icon/loading_circle.png", size=100, radius=40, speed=10)
    spinner.place(relx=0.5, rely=0.5, anchor='center')  # 将组件放置在正中

    root.mainloop()
