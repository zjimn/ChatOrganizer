import tkinter as tk
from tkinter import ttk


class CustomTextButton(ttk.Label):
    def __init__(self, parent, text, default_color="#000000", *args, **kwargs):
        super().__init__(parent, text=text, *args, **kwargs)

        self.active_color = None
        self.hover_color = None
        self.default_color = default_color
        self.set_default_color(default_color)

        # Bind events
        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        self.bind("<ButtonRelease-1>", self.on_hover)  # Restore hover color after click release

    def on_hover(self, event=None):
        self.configure(cursor="hand2", foreground=self.hover_color)

    def on_leave(self, event=None):
        self.configure(cursor="arrow", foreground=self.default_color)

    def on_click(self, event=None):
        self.configure(foreground=self.active_color)
        self.event_generate('<<ButtonClicked>>', when='tail')

    def set_default_color(self, default_color, hover_factor = 1.2, active_factor = 1.4):
        self.default_color = default_color
        self.hover_color = self._adjust_brightness(default_color, hover_factor)
        self.active_color = self._adjust_brightness(default_color, active_factor)

        # Set default properties
        self.configure(foreground=self.default_color, cursor="arrow")

    def _adjust_brightness(self, color, factor):
        """Adjust the brightness of a color."""
        if color.startswith("#"):
            color = color[1:]
        # Convert color to RGB
        rgb = [int(color[i:i + 2], 16) for i in (0, 2, 4)]
        # Adjust brightness
        adjusted_rgb = [
            min(max(int(c * factor), 0), 255) for c in rgb  # Ensure values stay within 0-255
        ]
        # Convert back to hexadecimal format
        return f"#{adjusted_rgb[0]:02x}{adjusted_rgb[1]:02x}{adjusted_rgb[2]:02x}"


# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Custom Text Button Example")

    custom_button = CustomTextButton(root, text="Click Me", default_color="#0077cc", font=("Arial", 14))
    custom_button.pack(pady=20)

    root.mainloop()