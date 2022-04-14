"""
结构:
dialogbox-> component -> character -> script -> abstract -> dialog -> converter -> editor
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
        info_data: dict = Template.get("info")
        info_data["default_lang"] = Setting.language
        info_data["linpg_version"] = Info.get_current_version()
        Config.save(os.path.join(dir_path, "info.{}".format(config_type)), info_data)
    else:
        EXCEPTION.fatal('Target path "{}" cannot be a file path!'.format(dir_path))
