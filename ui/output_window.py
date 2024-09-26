# output_window.py
import tkinter as tk
from tkinter import scrolledtext

class OutputWindow:
    def __init__(self, parent):
        self.parent = parent
        self.output_window = tk.Toplevel(parent)
        self.output_window.title("")
        self.output_window.wm_attributes("-topmost", 1)
        self.output_window.withdraw()

        x = parent.winfo_x()
        y = parent.winfo_y()
        self.output_window.geometry(f"{800}x{630}+{x + 50}+{y + 50}")

        self.output_frame = tk.Frame(self.output_window)
        self.output_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(20, 20))

        self.output_window_canvas = tk.Canvas(self.output_frame, bg="#f0f0f0", width=600)
        self.output_window_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.output_window_scrollbar = tk.Scrollbar(self.output_frame, orient=tk.VERTICAL, command=self.output_window_canvas.yview)
        self.output_window_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_window_canvas.configure(yscrollcommand=self.output_window_scrollbar.set)

        self.output_window_scrollbar_frame = tk.Frame(self.output_window_canvas)
        self.output_window_canvas.create_window((0, 0), window=self.output_window_scrollbar_frame, anchor='nw')
        self.output_window_scrollbar_frame.bind("<Configure>", lambda e: self.output_window_canvas.configure(
            scrollregion=self.output_window_canvas.bbox("all")))

        self.output_text = scrolledtext.ScrolledText(self.output_window_canvas, wrap=tk.WORD, state=tk.DISABLED)
        self.output_text.pack_forget()
        self.output_text.config(font=("Microsoft YaHei", 12), padx=10, pady=10)
