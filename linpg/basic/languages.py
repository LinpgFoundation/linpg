import os
from glob import glob
from typing import Any, Final

from ..exception import Exceptions
from .configurations import Configurations
from .getter import TypeSafeGetter
from .settings import Settings


# 本地化语言管理模块
class Languages:
    # 语言配置文件
    __LANG_DATA: Final[dict[str, Any]] = {}
    # 可选的语言
    __LANG_AVAILABLE: tuple[str, ...] = ()
    # 语言储存路径
    __LANG_PATH_PATTERN: Final[str] = os.path.join(os.path.dirname(__file__), "*.json")
    # 储存额外语言数据的文件夹
    __EX_LANG_FOLDER: Final[str] = "Lang"
    # 语言tga
    __LANG_TAGS: Final[dict[str, str]] = {"English": "en-US", "SimplifiedChinese": "zh-CN", "TraditionalChinese": "zh-TW"}

    # 重新加载语言文件
    @classmethod
    def reload(cls) -> None:
        # 加载引擎内部的默认语言文件
        cls.__LANG_DATA.clear()
        cls.__LANG_DATA.update(
            Configurations.load_file(os.path.join(os.path.dirname(__file__), f"{Settings.get_language()}.json"))
        )
        # 加载游戏自定义的外部语言文件
        path_t: str
        if os.path.exists(path_t := os.path.join(cls.__EX_LANG_FOLDER, f"{Settings.get_language()}.json")) or os.path.exists(
            path_t := os.path.join(cls.__EX_LANG_FOLDER, f"{Settings.get_language()}.json")
        ):
            try:
                cls.__LANG_DATA.update(Configurations.load_file(path_t))
            except Exception:
                Exceptions.inform("Linpg cannot load additional language file.")
        # 如果有开发者自带的语言文件
        cls.__LANG_AVAILABLE = (
            tuple(
                Configurations.load(lang_file, "Language")
                for lang_file in glob(os.path.join(cls.__LANG_PATH_PATTERN))
                if os.path.exists(os.path.join(cls.__EX_LANG_FOLDER, os.path.basename(lang_file).replace(".json", ".yaml")))
                or os.path.exists(os.path.join(cls.__EX_LANG_FOLDER, os.path.basename(lang_file)))
            )
            if os.path.exists("Lang")
            else tuple(Configurations.load(lang_file, "Language") for lang_file in glob(os.path.join(cls.__LANG_PATH_PATTERN)))
        )

    # 获取当前的语言
    @classmethod
    def get_current_language(cls) -> str:
        return str(cls.__LANG_DATA["Language"])

    # 获取当前的语言
    @classmethod
    def get_current_language_tag(cls) -> str:
        return cls.__LANG_TAGS[Settings.get_language()]

    # 获取语言的名称id
    @classmethod
    def get_language_id(cls, lang_name: str) -> str:
        for lang_file in glob(os.path.join(cls.__LANG_PATH_PATTERN)):
            if Configurations.load(lang_file, "Language") == lang_name:
                return os.path.basename(lang_file).removesuffix(".json")
        return ""

    # 获取可用语言
    @classmethod
    def get_available_languages(cls) -> tuple:
        return tuple(cls.__LANG_AVAILABLE)

    # 根据key(s)获取对应的语言
    @classmethod
    def get_text(cls, *key: str) -> str:
        return str(TypeSafeGetter.get_by_keys(cls.__LANG_DATA, key))

    @classmethod
    def get_text_by_keys(cls, keys: tuple) -> str:
        return str(TypeSafeGetter.get_by_keys(cls.__LANG_DATA, keys))

    # 根据key(s)获取对应的语言 - 与get_text不同，这里返回的是any，通常是列表或者字典
    @classmethod
    def get_texts(cls, *key: str) -> Any:
        return TypeSafeGetter.get_by_keys(cls.__LANG_DATA, key)

    # 获取本地化的数字
    @classmethod
    def get_num_in_local_text(cls, num: str | int) -> str:
        try:
            return str(cls.__LANG_DATA["Numbers"][int(num)])
        except Exception:
            return str(num)

    # 查看数据库中是否有对应的名字
    @classmethod
    def has_key(cls, name: str) -> bool:
        return name in cls.__LANG_DATA
