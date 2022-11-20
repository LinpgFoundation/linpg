from typing import Union

from ..config import *

# 名称类
strint = Union[str, int]


# 本地化语言管理模块
class Lang:

    # 语言配置文件
    __LANG_DATA: Final[dict] = {}
    # 可选的语言
    __LANG_AVAILABLE: Final[list] = []
    # 语言储存路径
    __LANG_PATH_PATTERN: Final[str] = os.path.join(os.path.dirname(__file__), "*.json")
    # 储存额外语言数据的文件夹
    __EX_LANG_FOLDER: Final[str] = "Lang"

    # 重新加载语言文件
    @classmethod
    def reload(cls) -> None:
        # 加载引擎内部的默认语言文件
        cls.__LANG_DATA.clear()
        cls.__LANG_DATA.update(Config.load_file(os.path.join(os.path.dirname(__file__), "{}.json".format(Setting.get_language()))))
        # 加载游戏自定义的外部语言文件
        path_t: str
        if os.path.exists(path_t := os.path.join(cls.__EX_LANG_FOLDER, "{0}.{1}".format(Setting.get_language(), Config.get_file_type()))) or os.path.exists(
            path_t := os.path.join(cls.__EX_LANG_FOLDER, "{}.json".format(Setting.get_language()))
        ):
            try:
                cls.__LANG_DATA.update(Config.load_file(path_t))
            except Exception:
                EXCEPTION.inform("Linpg cannot load additional language file.")
        # 获取当前所有完整的可用语言的列表
        cls.__LANG_AVAILABLE.clear()
        # 如果有开发者自带的语言文件
        if os.path.exists("Lang"):
            for lang_file in glob(os.path.join(cls.__LANG_PATH_PATTERN)):
                if os.path.exists(os.path.join(cls.__EX_LANG_FOLDER, os.path.basename(lang_file).replace(".json", ".yaml"))) or os.path.exists(
                    os.path.join(cls.__EX_LANG_FOLDER, os.path.basename(lang_file))
                ):
                    cls.__LANG_AVAILABLE.append(Config.load(lang_file, "Language"))
        else:
            for lang_file in glob(os.path.join(cls.__LANG_PATH_PATTERN)):
                cls.__LANG_AVAILABLE.append(Config.load(lang_file, "Language"))

    # 整理语言文件
    @classmethod
    def organize(cls) -> None:
        Config.organize(os.path.join(cls.__LANG_PATH_PATTERN))
        cls.reload()

    # 获取当前的语言
    @classmethod
    def get_current_language(cls) -> str:
        return str(cls.__LANG_DATA["Language"])

    # 获取语言的名称id
    @classmethod
    def get_language_id(cls, lang_name: str) -> str:
        for lang_file in glob(os.path.join(cls.__LANG_PATH_PATTERN)):
            if Config.load(lang_file, "Language") == lang_name:
                return os.path.basename(lang_file).removesuffix(".json")
        return ""

    # 获取可用语言
    @classmethod
    def get_available_languages(cls) -> tuple:
        return tuple(cls.__LANG_AVAILABLE)

    # 根据key(s)获取对应的语言
    @classmethod
    def get_text(cls, *key: str) -> str:
        return str(get_value_by_keys(cls.__LANG_DATA, key))

    @classmethod
    def get_text_by_keys(cls, keys: tuple) -> str:
        return str(get_value_by_keys(cls.__LANG_DATA, keys))

    # 根据key(s)获取对应的语言 - 与get_text不同，这里返回的是any，通常是列表或者字典
    @classmethod
    def get_texts(cls, *key: str) -> Any:
        return get_value_by_keys(cls.__LANG_DATA, key)

    # 获取本地化的数字
    @classmethod
    def get_num_in_local_text(cls, num: strint) -> str:
        try:
            return str(cls.__LANG_DATA["Numbers"][int(num)])
        except Exception:
            return str(num)

    # 查看数据库中是否有对应的名字
    @classmethod
    def has_key(cls, name: str) -> bool:
        return name in cls.__LANG_DATA


# 初始化
Lang.reload()
