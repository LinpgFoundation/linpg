import sys
from .setting import *

# debug模块
class Debug:

    # 是否开启开发者模式
    __ENABLE_DEVELOPER_MODE: bool = bool(Setting.get("DeveloperMode"))
    # 是否开启作弊
    __ENABLE_CHEATING: bool = False
    # 是否展示Fps
    __SHOW_FPS: bool = False
    # 是否在windows上运行
    __RUNNING_WINDOWS: bool = sys.platform.startswith("win")

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

    # 是否在windows上运行
    @classmethod
    def is_running_on_windows(cls) -> bool:
        return cls.__RUNNING_WINDOWS
