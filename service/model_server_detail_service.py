from db.model_server_detail_access import ModelServerDetailAccess


class ModelServerDetailService:
    def __init__(self):
        pass

    def get_all_dialog_model_list(self, type = "txt", server_key = None):
        with ModelServerDetailAccess() as msda:
            return msda.get_all_data(type, server_key)

    def get_data_by_server_key(self, server_key):
        with ModelServerDetailAccess() as msda:
            data = msda.get_data_by_server_key(server_key)
            return data

    def update_or_insert_data(self, server_key: str, txt_model_id: str = None, img_model_id: str = None, api_key: str = None, api_url: str = None, test_model_name: str = ''):
        with ModelServerDetailAccess() as msda:
            msda.upsert(server_key, txt_model_id, img_model_id, api_key, api_url, test_model_name)

    def update_txt_model(self, server_key: str, txt_model_id: str = None):
        with ModelServerDetailAccess() as msda:
            msda.update_txt_model(server_key, txt_model_id)


    def update_img_model(self, server_key: str, img_model_id: str = None):
        with ModelServerDetailAccess() as msda:
            msda.update_img_model(server_key, img_model_id)

    def delete_data(self, server_key):
        if not server_key:
            return
        with ModelServerDetailAccess() as msda:
            msda.delete(server_key)