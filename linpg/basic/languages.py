import os
from glob import glob
from typing import Any, Final

from ..exception import Exceptions
from .configurations import Configurations
from .getter import TypeSafeGetter
from .settings import Settings
from .specifications import Specifications


# 本地化语言管理模块
class Languages:
    # dict that stores all languages data
    __LANG_DATA: Final[dict[str, Any]] = {}
    # the languages choices that are available
    __LANG_AVAILABLE: tuple[str, ...] = ()

    # 重新加载语言文件
    @classmethod
    def reload(cls) -> None:
        # clear existing language data
        cls.__LANG_DATA.clear()
        # load current language data
        if os.path.exists(path_t := os.path.join(cls.__get_dir(), f"{Settings.get_language()}.json")):
            try:
                cls.__LANG_DATA.update(Configurations.load_file(path_t))
            except Exception:
                Exceptions.inform("Linpg cannot load additional language file.")
        # the languages that are available
        cls.__LANG_AVAILABLE = tuple(Configurations.load(lang_file, "Language") for lang_file in cls.__get_files())

    @staticmethod
    def __get_dir() -> str:
        return Specifications.get_directory("languages")

    # the directory that store all language files
    @classmethod
    def __get_files(cls) -> list[str]:
        return glob(os.path.join(cls.__get_dir(), "*.json"))

    # 获取语言的名称id
    @classmethod
    def get_language_id(cls, lang_name: str) -> str:
        for lang_file in cls.__get_files():
            if Configurations.load(lang_file, "Language") == lang_name:
                return os.path.basename(lang_file).removesuffix(".json")
        return "en_US"

    # 获取可用语言
    @classmethod
    def get_available_languages(cls) -> tuple[str, ...]:
        return cls.__LANG_AVAILABLE

    # 根据key(s)获取对应的语言
    @classmethod
    def get_text(cls, *key: str) -> str:
        return str(TypeSafeGetter.get_by_keys(cls.__LANG_DATA, key))

    # 根据key(s)获取对应的语言 - 与get_text不同，这里返回的是any，通常是列表或者字典
    @classmethod
    def get_texts(cls, *key: str) -> Any:
        return TypeSafeGetter.get_by_keys(cls.__LANG_DATA, key)

    # 查看数据库中是否有对应的名字
    @classmethod
    def contains(cls, name: str) -> bool:
        return name in cls.__LANG_DATA
