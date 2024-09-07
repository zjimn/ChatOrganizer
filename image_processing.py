from PIL import Image, ImageTk

def resize_image(image, max_width, max_height):
    """Resize image maintaining aspect ratio based on max dimensions."""
    original_width, original_height = image.size
    ratio = min(max_width / original_width, max_height / original_height)
    new_width = int(original_width * ratio)
    new_height = int(original_height * ratio)
    return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

def update_image_display(output_image, image):
    """Update the displayed image size based on current frame dimensions."""
    resized_image = resize_image(image, 800, 600)  # Example dimensions
    photo = ImageTk.PhotoImage(resized_image)
    output_image.config(image=photo)
    output_image.photo = photo  # Save reference to avoid garbage collection
    output_image.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
