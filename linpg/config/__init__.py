"""
结构:
base -> setting -> debug -> manager
"""
from .manager import *


# 加载设置配置文件
Setting.reload()
