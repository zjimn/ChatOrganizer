from db.dialogue_model_access import DialogueModelAccess
from db.dialogue_preset_detail_access import DialoguePresetDetailAccess
from db.model_server_access import ModelServerAccess


class ModelServerService:
    def __init__(self):
        pass

    def get_all_list(self):
        with ModelServerAccess() as msa:
            list = msa.get_all()
            keys = [item.key for item in list]  # 提取所有的key
            names = [item.name for item in list]  # 提取所有的value
            return keys, names

