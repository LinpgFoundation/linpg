# cython: language_level=3
"""
结构:
base -> setting -> ui -> info
"""
from .info import *

# 加载设置配置文件
Setting.reload()
