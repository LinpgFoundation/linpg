# cython: language_level=3
"""
结构:
base -> setting -> glob -> ui -> info
"""
from .info import *

# 加载设置配置文件
reload_setting()

# 整理当前文件夹中的配置文件
# organize_config_in_folder(os.path.join(os.path.dirname(__file__),"*.json"))
