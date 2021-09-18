from typing import Union
from ..config import *

# 名称类
strint = Union[str, int]


class LanguageManager:
    def __init__(self) -> None:
        # 语言配置文件
        self.__LANG_DATA: dict = {}
        # 可选的语言
        self.__LANG_AVAILABLE: list = []
        # 语言储存路径
        self.__LANG_PATH_PATTERN: str = os.path.join(os.path.dirname(__file__), "*.json")
        # 储存额外语言数据的文件夹
        self.__EX_LANG_FOLDER: str = "Lang"
        # 初始化
        self.reload()

    # 重新加载语言文件
    def reload(self) -> None:
        # 加载引擎内部的默认语言文件
        self.__LANG_DATA = dict(Config.load(os.path.join(os.path.dirname(__file__), "{}.json".format(Setting.language))))
        # 加载游戏自定义的外部语言文件
        path_t: str
        if os.path.exists(
            path_t := os.path.join(self.__EX_LANG_FOLDER, "{}.yaml".format(Setting.language))
        ) or os.path.exists(path_t := os.path.join(self.__EX_LANG_FOLDER, "{}.json".format(Setting.language))):
            try:
                self.__LANG_DATA.update(Config.load(path_t))
            except Exception:
                EXCEPTION.inform("Linpg cannot load additional language file.")
        # 获取当前所有完整的可用语言的列表
        self.__LANG_AVAILABLE.clear()
        # 如果有开发者自带的语言文件
        if os.path.exists("Lang"):
            for lang_file in glob(os.path.join(self.__LANG_PATH_PATTERN)):
                if os.path.exists(
                    os.path.join(self.__EX_LANG_FOLDER, os.path.basename(lang_file).replace(".json", ".yaml"))
                ) or os.path.exists(os.path.join(self.__EX_LANG_FOLDER, os.path.basename(lang_file))):
                    self.__LANG_AVAILABLE.append(Config.load(lang_file, "Language"))
        else:
            for lang_file in glob(os.path.join(self.__LANG_PATH_PATTERN)):
                self.__LANG_AVAILABLE.append(Config.load(lang_file, "Language"))

    # 整理语言文件
    def organize(self) -> None:
        Config.organize(os.path.join(self.__LANG_PATH_PATTERN))
        self.reload()

    # 获取当前的语言
    @property
    def current_language(self) -> str:
        return self.__LANG_DATA["Language"]

    # 获取语言的名称id
    def get_language_id(self, lang_name: str) -> str:
        for lang_file in glob(os.path.join(self.__LANG_PATH_PATTERN)):
            if Config.load(lang_file, "Language") == lang_name:
                return os.path.basename(lang_file).removesuffix(".json")
        return ""

    # 获取可用语言
    def get_available_languages(self) -> tuple:
        return tuple(self.__LANG_AVAILABLE)

    # 根据key(s)获取对应的语言
    def get_text(self, *key: str) -> any:
        return get_value_by_keys(self.__LANG_DATA, key)

    def get_text_by_keys(self, keys: tuple) -> any:
        return get_value_by_keys(self.__LANG_DATA, keys if isinstance(keys, tuple) else tuple(keys))

    # 尝试根据key(s)获取对应的语言
    def try_to_get_text(self, *key: str) -> any:
        return get_value_by_keys(self.__LANG_DATA, key, False)

    # 获取本地化的数字
    def get_num_in_local_text(self, num: strint) -> str:
        try:
            return deepcopy(self.__LANG_DATA["Numbers"][int(num)])
        except Exception:
            return str(num)


Lang: LanguageManager = LanguageManager()
