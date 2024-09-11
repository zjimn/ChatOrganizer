import json
import os
from datetime import datetime

from db.content_data_access import ContentDataAccess
from db.dialogue_data_access import DialogueDataAccess
from enums import ContentType


def load_records(file_path):
    if not os.path.isfile(file_path):
        return []  # Return an empty list if the file does not exist

    # Check if the file is empty
    if os.stat(file_path).st_size == 0:
        return []  # Return an empty list if the file is empty

    # Load the JSON content from the file
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def load_txt_records():
    with ContentDataAccess() as cda:
        all_data = cda.get_all_txt_data()
    return all_data

def load_txt_dialogs(content_id):
    with DialogueDataAccess() as dda:
        all_data = dda.get_data_by_content_id(content_id)
        return merge_txt_content(all_data)

def load_img_dialogs(content_id):
    with DialogueDataAccess() as dda:
        all_data = dda.get_data_by_content_id(content_id)
        return all_data

def merge_txt_content(data):
    return "\n".join(f"{item.role}: {item.message}\n" for item in data)

def load_img_records():
    with ContentDataAccess() as cda:
        all_data = cda.get_all_image_data()
    return all_data

def save_img_record(content_id, prompt, db_img_path):
    with ContentDataAccess() as cda:
        if content_id is None:
            content_id = cda.insert_data(ContentType.IMG.value, prompt, "", db_img_path)
        with DialogueDataAccess() as dda:
            dda.insert_data(content_id, "user", prompt)
            dda.insert_data(content_id, "assistant", "", db_img_path)
    return content_id

def save_txt_record(content_id, prompt, content):
    with ContentDataAccess() as cda:
        if content_id is None:
            content_id = cda.insert_data(ContentType.TXT.value, prompt, content, "")
        with DialogueDataAccess() as dda:
            dda.insert_data(content_id, "user", prompt)
            dda.insert_data(content_id, "assistant", content)
    return content_id


