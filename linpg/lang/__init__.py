# cython: language_level=3
from typing import Union
from ..config import *

#语言配置文件
_LINPG_LANG:dict = {}

#可选的语言
_LINPG_LANG_AVAILABLE:list = []

#整理语言文件
#organizeConfigInFolder(os.path.join(os.path.dirname(__file__),"*.json"))

#重新加载语言配置文件
def reload_lang() -> None:
    #加载语言文件
    global _LINPG_LANG
    try:
        _LINPG_LANG = {
            **loadConfig(os.path.join("Lang","{}.yaml".format(get_setting("Language")))),
            **loadConfig(os.path.join(os.path.dirname(__file__),"{}.json".format(get_setting("Language"))))
            }
    except:
        throwException("warning", "Linpg cannot load additional language file.")
        _LINPG_LANG = loadConfig(os.path.join(os.path.dirname(__file__),"{}.json".format(get_setting("Language"))))
    #获取本地可用的语言
    global _LINPG_LANG_AVAILABLE
    _LINPG_LANG_AVAILABLE.clear()
    for lang_file in glob(os.path.join(os.path.dirname(__file__),"*.json")):
        _LINPG_LANG_AVAILABLE.append(loadConfig(lang_file, "Language"))

#引擎初始化时应重新加载语言配置文件
reload_lang()

#获取当前的语言
def get_current_language() -> str: return deepcopy(_LINPG_LANG["Language"])

#获取语言的名称id
def get_language_id(lang_name:str) -> str:
    for lang_file in glob(os.path.join(os.path.dirname(__file__),"*.json")):
        if loadConfig(lang_file, "Language") == lang_name: return os.path.basename(lang_file).replace(".json","")
    return ""

#获取可用语言
def get_available_language() -> tuple: return tuple(_LINPG_LANG_AVAILABLE)

#获取语言配置文件
def get_lang(key:str, key2:str=None) -> any:
    if key2 is None:
        try:
            return deepcopy(_LINPG_LANG[key])
        except KeyError:
            throwException(
                "warning",
                'Getting "KeyError" while trying to get {}!\nPlease check your code or report this bug to the developer!'
                .format(key)
                )
            return key
    else:
        try:
            return deepcopy(_LINPG_LANG[key][key2])
        except KeyError:
            throwException(
                "warning",
                'Getting "KeyError" while trying to get {} from {} category!\nPlease check your code or report this bug to the developer!'
                .format(key2,key)
            )
            return key2

#尝试获取语言配置文件
def try_get_lang(key:str, key2:str=None) -> any:
    if key2 is None:
        try:
            return deepcopy(_LINPG_LANG[key])
        except KeyError:
            return key
    else:
        try:
            return deepcopy(_LINPG_LANG[key][key2])
        except KeyError:
            return key2

#获取本地化的数字
def get_num_in_local_text(num:Union[int,str]) -> str:
    num = int(num)
    try:
        return deepcopy(_LINPG_LANG["Numbers"][num])
    except:
        return str(num)