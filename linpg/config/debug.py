from .setting import *

# debug模块
class Debug:

    # 是否开启作弊
    __ENABLE_CHEATING: bool = False
    # 是否展示Fps
    __SHOW_FPS: bool = False

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