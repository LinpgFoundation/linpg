# cython: language_level=3
from .base import *

#初始化储存设置配置文件的变量
_LINPG_SETTING:dict = None

#用于储存当前配置文件保存路径的参数
_LINPG_SETTING_FOLDER_PATH:str = "Save"
_LINPG_SETTING_FILE_NAME:str = "setting.yaml"

#获取配置文件保存的路径
def get_setting_path() -> str: return os.path.join(_LINPG_SETTING_FOLDER_PATH, _LINPG_SETTING_FILE_NAME)

#设置配置文件保存的路径
def set_setting_path(path:str) -> None:
    global _LINPG_SETTING_FOLDER_PATH, _LINPG_SETTING_FILE_NAME
    _LINPG_SETTING_FOLDER_PATH, _LINPG_SETTING_FILE_NAME = os.path.split(path)

#获取设置配置文件
def get_setting(*keys:str) -> any: return get_value_by_keys(_LINPG_SETTING, keys)

#在不确定的情况下尝试获取设置配置文件
def try_get_setting(*keys:str) -> any: get_value_by_keys(_LINPG_SETTING, keys, False)

#修改设置参数
def set_setting(key:str, key2:str=None, value:any=None) -> None:
    if value is not None:
        if key2 is None:
            _LINPG_SETTING[key] = value
        else:
            _LINPG_SETTING[key][key2] = value

#保存设置参数
def save_setting() -> None: save_config(get_setting_path(), _LINPG_SETTING)

#修改设置参数并保存
def set_and_save_setting(key:str, key2:str=None, value:any=None) -> None:
    set_setting(key, key2, value)
    save_setting()

#重新加载设置配置文件，请勿在引擎外调用，重置配置文件请用reload_setting()
def reload_setting() -> None:
    global _LINPG_SETTING
    #如果配置文件setting.yaml存在
    if os.path.exists(get_setting_path()): _LINPG_SETTING = load_config(get_setting_path())
    #如果不存在就创建一个
    else:
        #导入local,查看默认语言
        import locale
        _LINPG_SETTING = load_config(os.path.join(os.path.dirname(__file__), "setting.json"))
        _LINPG_SETTING["Language"] = "SimplifiedChinese" if locale.getdefaultlocale()[0] == "zh_CN" else "English"
        #保存设置
        save_setting()

"""重要参数"""
#获取抗锯齿参数
def get_antialias() -> bool: return _LINPG_SETTING["Antialias"] is True
#获取文字信息
def get_font() -> str: return str(_LINPG_SETTING["Font"])
#设置文字信息
def set_font(value:str) -> None: _LINPG_SETTING["Font"] = value
#获取文字类型
def get_font_type() -> str: return str(_LINPG_SETTING["FontType"])
#设置文字类型
def set_font_type(value:str) -> None: _LINPG_SETTING["FontType"] = value
#获取文字的具体信息
def get_font_details() -> tuple: return get_font(), get_font_type(), get_antialias()