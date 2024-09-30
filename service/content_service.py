from typing import Optional

from config.constant import USER_NAME
from config.enum import ContentType
from db.content_data_access import ContentDataAccess
from db.dialogue_data_access import DialogueDataAccess
from db.models import ContentData
from util.str_util import get_chars_by_count


class ContentService:
    def __init__(self):
        pass

    def load_txt_records_by_page(self, txt="", tree_id=None, page_number=1, page_size=20, content_id=None, sort_by=None,
                                 sort_order="asc"):
        with ContentDataAccess() as cda:
            return cda.get_data_by_describe_or_content_by_page(txt, ContentType.TXT.value, page_number, page_size,
                                                               tree_id, content_id, sort_by, sort_order)

    def load_img_records_by_page(self, txt="", tree_id=None, page_number=1, page_size=20, content_id=None, sort_by=None,
                                 sort_order="asc"):
        with ContentDataAccess() as cda:
            return cda.get_data_by_describe_or_content_by_page(txt, ContentType.IMG.value, page_number, page_size,
                                                               tree_id, content_id, sort_by, sort_order)

    def load_txt_records(self, txt="", tree_id=None, content_id=None, sort_by=None, sort_order="asc"):
        with ContentDataAccess() as cda:
            return cda.get_data_by_describe_or_content(txt, ContentType.TXT.value, tree_id, content_id, sort_by,
                                                       sort_order)

    def load_img_records(self, txt="", tree_id=None, content_id=None, sort_by=None, sort_order="asc"):
        with ContentDataAccess() as cda:
            return cda.get_data_by_describe_or_content(txt, ContentType.IMG.value, tree_id, content_id, sort_by,
                                                       sort_order)

    def update_data(self, content_id, type, describe, content, img_path=None, dialogues=None):
        if dialogues is not None:
            content = self.merge_txt_content(dialogues, 50)
        with ContentDataAccess() as cda:
            cda.update_data(content_id, type, None, describe, content, img_path)

    def move_to_target_tree(self, content_ids, tree_id):
        with ContentDataAccess() as cda:
            for id in content_ids:
                cda.update_data(data_id=id, content_hierarchy_child_id=tree_id)

    def copy_to_target_tree(self, content_ids, tree_id):
        with ContentDataAccess() as cda:
            for content_id in content_ids:
                data = cda.get_data_by_id(content_id)
                inserted_data_id = cda.insert_data(data.type, tree_id, data.describe, data.content, data.img_path)
                with DialogueDataAccess() as dda:
                    dialogues = dda.get_data_by_content_id(content_id)
                    for dialogue in dialogues:
                        dda.insert_data(inserted_data_id, dialogue.role, dialogue.message, dialogue.img_path)

    def batch_update_dialogue_data(self, data):
        with DialogueDataAccess() as dda:
            dda.batch_update_data(data)

    def save_img_record(self, content_id, tree_id, prompt, db_img_path):
        with ContentDataAccess() as cda:
            if content_id is None:
                content_id = cda.insert_data(ContentType.IMG.value, tree_id, prompt, "",
                                             db_img_path)
            with DialogueDataAccess() as dda:
                dda.insert_data(content_id, "user", prompt)
                dda.insert_data(content_id, "assistant", "", db_img_path)
        return content_id

    def save_txt_record(self, content_id, tree_id, prompt, content):
        with ContentDataAccess() as cda:
            if content_id is None:
                content_id = cda.insert_data(ContentType.TXT.value, tree_id, prompt, content, "")
            with DialogueDataAccess() as dda:
                dda.insert_data(content_id, "user", prompt)
                dda.insert_data(content_id, "assistant", content)
        return content_id

    def load_data(self, content_id: int) -> Optional[ContentData]:
        with ContentDataAccess() as cda:
            data = cda.get_data_by_id(content_id)
            if data is None:
                print(f"No data found for content_id: {content_id}")
                return None
            content = self.merge_txt_content(data.dialogues, 50)
            new_data = ContentData(
                id=data.id,
                type=data.type,
                describe=data.describe,
                content=content,
                dialogues=data.dialogues
            )
        return new_data

    def load_txt_dialogs_with_merge(self, content_id):
        with DialogueDataAccess() as dda:
            all_data = dda.get_data_by_content_id(content_id)
        return self.merge_txt_content(all_data)

    def load_txt_dialogs(self, content_id):
        with DialogueDataAccess() as dda:
            return dda.get_data_by_content_id(content_id)

    def load_img_dialogs(self, content_id):
        with DialogueDataAccess() as dda:
            return dda.get_data_by_content_id(content_id)

    def merge_txt_content(self, data, max_chars=None):
        result = []
        char_count = 0
        for item in data:
            if item.role == USER_NAME:
                continue
            line = item.message
            result.append("\n")
            for char in line:
                if char.isspace():
                    result.append(char)
                else:
                    if max_chars is not None and char_count >= max_chars:
                        return ''.join(result)
                    result.append(char)
                    char_count += 1
        return get_chars_by_count(''.join(result), max_chars)