import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import requests
from io import BytesIO
from image_completion import AI_CreateImage
from text_completion import GPT_Completion
from datetime import datetime

image = None
original_image = None
photo_image = None
zoom_level = 1.0
image_id = None



def save_image(image, root):
    # 获取当前日期和时间，格式化为文件名
    default_filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.png")

    file_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        initialfile=default_filename,  # 设置默认文件名
        filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
    )
    if file_path and image:
        try:
            original_image.save(file_path)
        except Exception as e:
            print(f"Failed to save image: {e}")

def on_right_click(event, image_url, root):
    menu = tk.Menu(root, tearoff=0)
    menu.add_command(
        label="保存图片",
        command=lambda: save_image(image_url, root)
    )
    menu.post(event.x_root, event.y_root)


def show_image(label, url, root):
    global original_image, photo_image

    try:
        # 下载并加载新图像
        response = requests.get(url)
        image_data = BytesIO(response.content)
        original_image = Image.open(image_data)

        # 更新图像
        update_image(label)

        # 绑定右键点击事件
        label.bind("<Button-3>", lambda event: on_right_click(event, url, root))

        label.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    except Exception as e:
        print(f"Failed to load image: {e}")



def update_image(label):
    global photo_image, zoom_level

    if original_image:
        # 根据缩放级别调整图像大小
        new_size = (int(original_image.width * zoom_level), int(original_image.height * zoom_level))
        resized_image = original_image.resize(new_size, Image.Resampling.LANCZOS)
        photo_image = ImageTk.PhotoImage(resized_image)

        label.config(image=photo_image)
        label.photo = photo_image

def show_text(output_text, text):
    """显示生成的文本内容。"""
    output_text.config(state=tk.NORMAL)  # 允许修改文本框内容
    output_text.delete(1.0, tk.END)      # 清空文本框内容
    output_text.insert(tk.END, text)    # 插入新内容
    output_text.config(state=tk.DISABLED)  # 禁止修改文本框内容

def on_submit(input_text, option_var, output_text, output_image, size_var, root):
    """处理提交按钮的点击事件。"""
    prompt = input_text.get().strip()
    option = option_var.get()
    selected_size = size_var.get()  # 获取选定的图像尺寸

    if not prompt:
        return

    if option == "图片":
        output_text.pack_forget()  # 隐藏尺寸下拉列表
        output_image.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)  # Show image
        #image_data = AI_CreateImage(prompt, selected_size, 1)
        #url = image_data[0].url  # 从返回的数据中提取 URL
        url = "https://dalleproduse.blob.core.windows.net/private/images/93244186-7746-4be4-b74c-99d917874335/generated_00.png?se=2024-09-07T18%3A24%3A37Z&sig=v%2Bl%2FzBXZt7xZzJafNSS5ysD%2BR3F6Mv19A3Lvls4hkyA%3D&ske=2024-09-13T18%3A18%3A17Z&skoid=09ba021e-c417-441c-b203-c81e5dcd7b7f&sks=b&skt=2024-09-06T18%3A18%3A17Z&sktid=33e01921-4d64-4f8c-a055-5bdaffd5e33d&skv=2020-10-02&sp=r&spr=https&sr=b&sv=2020-10-02"
        show_image(output_image, url, root)
    else:
        output_image.pack_forget()  # 隐藏尺寸下拉列表
        output_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)  # Show text display
        answer = GPT_Completion(prompt)
        show_text(output_text, answer)

def on_option_change(option_var, size_menu):
    """处理下拉列表选择变化事件。"""
    if option_var.get() == "图片":
        size_menu.pack(side=tk.RIGHT, padx=5, pady=(0, 15))
    else:
        size_menu.pack_forget()  # 隐藏尺寸下拉列表


def on_key_press(event, submit_button):
    """处理键盘按下事件，触发按钮点击事件并调用 on_submit。"""
    if event.keysym == 'Return':
        submit_button.event_generate("<Button-1>")  # 生成鼠标左键点击事件
        # 调用 on_submit 函数

def on_key_release(event, submit_button, input_text, option_var, output_text, output_image, size_var, root):
    if event.keysym == 'Return':
        submit_button.event_generate("<ButtonRelease-1>")  # 生成鼠标左键释放事件
        on_submit(input_text, option_var, output_text, output_image, size_var, root)


def on_mouse_wheel(event, label):
    global zoom_level

    if event.num == 4 or event.delta > 0:  # Scroll up
        zoom_level *= 1.1
    elif event.num == 5 or event.delta < 0:  # Scroll down
        zoom_level /= 1.1

    update_image(label)

def adjust_option_menu_width(submit_button, option_menu):
    """调整下拉列表宽度以匹配提交按钮的宽度。"""
    button_width = submit_button.winfo_width()
    option_menu.config(width=button_width // 10)  # 估算宽度基于字符数

def on_resize(event, submit_button, option_menu):
    """处理窗口调整事件，调整下拉列表宽度。"""
    adjust_option_menu_width(submit_button, option_menu)

def bind_events(root, input_text, option_var, output_text, output_image, size_var, submit_button, size_menu):
    # 绑定事件
    option_var.trace("w", lambda *args: on_option_change(option_var, size_menu))
    root.bind("<KeyPress>", lambda event: on_key_press(event, submit_button))
    input_text.bind("<KeyRelease>", lambda e: on_key_release(e, submit_button, input_text, option_var, output_text, output_image, size_var, root))
    #canvas.bind("<MouseWheel>", lambda e: on_mouse_wheel(e, canvas))
    output_image.bind_all("<MouseWheel>", lambda e: on_mouse_wheel(e, output_image))

    root.bind("<Configure>", on_resize)
    submit_button.config(command=lambda: on_submit(input_text, option_var, output_text, output_image, size_var, root))