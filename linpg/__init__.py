"""
结构:
exception -> abstracts -> config -> language -> basic -> core -> ui -> dialogue -> battle -> api
"""
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
print(f'linpg {Info.get_current_version()} ({f"{GraphicLibrary.get_name()} {pygame.version.ver}"}, Python {EXCEPTION.get_python_version()})')
# only show prompt when using pygame
if GraphicLibrary.is_using_pygame():
    print(f"Hello from the linpg community. {Info.get_repository_url()}")
