import json
import os
from datetime import datetime

from db.content_data_access import ContentDataAccess
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
        cda.insert_data("example_type", "example_description", "example_content", "path/to/image.jpg")
        all_data = cda.get_all_txt_data()
    return all_data

def load_img_records():
    with ContentDataAccess() as cda:
        cda.insert_data("example_type", "example_description", "example_content", "path/to/image.jpg")
        all_data = cda.get_all_image_data()
    return all_data

def save_img_record(prompt, img):

    with ContentDataAccess() as cda:
        cda.insert_data(ContentType.IMG.value, prompt, "", img)

def save_txt_record(prompt, content):
    with ContentDataAccess() as cda:
        cda.insert_data(ContentType.TXT.value, prompt, content, "")