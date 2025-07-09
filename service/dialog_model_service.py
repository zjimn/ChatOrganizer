from db.dialogue_model_access import DialogueModelAccess
from db.dialogue_preset_detail_access import DialoguePresetDetailAccess
from db.model_server_detail_access import ModelServerDetailAccess


class DialogueModelService:
    def __init__(self):
        pass

    def get_all_dialog_model_list(self, type = "txt", server_key = None):
        with DialogueModelAccess() as dpa:
            return dpa.get_all_data(type, server_key)

    def get_data_by_id(self, id):
        with DialogueModelAccess() as dpa:
            data = dpa.get_data_by_id(id)
            return data

    def update_or_insert_data(self, detail, type = "txt", server_key = None):
        with DialogueModelAccess() as dma:
            for data in detail:
                if data.delete_time:
                    with ModelServerDetailAccess() as msda:
                        msda.remove_model(data.id)
                if data.id is None:
                    dma.insert_data(data.name, type, server_key, data.comment)
                else:
                    dma.update_data(data.id, data.name, data.delete_time, data.comment)

    def delete_data(self, id):
        if not id:
            return
        with DialogueModelAccess() as dma:
            dma.delete(id)