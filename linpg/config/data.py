from .modules import *

# 数据库
class DataBase:

    # 用于存放数据库数据的字典
    __DATA_BASE_DICT: Final[dict] = {"Tiles": {}, "Decorations": {}, "Npc": {}, "Filters": {}}

    @classmethod
    def get(cls, *_key: str) -> Any:
        return get_value_by_keys(cls.__DATA_BASE_DICT, _key)

    @classmethod
    def update(cls, _value: dict) -> None:
        for key, value in _value.items():
            if key not in cls.__DATA_BASE_DICT:
                cls.__DATA_BASE_DICT[key] = value
            else:
                cls.__DATA_BASE_DICT[key].update(value)


# 全局数据
class GlobalVariables:

    # 用于存放全局数据的字典
    __GLOBAL_VARIABLES_DICT: Final[dict] = {}

    # 获取特定的全局数据
    @classmethod
    def get(cls, _key: str) -> object:
        return cls.__GLOBAL_VARIABLES_DICT[_key]

    # 以str的形式获取特定的全局数据
    @classmethod
    def get_str(cls, _key: str) -> str:
        return str(cls.__GLOBAL_VARIABLES_DICT[_key])

    # 尝试以str的形式获取特定的全局数据
    @classmethod
    def try_get_str(cls, _key: str) -> Optional[str]:
        _temp = cls.__GLOBAL_VARIABLES_DICT.get(_key)
        return str(_temp) if _temp is not None else _temp

    # 以int的形式获取特定的全局数据
    @classmethod
    def get_int(cls, _key: str) -> int:
        return int(cls.__GLOBAL_VARIABLES_DICT[_key])

    # 尝试以int的形式获取特定的全局数据
    @classmethod
    def try_get_int(cls, _key: str) -> Optional[int]:
        _temp = cls.__GLOBAL_VARIABLES_DICT.get(_key)
        return int(_temp) if _temp is not None else _temp

    # 以dict的形式获取特定的全局数据
    @classmethod
    def get_dict(cls, _key: str) -> dict:
        return dict(cls.__GLOBAL_VARIABLES_DICT[_key])

    # 尝试以dict的形式获取特定的全局数据
    @classmethod
    def try_get_dict(cls, _key: str) -> Optional[dict]:
        _temp = cls.__GLOBAL_VARIABLES_DICT.get(_key)
        return dict(_temp) if _temp is not None else _temp

    # 是否值存在且不为None
    @classmethod
    def is_not_none(cls, _key: str) -> bool:
        return cls.__GLOBAL_VARIABLES_DICT.get(_key) is not None

    # 设置特定的全局数据
    @classmethod
    def set(cls, _key: str, value: object) -> None:
        cls.__GLOBAL_VARIABLES_DICT[_key] = value

    # 删除特定的全局数据
    @classmethod
    def remove(cls, _key: str) -> None:
        cls.__GLOBAL_VARIABLES_DICT.pop(_key, None)

    # 清空所有全局数据
    @classmethod
    def clear(cls) -> None:
        cls.__GLOBAL_VARIABLES_DICT.clear()

    # 如果不是对应的值，则设置为对应的值，返回是否对应
    @classmethod
    def if_get_set(cls, _key: str, valueToGet: object, valueToSet: object) -> bool:
        if cls.__GLOBAL_VARIABLES_DICT[_key] == valueToGet:
            cls.__GLOBAL_VARIABLES_DICT[_key] = valueToSet
            return True
        else:
            return False
