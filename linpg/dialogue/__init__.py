"""
结构:
component -> render -> abstract -> dialogue
"""

from .dialogue import *


# 在指定目录创建项目
def create_new_project(dir_path: str) -> None:
    # 如果项目文件夹不存在，则创建一个
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    # 确保目标是一个文件夹
    if os.path.isdir(dir_path):
        # 根据模块生成项目信息
        info_data: dict = {
            "author": "Put your name here",
            "default_language": Settings.get_language(),
            "link": "https://whateve-you-want/maybe-your-github-link",
            "linpg_version": Version.get_current_version(),
            "title": {},
            "version": "0.0",
        }
        info_data["title"][Settings.get_language()] = Languages.get_text("Editor", "example_project")
        Configurations.save(os.path.join(dir_path, f"info.json"), info_data)
    else:
        Exceptions.fatal(f'Target path "{dir_path}" cannot be a file path!')
