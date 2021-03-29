# cython: language_level=3
from .controller import *

#语言配置文件
__LINPG_LANG:dict = None

"""
#整理语言文件
for lang_file in glob.glob(os.path.join(os.path.dirname(__file__),"../lang/*.yaml")):
    organizeConfigInFolder(lang_file)
"""

#重新加载语言配置文件
def reload_lang() -> None:
    global __LINPG_LANG
    __LINPG_LANG = dicMerge(
        loadConfig(os.path.join(os.path.dirname(__file__),"../lang/{}.yaml".format(get_setting("Language")))),
        loadConfig("Lang/{}.yaml".format(get_setting("Language")))
        )

#引擎初始化时应重新加载语言配置文件
reload_lang()

#获取语言配置文件
def get_lang(key:str, key2:str=None) -> any:
    if key2 == None:
        if key in __LINPG_LANG:
            return deepcopy(__LINPG_LANG[key])
        else:
            return None
    else:
        return deepcopy(__LINPG_LANG[key][key2])

#获取本地化的数字
def get_num_in_local_text(num:Union[int,str]) -> str:
    num = int(num)
    try:
        return deepcopy(__LINPG_LANG["Numbers"][num])
    except:
        return str(num)