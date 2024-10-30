import os
import sys
from dotenv import load_dotenv

def resource_path(relative_path):
    """获取资源路径"""
    if getattr(sys, 'frozen', False):
        # 如果是打包后的应用
        base_path = sys._MEIPASS
    else:
        # 如果是普通的 Python 脚本
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)