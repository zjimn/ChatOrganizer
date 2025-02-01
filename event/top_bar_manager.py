from config.constant import LAST_TYPE_OPTION_KEY_NAME, TYPE_OPTION_TXT_KEY, TYPE_OPTION_IMG_KEY
from event.event_bus import event_bus
from event.model_viewer_manager import ModelViewerManager
from event.preset_viewer_manager import PresetViewerManager
from service.DialogModelService import DialogueModelService
from service.DialogPresetService import DialoguePresetService
from service.TreeService import TreeService
from ui.model_viewer import ModelViewer
from ui.preset_viewer import PresetViewer
from util.config_manager import ConfigManager


class TopBarManager:
    def __init__(self, main_window):
        self.model_type = None
        self.dialog_model_data = None
        self.selected_tree_id = None
        self.selected_preset_id = None
        self.dialog_preset_data = None
        self.main_window = main_window
        self.preset_manager_button = main_window.top_bar.preset_manager_button
        self.preset_combobox = main_window.top_bar.preset_combobox
        self.preset_options = main_window.top_bar.preset_options
        self.preset_var = main_window.top_bar.preset_var

        self.model_manager_button = main_window.top_bar.model_manager_button
        self.model_combobox = main_window.top_bar.model_combobox
        self.model_options = main_window.top_bar.model_options
        self.model_var = main_window.top_bar.model_var

        self.setting_button = main_window.top_bar.setting_button
        self.config_manager = ConfigManager()
        parent = main_window.root
        self.preset_viewer = PresetViewer(parent)
        self.model_viewer = ModelViewer(parent)
        self.preset_viewer_manager = PresetViewerManager(parent, self.preset_viewer)
        self.model_viewer_manager = ModelViewerManager(parent, self.model_viewer)
        self.bind_events()
        self.tree_service = TreeService()
        self.dialogue_preset_service = DialoguePresetService()
        self.dialogue_model_service = DialogueModelService()
        self.set_model_type()
        self.load_data()


    def load_data(self):
        self.reload_dialog_preset()

    def set_model_type(self):
        model_type = "text"
        if self.config_manager.get(LAST_TYPE_OPTION_KEY_NAME, TYPE_OPTION_TXT_KEY) == TYPE_OPTION_IMG_KEY:
            model_type = "img"
        self.model_type = model_type


    def on_click_preset_manage_button(self):
        event_bus.publish("OpenPresetViewer")

    def on_click_model_manage_button(self):
        event_bus.publish("OpenModelViewer")


    def on_click_setting_button(self):
        event_bus.publish("OpenSettingWindow")

    def on_preset_combobox_select(self, event):
        preset_combobox_selected_index = self.preset_combobox.current()
        data = self.dialog_preset_data[preset_combobox_selected_index]
        if data:
            preset_id = data.id
            name, max_history_count, detail = self.dialogue_preset_service.get_data_by_id(preset_id)
            self.config_manager.set("max_history_count", max_history_count)
            sys_messages = [item.value for item in detail]
            event_bus.publish("DialogPresetChanged", preset_id = preset_id, sys_messages = sys_messages)

    def on_model_combobox_select(self, event):
        model_combobox_selected_index = self.model_combobox.current()
        data = self.dialog_model_data[model_combobox_selected_index]
        if data:
            model_id = data.id
            model_name = data.name
            if self.model_type == "text":
                self.config_manager.set("text_model_id", model_id)
                self.config_manager.set("text_model_name", model_name)
            else:
                self.config_manager.set("img_model_id", model_id)
                self.config_manager.set("img_model_name", model_name)
            event_bus.publish("DialogModelChanged", model_name = model_name)

    def reload_dialog_preset(self, id = None):
        data = self.dialogue_preset_service.get_all_dialog_preset_list()
        self.dialog_preset_data = data
        self.reload_preset_combobox(self.selected_tree_id)

    def reload_preset_combobox(self, tree_id):
        self.selected_tree_id = tree_id
        preset_id = self.tree_service.get_preset_by_tree_id(tree_id)
        preset_index = None
        for index, item in enumerate(self.dialog_preset_data):
            if item.id == preset_id:
                preset_index = index
        new_options = [item.name for item in self.dialog_preset_data]
        self.preset_options = new_options
        self.preset_combobox['values'] = self.preset_options
        if preset_index is None:
            self.preset_var.set("")
            self.selected_preset_id = None
            self.config_manager.set("max_history_count", 0)
            event_bus.publish("DialogPresetLoaded", preset_id=None, sys_messages=[])
        if self.preset_options and preset_index is not None:
            self.selected_preset_id = self.preset_options[preset_index]
            self.preset_var.set(self.preset_options[preset_index])
            name, max_history_count, detail = self.dialogue_preset_service.get_data_by_id(preset_id)
            sys_messages = [item.value for item in detail]
            self.config_manager.set("max_history_count", max_history_count)
            event_bus.publish("DialogPresetLoaded", preset_id = preset_id, sys_messages = sys_messages)
        if len(self.preset_options) > 0:
            max_width = min(50, max(20, max(len(option) for option in self.preset_options)))
            self.preset_combobox.config(width=max_width)



    def reload_dialog_model(self, type = None):
        self.set_model_type()
        data = self.dialogue_model_service.get_all_dialog_model_list(self.model_type)
        self.dialog_model_data = data
        self.reload_model_combobox()

    def reload_model_combobox(self):
        model_index = None
        model_id = None
        if self.model_type == "text":
            model_id = self.config_manager.get("text_model_id")
        else:
            model_id = self.config_manager.get("img_model_id")
        for index, item in enumerate(self.dialog_model_data):
            if model_id and item.id == model_id:
                model_index = index
        new_options = [item.name for item in self.dialog_model_data]
        self.model_options = new_options
        self.model_combobox['values'] = self.model_options
        if model_index is None:
            self.model_var.set("")
            event_bus.publish("DialogModelChanged", model_name="")
        if self.model_options and model_index is not None:
            model_name= self.model_options[model_index]
            self.model_var.set(model_name)
            event_bus.publish("DialogModelChanged", model_name=model_name)
        if len(self.model_options) > 0:
            max_width = min(50, max(10, max(len(option) for option in self.model_options)))
            self.model_combobox.config(width=max_width)



    def bind_events(self):
        self.preset_manager_button.config(command = self.on_click_preset_manage_button)
        self.model_manager_button.config(command = self.on_click_model_manage_button)
        self.setting_button.config(command = self.on_click_setting_button)
        self.preset_combobox.bind("<<ComboboxSelected>>", self.on_preset_combobox_select)
        self.model_combobox.bind("<<ComboboxSelected>>", self.on_model_combobox_select)
        event_bus.subscribe("DialogPresetUpdated", self.reload_dialog_preset)
        event_bus.subscribe("DialogModelUpdated", self.reload_dialog_model)
        event_bus.subscribe("ReloadDialogModel", self.reload_dialog_model)
        event_bus.subscribe("ChangeTypeUpdateList", self.reload_dialog_model)
        event_bus.subscribe('TreeItemPress', self.reload_preset_combobox)
        event_bus.subscribe('TreeDialoguePresetDeleted', self.reload_preset_combobox)

