"""
结构:
component -> render -> abstract -> dialog -> editor
"""

from .editor import *


# 在指定目录创建项目
def create_new_project(dir_path: str, config_type: str = "json") -> None:
    # 如果项目文件夹不存在，则创建一个
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    # 确保目标是一个文件夹
    if os.path.isdir(dir_path):
        # 根据模块生成项目信息
        info_data: dict = {
            "author": "Put your name here",
            "default_language": Setting.get_language(),
            "link": "https://whateve-you-want/maybe-your-github-link",
            "linpg_version": Info.get_current_version(),
            "title": {},
            "version": "0.0",
        }
        info_data["title"][Setting.get_language()] = Lang.get_text("Editor", "example_project")
        Config.save(os.path.join(dir_path, f"info.{config_type}"), info_data)
    else:
        EXCEPTION.fatal(f'Target path "{dir_path}" cannot be a file path!')
