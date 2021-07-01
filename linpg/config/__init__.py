# cython: language_level=3
"""
结构:
base -> setting -> glob -> ui -> info
"""
from .info import *

# 加载设置配置文件
Setting.reload()

# 整理当前文件夹中的配置文件
# Config.organize(os.path.join(os.path.dirname(__file__),"*.json"))
