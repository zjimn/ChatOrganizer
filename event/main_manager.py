from config.app_config import AppConfig
from config.constant import LAST_SELECTED_TREE_ID_NAME
from event.event_bus import event_bus


class MainManager:
    def __init__(self, main_window):
        self.selected_tree_id = None
        self.root = main_window.root
        self.app_config = AppConfig()
        self.root.update_idletasks()
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
