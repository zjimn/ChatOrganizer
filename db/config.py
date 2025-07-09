import os
from pathlib import Path

from config.constant import APP_NAME, DB_FOLDER, DB_FILENAME
from util.file_util import get_documents_directory

db_path = os.path.join(Path(get_documents_directory()), APP_NAME, DB_FOLDER, DB_FILENAME)
db_normal_path = os.path.normpath(db_path)
db_normal_path = db_normal_path.replace(os.sep, '/')
DATABASE_URL = f'sqlite:///{db_normal_path}'
