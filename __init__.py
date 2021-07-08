#这个__init__.py文件用于直接从linpgdev导入linpg
from .linpg import *

print("Warning: You are importing from dev build of linpg!")

clean_up:bool = False

if clean_up is True:
    #移除__pycache__文件（debug用途）
    config.search_and_remove_folder("linpg","__pycache__")
    #整理语言
    lang.organize()
    # 整理内部设置配置文件
    config.organize_internal()