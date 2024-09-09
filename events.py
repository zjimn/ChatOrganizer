import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import requests
from io import BytesIO
from enum import Enum
import math
import record_manager
from config import TYPE_OPTION_KEY
from record_manager import load_txt_records
from enums import ViewType
from image_completion import create_image_from_text
from text_completion import generate_gpt_completion
from datetime import datetime
from typing import Optional
from PIL import Image, ImageDraw, ImageTk, ImageFont
from data_management import DataManagement  # Import the class
from db.config_data_access import ConfigDataAccess

original_image: Optional[Image.Image] = None
photo_image = None
zoom_level = 1.0
image_id = None

def save_image(main_window, image, root):
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
            prompt = main_window.input_text.get()
            record_manager.save_img_record(prompt, file_path)
        except Exception as e:
            print(f"Failed to save image: {e}")

def on_right_click(event,main_window, image_url, root):
    menu = tk.Menu(root, tearoff=0)
    menu.add_command(
        label="保存图片",
        command=lambda: save_image(main_window, image_url, root)
    )
    menu.post(event.x_root, event.y_root)


def show_image(main_window, url, root):
    global original_image, photo_image
    main_window.tree.pack_forget()
    # Show Canvas
    main_window.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    main_window.output_image.pack(fill=tk.BOTH, expand=True, padx=0, pady=(40, 0))
    main_window.output_text.pack_forget()
    main_window.canvas.delete("all")
    try:
        # 下载并加载新图像
        response = requests.get(url)
        image_data = BytesIO(response.content)
        original_image = Image.open(image_data)
        # 更新图像
        update_image(main_window.output_image)
        # 绑定右键点击事件
        main_window.output_image.bind("<Button-3>", lambda event: on_right_click(event, main_window, url, root))
        root.after(100, lambda: update_button_position(main_window))
        update_button_position(main_window)
        print(f"in load image:")
    except Exception as e:
        print(f"Failed to load image: {e}")


def show_image_by_path(main_window, img_path, root):
    global original_image
    main_window.tree.pack_forget()
    # Show Canvas
    main_window.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    main_window.output_image.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)  # Show image
    main_window.output_text.pack_forget()
    main_window.canvas.delete("all")
    try:
        # 下载并加载新图像
        original_image = Image.open(img_path)
        # 更新图像
        update_image(main_window.output_image)
        main_window.output_image.pack(fill=tk.BOTH, expand=True, padx=0, pady=(40, 0))

        root.after(100, lambda: update_button_position(main_window))
        update_button_position(main_window)
    except Exception as e:
        print(f"Failed to load image: {e}")


def update_image(label):
    global photo_image, zoom_level

    if original_image:
        # 根据缩放级别调整图像大小
        if zoom_level <= 0:
            zoom_level = 0.01
        if zoom_level > 10:
            zoom_level = 10
        new_size = (
            math.ceil(original_image.width * zoom_level),
            math.ceil(original_image.height * zoom_level)
        )
        resized_image = original_image.resize(new_size, Image.Resampling.LANCZOS)
        photo_image = ImageTk.PhotoImage(resized_image)

        label.config(image=photo_image)
        label.photo = photo_image

def show_text(main_window, txt, root):
    """显示生成的文本内容。"""
    main_window.tree.pack_forget()
    # Show Canvas


    #scrollbar_width = get_scrollbar_width(main_window)
    scrollbar_width = 15
    main_window.canvas.place(
        relx=1.0,  # Right edge of the parent window
        rely=0.0,  # Top edge of the parent window
        anchor='ne',  # North-east corner of the canvas
        x=-10 - scrollbar_width,  # Offset from the right edge (10 pixels margin minus scrollbar width)
        y=0,  # Offset from the top edge (20 pixels margin)
        width=100,  # Set width of the canvas
        height=50  # Set height of the canvas
    )

    main_window.output_image.pack_forget()
    main_window.output_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(40, 0))
    main_window.output_text.config(state=tk.NORMAL)  # 禁止编辑
    main_window.output_text.delete(1.0, tk.END)  # Clear the text box
    main_window.output_text.insert(tk.END, txt)
    main_window.output_text.config(state=tk.DISABLED)
    # Display detailed information on Canvas
    #main_window.canvas.delete("all")
    #main_window.canvas.create_text(10, 40, anchor="nw", text=txt, font=("Microsoft YaHei", 12))
    root.after(100, lambda: update_button_position(main_window))

def get_scrollbar_width(main_window):
    scrollbars = [w for w in main_window.output_text.winfo_children() if isinstance(w, tk.Scrollbar)]
    if scrollbars:
        return scrollbars[0].winfo_width()

def show_tree(main_window):
    view_type = main_window.view_type
    # Clear back button
    main_window.canvas.delete("button")
    # Hide
    main_window.canvas.pack_forget()
    main_window.output_text.pack_forget()

    # Show Treeview
    main_window.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    data_manager = DataManagement(main_window)
    if view_type == ViewType.TXT:
        data_manager.set_column_width(main_window.output_frame)
        data_manager.update_txt_data_items(main_window.output_frame)
    elif view_type == ViewType.IMG:
        data_manager.set_column_width(main_window.output_frame)
        data_manager.update_img_data_items(main_window.output_frame)
    main_window.data_manager = data_manager



def on_submit(main_window, root):
    """处理提交按钮的点击事件。"""
    prompt = main_window.input_text.get().strip()
    option = main_window.option_var.get()
    selected_size = main_window.size_var.get()  # 获取选定的图像尺寸
    main_window.tree.pack_forget()
    main_window.output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    if not prompt:
        return

    if option == "图片":
        image_data = create_image_from_text(prompt, selected_size, 1)
        url = image_data[0].url  # 从返回的数据中提取 URL
        #url = 'https://dalleproduse.blob.core.windows.net/private/images/c39ceb5d-7607-4552-8148-032a899604d1/generated_00.png?se=2024-09-09T09%3A25%3A19Z&sig=yumj8EH%2B%2F6xFGQjA4XGgmXSofwwQ6R%2F7dGOWyGIKzls%3D&ske=2024-09-13T05%3A22%3A12Z&skoid=09ba021e-c417-441c-b203-c81e5dcd7b7f&sks=b&skt=2024-09-06T05%3A22%3A12Z&sktid=33e01921-4d64-4f8c-a055-5bdaffd5e33d&skv=2020-10-02&sp=r&spr=https&sr=b&sv=2020-10-02'
        show_image(main_window, url, root)
    else:
        answer = generate_gpt_completion(prompt)
        show_text(main_window, answer, root)
        prompt = main_window.input_text.get()
        record_manager.save_txt_record(prompt, answer)


def on_option_change(main_window):
    """处理下拉列表选择变化事件。"""
    if main_window.option_var.get() == "图片":
        main_window.view_type = ViewType.IMG
        show_tree(main_window)
        main_window.size_menu.pack(side=tk.RIGHT, padx=5, pady=(0, 15))
    else:
        main_window.view_type = ViewType.TXT
        show_tree(main_window)
        main_window.size_menu.pack_forget()  # 隐藏尺寸下拉列表



def on_key_press(event, submit_button):
    """处理键盘按下事件，触发按钮点击事件并调用 on_submit。"""
    if event.keysym == 'Return':
        submit_button.state(['pressed'])  # 按钮按下状态
        # 调用 on_submit 函数

def on_key_release(event, main_window, root):
    """处理键盘按下事件，触发按钮点击事件并调用 on_submit。"""
    if event.keysym == 'Return':
        main_window.submit_button.state(['!pressed'])  # 取消按钮按下状态
        on_submit(main_window, root)


def on_mouse_wheel(event, label):
    global zoom_level

    if event.num == 4 or event.delta > 0:  # Scroll up
        zoom_level *= 1.1
    elif event.num == 5 or event.delta < 0:  # Scroll down
        zoom_level /= 1.1

    update_image(label)

def adjust_option_menu_width(main_window):
    """调整下拉列表宽度以匹配提交按钮的宽度。"""
    button_width = main_window.submit_button.winfo_width()
    main_window.option_menu.config(width=button_width // 10)  # 估算宽度基于字符数

def update_column_widths(tree):
    total_width = tree.winfo_width()
    num_columns = len(tree["columns"])
    if num_columns > 0:
        column_width = total_width // num_columns
        for col in tree["columns"]:
            tree.column(col, width=column_width)

def on_resize(event, main_window):
    """处理窗口调整事件，调整下拉列表宽度。"""
    adjust_option_menu_width(main_window)
    update_column_widths(main_window.tree)


def on_item_double_click(event, main_window, root):
    item = main_window.tree.selection()[0]  # Get the selected item
    values = main_window.tree.item(item, 'values')  # Get the values of the selected item
    #show_text(main_window, values[0], root)

    if main_window.view_type == ViewType.TXT:
        show_text(main_window, values[2], root)
    elif main_window.view_type == ViewType.IMG:
        show_image_by_path(main_window, values[2], root)


def create_transparent_red_text(canvas, text, font):
    # Create an image and draw object
    image_size = (20, 20)  # Set a fixed size for the button
    image = Image.new('RGBA', image_size, (255, 255, 255, 0))  # Transparent background
    draw = ImageDraw.Draw(image)

    # Draw semi-transparent red rectangle
    draw.rectangle([0, 0, *image_size], fill=(255, 0, 0, 100))  # Adjust transparency

    # Calculate text position
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_x = (image_size[0] - (text_bbox[2] - text_bbox[0])) / 2 - 1
    text_y = (image_size[1] - (text_bbox[3] - text_bbox[1])) / 2 - 8

    # Draw text
    draw.text((text_x, text_y), text, font=font, fill=(255, 255, 255, 255))  # Opaque white text

    # Convert image to tkinter format
    return ImageTk.PhotoImage(image)


def update_button_position(main_window):
    canvas_width = main_window.canvas.winfo_width()
    canvas_height = main_window.canvas.winfo_height()

    # Set font
    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except IOError:
        font = ImageFont.load_default()

    button_image = create_transparent_red_text(main_window.canvas, "×", font)

    # Clear previous button
    main_window.canvas.delete("button")

    # Calculate position for the button
    padding = 10
    x = canvas_width - button_image.width()
    y = padding

    # Display button on canvas
    main_window.canvas.create_image(x, y, anchor="nw", image=button_image, tags="button")
    main_window.canvas.image = button_image  # Prevent garbage collection
    main_window.canvas.tag_raise("button")
    # Bind button click event
    main_window.canvas.tag_bind("button", "<Button-1>", lambda event: on_back_button_click(event,main_window))


def on_back_button_click(event, main_window):
    show_tree(main_window)


def bind_events(root, main_window, config_data_access):
    # 绑定事件
    root.bind("<Configure>", lambda e: on_resize(e, main_window))
    main_window.option_var.trace("w", lambda *args: on_option_change(main_window))
    root.bind("<KeyPress>", lambda event: on_key_press(event, main_window.submit_button))


    root.bind("<KeyRelease>", lambda e: on_key_release(e, main_window, root))
    #canvas.bind("<MouseWheel>", lambda e: on_mouse_wheel(e, canvas))
    main_window.output_image.bind_all("<MouseWheel>", lambda e: on_mouse_wheel(e, main_window.output_image))
    main_window.submit_button.config(command=lambda: on_submit(main_window, root))

    # Bind double-click event to Treeview
    main_window.tree.bind("<Double-1>", lambda event: on_item_double_click(event, main_window, root))

    # Update button position on window resize
    root.bind('<Configure>', lambda event: update_button_position(main_window))