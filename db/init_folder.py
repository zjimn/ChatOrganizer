from pathlib import Path
from config.constant import IMAGE_DIR_PATH

def init_folder():
    dir = Path(IMAGE_DIR_PATH)
    dir.mkdir(parents=True, exist_ok=True)