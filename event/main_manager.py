from typing import Optional
from PIL import Image
from api.openai_image_api import OpenaiImageApi
from api.openai_text_api import OpenaiTextApi
from config.app_config import AppConfig
from config.constant import LAST_SELECTED_TREE_ID_NAME
from event.event_bus import event_bus
from service.content_service import ContentService
from util.text_inserter import TextInserter
from util.token_management import TokenManager
from util.window_util import center_window


class MainManager:
    def __init__(self, main_window):
        self.selected_tree_id = None
        self.output_window_canvas_scroll_enabled = None
        self.focus_dialog_index = None
        self.dialog_frames = []
        self.dialog_labels = []
        self.zoom_levels = []
        self.dialog_images = []
        self.root = main_window.root
        self.app_config = AppConfig()
        self.content_service = ContentService()
        self.original_image: Optional[Image.Image] = None
        self.photo_image = None
        self.zoom_level = 1.0
        self.session_id = None
        self.token_management = TokenManager()
        self.img_generator = OpenaiImageApi()
        self.txt_generator = OpenaiTextApi()
        self.root.update_idletasks()
        self.text_inserter = TextInserter(self.root, main_window.output_window.output_text)
        self.bind_events()

    def on_press_tree_item(self, tree_id):
        self.selected_tree_id = tree_id

    def on_close_main_window(self):
        self.app_config.set(LAST_SELECTED_TREE_ID_NAME, self.selected_tree_id)
        self.app_config.save_all()
        self.root.destroy()

    def bind_events(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_close_main_window)
        event_bus.subscribe('TreeItemPress', self.on_press_tree_item)
