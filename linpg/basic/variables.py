import os
from typing import Any, Final

from .configurations import Configurations
from .files import Files
from .getter import TypeSafeGetter
from .setter import TypeSafeSetter
from .specifications import Specifications


# 全局数据
class GlobalVariables(TypeSafeGetter, TypeSafeSetter):
    # 用于存放全局数据的字典
    __GLOBAL_VARIABLES_DICT: Final[dict] = {}

    @classmethod
    def _get_data(cls) -> dict:
        return cls.__GLOBAL_VARIABLES_DICT

    # 删除特定的全局数据
    @classmethod
    def remove(cls, _key: str) -> None:
        cls.__GLOBAL_VARIABLES_DICT.pop(_key, None)

    # 如果不是对应的值，则设置为对应的值，返回是否对应
    @classmethod
    def if_get_set(cls, _key: str, valueToGet: object, valueToSet: object) -> bool:
        if cls.__GLOBAL_VARIABLES_DICT[_key] == valueToGet:
            cls.__GLOBAL_VARIABLES_DICT[_key] = valueToSet
            return True
        else:
            return False


# debug模块
class Debug:
    # 是否开启开发者模式
    __ENABLE_DEVELOPER_MODE: bool = False
    # 是否开启作弊
    __ENABLE_CHEATING: bool = False
    # 是否展示Fps
    __SHOW_FPS: bool = False

    # 开发者模式
    @classmethod
    def get_developer_mode(cls) -> bool:
        return cls.__ENABLE_DEVELOPER_MODE

    @classmethod
    def set_developer_mode(cls, value: bool) -> None:
        cls.__ENABLE_DEVELOPER_MODE = value

    # 作弊模式
    @classmethod
    def get_cheat_mode(cls) -> bool:
        return cls.__ENABLE_CHEATING

    @classmethod
    def set_cheat_mode(cls, value: bool) -> None:
        cls.__ENABLE_CHEATING = value

    # 展示Fps
    @classmethod
    def get_show_fps(cls) -> bool:
        return cls.__SHOW_FPS

    @classmethod
    def set_show_fps(cls, value: bool) -> None:
        cls.__SHOW_FPS = value


# 持久数据管理IO
class PersistentVariables(TypeSafeGetter, TypeSafeSetter):
    __DATA: Final[dict[str, Any]] = {}
    __PATH: Final[str] = Specifications.get_directory("save", "persistent.json")

    @classmethod
    def _get_data(cls) -> dict:
        return cls.__DATA

    @classmethod
    def set(cls, *_key: str, value: Any, assumeKeyExists: bool = False) -> None:
        super().set(*_key, value=value, assumeKeyExists=assumeKeyExists)
        cls.save()

    @classmethod
    def reload(cls) -> None:
        cls.__DATA.clear()
        if os.path.exists(cls.__PATH):
            cls.__DATA.update(Configurations.load_file(cls.__PATH))

    @classmethod
    def save(cls) -> None:
        if len(cls.__DATA) > 0:
            Configurations.save(cls.__PATH, cls.__DATA)
        else:
            Files.delete(cls.__PATH)
