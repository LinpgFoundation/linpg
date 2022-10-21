"""
结构:
exception -> config -> language -> basic -> core -> ui -> dialogue -> battle -> api
"""
from platform import python_version

from .interface import *

"""整理linpg内部"""
clean_up: bool = False
if clean_up is True:
    # 移除 __pycache__ 文件（debug用途）
    Files.search_and_remove_folder(os.path.dirname(__file__), "__pycache__")
    # 整理语言
    Lang.organize()
    # 整理内部设置配置文件
    Config.organize_internal()

print("linpg {0} ({1}, Python {2})".format(Info.get_current_version(), "Pygame {}".format(pygame.version.ver), python_version()))
print("Hello from the linpg community. {}".format(Info.get_repository_url()))
