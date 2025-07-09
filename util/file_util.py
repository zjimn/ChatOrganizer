import os
from pathlib import Path

from config.constant import APP_NAME, CONFIG_FILENAME, DB_FOLDER


def get_documents_directory():
    home_directory = os.path.expanduser('~')

    if os.name == 'nt':
        documents_directory = os.path.join(home_directory, 'Documents')
    else:
        documents_directory = os.path.join(home_directory, 'Documents')

    return documents_directory

def init_folder(folder=""):
    db_path = Path(get_documents_directory()) / APP_NAME / DB_FOLDER
    default_log_dir = Path(db_path)
    default_log_dir.mkdir(parents=True, exist_ok=True)