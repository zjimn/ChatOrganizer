# display_frame.py
import tkinter as tk
from tkinter import ttk, scrolledtext

class DisplayFrame:
    def __init__(self, parent):
        self.parent = parent

        self.right_frame = tk.Frame(parent)
        self.right_frame.grid(row=0, column=1, sticky="nswe")

        self.search_input_entry_text = tk.StringVar()
        self.search_input_text = ttk.Entry(self.right_frame, width=50, textvariable=self.search_input_entry_text)
        self.search_input_text.pack(side=tk.TOP, fill=tk.X, padx=0, pady=(0, 10), anchor=tk.S)
        self.search_input_text.config(font=("Microsoft YaHei", 10))

        self.tree_frame = tk.Frame(self.right_frame)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(self.tree_frame, columns=("#0","id", "img", "prompt", "content", "create_time", "operation"), style='List.Treeview')
        self.tree.heading("#0", text="图片")
        self.tree.heading("id", text="id")
        self.tree.heading("img", text="图片")
        self.tree.heading("prompt", text="描述")
        self.tree.heading("content", text="内容")
        self.tree.heading("create_time", text="创建时间")
        self.tree.heading("operation", text="操作")
        self.tree.column("#0", width=100, anchor="center")
        self.tree.column("id", width=150, anchor="center")
        self.tree.column("img", width=1000, anchor="center")
        self.tree.column("prompt", width=450, anchor="center")
        self.tree.column("content", width=450, anchor="center")
        self.tree.column("create_time", width=150, anchor="center")
        self.tree.column("operation", width=150, anchor="center")

        self.tree_scrollbar = tk.Scrollbar(self.tree, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=self.tree_scrollbar.set)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # Add sample data
        self.insert_sample_data()

    def insert_sample_data(self):
        # Sample data to populate the tree ui
        sample_data = [
            {"id": "1", "img": "Image1.png", "prompt": "Sample prompt 1", "content": "Sample content 1", "create_time": "2024-09-01", "operation": "Edit"},
            {"id": "2", "img": "Image2.png", "prompt": "Sample prompt 2", "content": "Sample content 2", "create_time": "2024-09-02", "operation": "Delete"},
            # Add more sample data as needed
        ]

        for item in sample_data:
            self.tree.insert("", tk.END, values=(item["id"], item["img"], item["prompt"], item["content"], item["create_time"], item["operation"]))
