from db.dialogue_preset_access import DialoguePresetAccess
from db.dialogue_preset_detail_access import DialoguePresetDetailAccess


class DialoguePresetService:
    def __init__(self):
        pass

    def get_all_dialog_preset_list(self):
        with DialoguePresetAccess() as dpa:
            return dpa.get_all_data()

    def get_data_by_id(self, id):
        with DialoguePresetAccess() as dpa:
            with DialoguePresetDetailAccess() as dpda:
                detail = dpda.get_data_by_preset_id(id)
                data = dpa.get_data_by_id(id)
                name = data.name
                max_history_count = data.max_history_count
                return name, max_history_count, detail

    def insert_data(self, name, max_history_count, detail):
        with DialoguePresetAccess() as dpa:
            id = dpa.insert_data(name, max_history_count)
            if not id:
                return
            with DialoguePresetDetailAccess() as dpda:
                for data in detail:
                    data.preset_id = id
                    return dpda.insert_by_object(data)

    def update_data(self, id, name, max_history_count, detail):
        if not id:
            return
        with DialoguePresetAccess() as dpa:
            dpa.update_data(id, name, max_history_count)
            with DialoguePresetDetailAccess() as dpda:
                for data in detail:
                    if data.id is None:
                        dpda.insert_data(id, data.value)
                    else:
                        dpda.update_data(data.id, data.value, data.delete_time)

    def delete_data(self, id):
        if not id:
            return
        with DialoguePresetAccess() as dpa:
            dpa.delete(id)
            with DialoguePresetDetailAccess() as dpda:
                dpda.delete_by_preset_id(id)