
from PIL import Image, ImageTk


def resize_image(img, target_size):
    # 获取原始图片的尺寸
    original_width, original_height = img.size

    # 目标宽度和高度
    target_width, target_height = target_size

    # 如果 target_width 为空，根据 target_height 等比例缩放宽度
    if target_width is None:
        ratio = target_height / original_height
        target_width = int(original_width * ratio)
        target_size = target_width, target_size[1]

    # 如果 target_height 为空，根据 target_width 等比例缩放高度
    if target_height is None:
        ratio = target_width / original_width
        target_height = int(original_height * ratio)
        target_size = target_size[0], target_height


    # 计算新的尺寸
    ratio = min(target_width / original_width, target_height / original_height)
    new_width = int(original_width * ratio)
    new_height = int(original_height * ratio)
    if new_width < 1:
        new_width = 1
    if new_height < 1:
        new_height = 1
    # 调整图片大小
    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # 创建一个目标大小的白色背景图像
    background = Image.new('RGBA', target_size, (255, 255, 255, 0))

    # 计算位置
    position = ((target_width - new_width) // 2, (target_height - new_height) // 2)

    # 将调整大小的图片粘贴到背景中
    background.paste(img, position)

    return background

def full_cover_resize(img, target_size):
    target_width, target_height = target_size
    original_width, original_height = img.size
    if original_width / original_height > target_width / target_height:

        return resize_image(img, (None,target_size[1]))

    else:
        return resize_image(img, (target_size[0], None))

def resize(img, target_size):
    target_width, target_height = target_size
    original_width, original_height = img.size
    if original_width / original_height > target_width / target_height:

        return resize_image(img, (None,target_size[1]))

    else:
        return resize_image(img, (target_size[0], None))

def resize_image_by_path(img_path, target_size):
    img = Image.open(img_path)

    return resize_image(img, target_size)


def open_img_replace_if_error(img_path, replace_img, size):
    if not img_path or img_path == '':
        return replace_img
    try:
        img = Image.open(img_path)
        img = resize_image(img, size)
        img_tk = ImageTk.PhotoImage(img)
    except Exception as e:
        img_tk = replace_img
        print(f"Error adding item with image: {e}")

    return img_tk