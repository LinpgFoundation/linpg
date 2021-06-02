# cython: language_level=3
from .setting import *

"""全局数据"""
_LINPG_GLOBAL_DATA: dict = {}

# 设置特定的全局数据
def set_glob_value(key: str, value: any) -> None:
    global _LINPG_GLOBAL_DATA
    _LINPG_GLOBAL_DATA[key] = value

# 获取特定的全局数据
def get_glob_value(key: str) -> any:
    return deepcopy(_LINPG_GLOBAL_DATA[key])

# 如果不是对应的值，则设置为对应的值，返回是否对应
def if_get_set_value(key: str, valueToGet: any, valueToSet: any) -> bool:
    global _LINPG_GLOBAL_DATA
    if _LINPG_GLOBAL_DATA[key] == valueToGet:
        _LINPG_GLOBAL_DATA[key] = valueToSet
        return True
    else:
        return False

# 删除特定的全局数据
def remove_glob_value(key: str) -> None:
    global _LINPG_GLOBAL_DATA
    del _LINPG_GLOBAL_DATA[key]
