
import tkinter as tk
from PIL import Image, ImageTk
from util.image_editor import ImageEditor

class IconToggleButton(tk.Label):
    def __init__(self, master, width=15, height=15, check_image_path=None,
                 uncheck_image_path=None, default_state = True, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.root = self.winfo_toplevel()
        self.last_position = (self.root.winfo_x(), self.root.winfo_y())
        self.is_hovering = None
        self.width = width
        self.height = height
        self.check_image_path = check_image_path
        self.uncheck_image_path = uncheck_image_path
        self.is_checked = default_state
        self.is_enabled = True
        self.data = {"state": self.is_checked}

        self.default_enter_brightness = 1
        self.default_enter_color = 1

        self.default_leave_brightness = 0.9
        self.default_leave_color = 1

        self.enter_brightness = 1
        self.enter_color = 1
        self.leave_brightness = self.default_leave_brightness
        self.leave_color = self.default_leave_color
        self.image_editor = ImageEditor(self, self.check_image_path, width, height,
                                        default_brightness=self.default_leave_brightness,
                                        default_color=self.default_leave_color)
        self.set_state(self.is_checked)
        self.bind("<Button-1>", self.toggle)
        self.image_editor.canvas.bind("<Button-1>", self.toggle)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.config(cursor="hand2")
        self.root.bind_all("<Configure>", self.on_configure, add = "+")

    def toggle(self, event=None):
        if self.is_enabled:
            self.is_checked = not self.is_checked
            self.refresh()
            self.data["state"] = self.is_checked
            self.event_generate('<<CheckboxToggled>>', when='tail')

    def set_state(self, state):
        self.is_checked = state
        self.refresh()

    def get_state(self):
        return self.is_checked

    def set_enabled(self, enabled):
        self.is_enabled = enabled

    def refresh(self):
        img_path = self.check_image_path if self.is_checked else self.uncheck_image_path
        self.image_editor.set_image(img_path)
        self.adjust_brightness_color(self.leave_brightness, self.leave_color)

    def adjust_brightness_color(self, brightness, color):
        self.image_editor.adjust_brightness_color(brightness, color)

    def on_enter(self, event):
        self.adjust_brightness_color(self.enter_brightness, self.enter_color)
        self.is_hovering = True
        self.schedule_action()

    def on_configure(self, event):
        if self.root is None or not self.root.winfo_exists():
            return
        current_position = (self.root.winfo_x(), self.root.winfo_y())
        if current_position != self.last_position:
            self.last_position = current_position
            self.update()
            self.set_leave_color()
    '''
    update continuously during hover to prevent icon display error
    '''
    def schedule_action(self):
        if self.is_hovering:
            self.adjust_brightness_color(self.enter_brightness, self.enter_color)
            self.after(100, self.schedule_action)

    def on_leave(self, event):
        self.set_leave_color()

    def set_leave_color(self):
        self.adjust_brightness_color(self.leave_brightness, self.leave_color)
        self.update()
        self.is_hovering = False

    def set_check_image_path(self, image_path):
        self.check_image_path = image_path
        self.refresh()

    def set_uncheck_image_path(self, image_path):
        self.uncheck_image_path = image_path
        self.refresh()

    def reset_brightness_color(self):
        self.enter_brightness = self.default_enter_brightness
        self.enter_color = self.default_enter_color
        self.leave_brightness = self.default_leave_brightness
        self.leave_color = self.default_leave_color
        self.refresh()

    def set_enter_brightness_color(self, brightness, color):
        self.enter_brightness = brightness
        self.enter_color = color
        self.image_editor.adjust_brightness_color(brightness, color)

    def set_leave_brightness_color(self, brightness, color):
        self.leave_brightness = brightness
        self.leave_color = color
        self.image_editor.adjust_brightness_color(brightness, color)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Icon Checkbox Example")
    icon_checkbox = IconToggleButton(root)
    icon_checkbox.pack(pady=20)
    root.mainloop()