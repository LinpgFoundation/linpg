import os
from typing import Final

from ..abstracts.getter import TypeSafeGetter
from ..exception import Exceptions


# 使用引擎的开发者可以自定义的参数
class Specifications(TypeSafeGetter):
    # init specification with default parameters
    __SPECIFICATIONS: Final[dict[str, dict]] = {
        "Achievements": {},
        "DefaultFont": {"font": "Arial", "type": "default"},
        "DefaultSetting": {
            "AntiAlias": True,
            "EnableOpenGL": False,
            "EnableVerticalSync": False,
            "Language": "English",
            "LowMemoryMode": False,
            "MaxFps": 999,
            "MonitorToDisplay": 0,
            "MouseIconWidth": 25,
            "MouseMoveSpeed": 25,
            "NumberOfChannels": 8,
            "ReadingSpeed": 1,
            "Resolution": {"height": 1080, "scale": 100, "width": 1920},
            "Sound": {"background_music": 100, "effects": 100, "environment": 100, "global_value": 100},
        },
        "Directories": {
            "background_image": ["Assets", "image", "dialog_background"],
            "cache": ["Cache"],
            "character_icon": ["Assets", "image", "npc_icon"],
            "character_image": ["Assets", "image", "npc"],
            "character_sound": ["Assets", "sound", "character"],
            "environment": ["Assets", "image", "environment"],
            "font": ["Assets", "font"],
            "movie": ["Assets", "movie"],
            "music": ["Assets", "music"],
            "save": ["Save"],
            "screenshots": ["screenshots"],
            "setting": ["Save"],
            "sound": ["Assets", "sound"],
            "sprite": ["Assets", "image", "sprites"],
            "user_interface": ["Assets", "image", "ui"],
        },
    }

    @classmethod
    def init(cls, spec: dict) -> None:
        cls.__SPECIFICATIONS.update(spec)

    @classmethod
    def get_directory(cls, category: str, *_sub: str) -> str:
        return str(os.path.join(*cls.__SPECIFICATIONS["Directories"][category], *_sub))


# 版本信息管理模块
class Version:
    # 引擎主版本号
    __VERSION: Final[int] = 4
    # 引擎次更新版本号
    __REVISION: Final[int] = 0
    # 引擎补丁版本
    __PATCH: Final[int] = 0

    # 确保linpg版本
    @classmethod
    def ensure_linpg_version(cls, action: str, revision: int, patch: int, version: int = 3) -> bool:
        match action:
            case "==":
                return cls.__VERSION == version and cls.__REVISION == revision and cls.__PATCH == patch
            case ">=":
                return cls.__VERSION >= version and cls.__REVISION >= revision and cls.__PATCH >= patch
            case "<=":
                return cls.__VERSION <= version and cls.__REVISION <= revision and cls.__PATCH <= patch
            case _:
                Exceptions.fatal(f'Action "{action}" is not supported!')

    # 获取当前版本号
    @classmethod
    def get_current_version(cls) -> str:
        return f"{cls.__VERSION}.{cls.__REVISION}.{cls.__PATCH}"

    # 获取github项目地址
    @classmethod
    def get_repository_url(cls) -> str:
        return "https://github.com/LinpgFoundation/linpg"
