"""
结构:
exception -> config -> lang -> tools -> basic -> core -> ui -> dialog -> map -> character -> battle -> api
"""
from .api import *
from platform import python_version

"""整理linpg内部"""
clean_up: bool = False
if clean_up is True:
    # 移除__pycache__文件（debug用途）
    Builder.search_and_remove_folder(os.path.dirname(__file__), "__pycache__")
    # 整理语言
    Lang.organize()
    # 整理内部设置配置文件
    Config.organize_internal()

print("linpg {0} ({1}, Python {2})".format(Info.get_current_version(), get_library_info(), python_version()))
print("Hello from the linpg community. {}".format(Info.get_repository_url()))
