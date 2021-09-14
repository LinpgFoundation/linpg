"""
结构:
base -> setting -> glob -> info
"""
from .info import *

# 加载设置配置文件
Setting.reload()
