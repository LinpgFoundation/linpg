# cython: language_level=3
from .config import *

#语言配置文件
__LINPG_LANG = None

#重新加载语言配置文件
def reload_lang() -> None:
    global __LINPG_LANG
    __LINPG_LANG = loadConfig("Lang/{}.yaml".format(get_setting("Language")))

#引擎初始化时应重新加载语言配置文件
reload_lang()

#获取语言配置文件
def get_lang(key:str,key2:str=None) -> any:
    if key2 == None:
        if key in __LINPG_LANG:
            return deepcopy(__LINPG_LANG[key])
        else:
            return None
    else:
        return deepcopy(__LINPG_LANG[key][key2])