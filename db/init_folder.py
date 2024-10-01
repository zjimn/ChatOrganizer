from pathlib import Path

def init_folder():
    dir = Path('data/images')
    dir.mkdir(parents=True, exist_ok=True)