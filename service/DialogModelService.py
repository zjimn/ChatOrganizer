from db.dialogue_model_access import DialogueModelAccess
from db.dialogue_preset_detail_access import DialoguePresetDetailAccess


class DialogueModelService:
    def __init__(self):
        pass

    def get_all_dialog_model_list(self, type = "text"):
        with DialogueModelAccess() as dpa:
            return dpa.get_all_data(type)

    def get_data_by_id(self, id):
        with DialogueModelAccess() as dpa:
            data = dpa.get_data_by_id(id)
            return data

    def update_or_insert_data(self, detail, type = "text"):
        with DialogueModelAccess() as dma:
            for data in detail:
                if data.id is None:
                    dma.insert_data(data.name, type)
                else:
                    dma.update_data(data.id, data.name, data.delete_time)

    def delete_data(self, id):
        if not id:
            return
        with DialogueModelAccess() as dma:
            dma.delete(id)