import os
from typing import Final

from .getter import TypeSafeGetter


# 使用引擎的开发者可以自定义的参数
class Specifications(TypeSafeGetter):
    # init specification with default parameters
    __SPECIFICATIONS: Final[dict[str, dict]] = {
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
            "languages": ["Languages"],
        },
    }

    @classmethod
    def update(cls, spec: dict) -> None:
        cls.__SPECIFICATIONS.update(spec)

    @classmethod
    def _get_data(cls) -> dict:
        return cls.__SPECIFICATIONS

    @classmethod
    def get_directory(cls, category: str, *_sub: str) -> str:
        return str(os.path.join(*cls.__SPECIFICATIONS["Directories"][category], *_sub))
