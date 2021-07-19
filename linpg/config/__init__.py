"""
结构:
base -> setting -> ui -> info
"""
from .info import *

# 加载设置配置文件
Setting.reload()
