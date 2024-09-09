import json
import os
from datetime import datetime

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
    config = load_config()
    return load_records( config["txt_records_path"])

def load_img_records():
    config = load_config()
    return load_records( config["img_records_path"])

def load_config(config_file='config.json'):
    """Load configuration from a JSON file."""
    with open(config_file, 'r', encoding='utf-8') as file:
        config = json.load(file)
    return config

def save_img_record(prompt, img):
    """Save an image record with the given prompt and image data."""
    config = load_config()
    img_records_path = config["img_records_path"]

    # Create a new record
    create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_record = {
        "prompt": prompt,
        "img": img,
        "create_time": create_time
    }

    # Load existing records
    records = load_records(img_records_path)
    records.append(new_record)

    # Save updated records back to the file
    with open(img_records_path, 'w', encoding='utf-8') as file:
        json.dump(records, file, ensure_ascii=False, indent=4)

def save_txt_record(prompt, content):
    """Save a text record with the given prompt and content."""
    config = load_config()
    txt_records_path = config["txt_records_path"]

    # Create a new record
    create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_record = {
        "prompt": prompt,
        "content": content,
        "create_time": create_time
    }

    # Load existing records
    records = load_records(txt_records_path)
    records.append(new_record)

    # Save updated records back to the file
    with open(txt_records_path, 'w', encoding='utf-8') as file:
        json.dump(records, file, ensure_ascii=False, indent=4)