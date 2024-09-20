import threading
import tkinter as tk
from tkinter import filedialog
import requests
from io import BytesIO
import math

from config import constant
from config.app_config import AppConfig
from config.constant import TYPE_OPTION_KEY_NAME, IMG_SIZE_OPTION_KEY_NAME, ASSISTANT_NAME, LAST_SELECTED_TREE_ID_NAME
from db.models import Dialogue

from config.enum import ViewType

from datetime import datetime
from typing import Optional
from PIL import Image, ImageTk
from pathlib import Path
import tkinter.font as tkfont

from api.openai_image_api import OpenaiImageApi

from api.openai_text_api import OpenaiTextApi
from event.event_bus import event_bus
from service.content_service import ContentService
from util.text_inserter import TextInserter
from util.image_util import full_cover_resize
from util.token_management import TokenManager


class MainManager:
    def __init__(self, root, main_window):
        self.selected_tree_id = None
        self.output_window_canvas_scroll_enabled = None
        self.focus_dialog_index = None
        self.dialog_frames = []
        self.dialog_labels = []
        self.zoom_levels = []
        self.dialog_images = []
        self.root = root
        self.app_config = AppConfig()
        self.content_service = ContentService()

        self.main_window = main_window
        self.original_image: Optional[Image.Image] = None
        self.photo_image = None
        self.zoom_level = 1.0
        self.session_id = None

        self.token_management = TokenManager()
        self.img_generator = OpenaiImageApi()
        self.txt_generator = OpenaiTextApi()
        self.bind_events()
        root.update_idletasks()
        self.center_window()
        root.update_idletasks()
        self.text_inserter = TextInserter(self.root, self.main_window.output_window.output_text)

        self.bind_events()


    def center_window(self):
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        # 获取屏幕的宽度和高度
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # 计算窗口的 x 和 y 坐标，使其在屏幕中心
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        # 设置窗口的大小和位置
        self.root.geometry(f"{width}x{height}+{x}+{y}")


    def update_column_widths(self, tree):
        total_width = tree.winfo_width()
        num_columns = len(tree["columns"])
        if num_columns > 0:
            column_width = total_width // num_columns
            for col in tree["columns"]:
                tree.column(col, width=column_width)

    def on_resize(self, event, main_window):
        """处理窗口调整事件，调整下拉列表宽度。"""
        #self.adjust_option_menu_width()
        #self.update_column_widths(main_window.display_frame.tree)

    def on_press_tree_item(self, tree_id):
        self.selected_tree_id = tree_id

    def on_close_main_window(self):
        self.app_config.set(LAST_SELECTED_TREE_ID_NAME, self.selected_tree_id)
        self.app_config.save_all()
        self.root.destroy()


    def bind_events(self):
        # 绑定事件

        self.root.protocol("WM_DELETE_WINDOW", self.on_close_main_window)
        self.root.bind("<Configure>", lambda e: self.on_resize(e, self.main_window))
        event_bus.subscribe('TreeItemPress', self.on_press_tree_item)
