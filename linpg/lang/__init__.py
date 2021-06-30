# cython: language_level=3
from typing import Union
from ..config import *

class LanguageManager:
    def __init__(self) -> None:
        #语言配置文件
        self.__LINPG_LANG:dict = {}
        #可选的语言
        self.__LINPG_LANG_AVAILABLE:list = []
        # 语言储存路径
        self.__LANG_PATH:str = os.path.join(os.path.dirname(__file__), "*.json")
        #初始化
        self.reload()
    #重新加载语言文件
    def reload(self) -> None:
        if os.path.exists(os.path.join("Lang","{}.yaml".format(get_setting("Language")))):
            self.__LINPG_LANG = {
                **load_config(os.path.join("Lang","{}.yaml".format(get_setting("Language")))),
                **load_config(os.path.join(os.path.dirname(__file__),"{}.json".format(get_setting("Language"))))
                }
        elif os.path.exists(os.path.join("Lang","{}.json".format(get_setting("Language")))):
            self.__LINPG_LANG = {
                **load_config(os.path.join("Lang","{}.json".format(get_setting("Language")))),
                **load_config(os.path.join(os.path.dirname(__file__),"{}.json".format(get_setting("Language"))))
                }
        else:
            throw_exception("warning", "Linpg cannot load additional language file.")
            self.__LINPG_LANG = load_config(os.path.join(os.path.dirname(__file__),"{}.json".format(get_setting("Language"))))
        #获取本地可用的语言
        self.__LINPG_LANG_AVAILABLE.clear()
        for lang_file in glob(os.path.join(self.__LANG_PATH)):
            if os.path.exists(os.path.join("Lang",os.path.basename(lang_file).replace(".json",".yaml"))) or \
                os.path.exists(os.path.join("Lang",os.path.basename(lang_file))):
                self.__LINPG_LANG_AVAILABLE.append(load_config(lang_file, "Language"))
    #整理语言文件
    def organize(self) -> None:
        organize_config_in_folder(os.path.join(self.__LANG_PATH))
        self.reload()
    #获取当前的语言
    def get_current_language(self) -> str: return deepcopy(self.__LINPG_LANG["Language"])
    #获取语言的名称id
    def get_language_id(self, lang_name:str) -> str:
        for lang_file in glob(os.path.join(self.__LANG_PATH)):
            if load_config(lang_file, "Language") == lang_name: return os.path.basename(lang_file).replace(".json","")
        return ""
    #获取可用语言
    def get_available_languages(self) -> tuple: return tuple(self.__LINPG_LANG_AVAILABLE)
    #根据key(s)获取对应的语言
    def get_text(self, *key:str) -> any: return get_value_by_keys(self.__LINPG_LANG, key)
    def get_text_by_keys(self, keys:Union[tuple, list]) -> any:
        return get_value_by_keys(self.__LINPG_LANG, tuple(keys)) if not isinstance(keys, tuple) else get_value_by_keys(self.__LINPG_LANG, keys)
    #尝试根据key(s)获取对应的语言
    def try_to_get_text(self, *key:str) -> any: return get_value_by_keys(self.__LINPG_LANG, key, False)
    #获取本地化的数字
    def get_num_in_local_text(self, num:Union[int,str]) -> str:
        try:
            return deepcopy(self.__LINPG_LANG["Numbers"][int(num)])
        except Exception:
            return str(num)

Lang:LanguageManager = LanguageManager()

#Lang.organize()

"""即将弃置"""
#重新加载语言配置文件
def reload_lang() -> None: Lang.reload()
#获取当前的语言
def get_current_language() -> str: return Lang.get_current_language()
#获取语言的名称id
def get_language_id(lang_name:str) -> str: Lang.get_language_id(lang_name)
#获取可用语言
def get_available_language() -> tuple: return Lang.get_available_languages()
#根据key(s)获取对应的语言
def get_lang(*keys:str) -> any: return Lang.get_text_by_keys(keys)
def get_lang_by_keys(keys:Union[tuple, list]) -> any: Lang.get_text_by_keys(keys)
#获取本地化的数字
def get_num_in_local_text(num:Union[int,str]) -> str: Lang.get_num_in_local_text(num)