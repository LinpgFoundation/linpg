# cython: language_level=3
from .base import *

class SettingSystem:
    def __init__(self) -> None:
        #储存设置配置文件的数据
        self.__SETTING_DATA:dict = {}
        #当前配置文件保存路径的参数
        self.__SETTING_FOLDER_PATH:str = "Save"
        self.__SETTING_FILE_NAME:str = "setting.yaml"
        #初始化
        self.reload()
    #获取配置文件保存的路径
    def get_config_path(self) -> str: return os.path.join(self.__SETTING_FOLDER_PATH, self.__SETTING_FILE_NAME)
    #设置配置文件保存的路径
    def set_config_path(self, path:str) -> None: self.__SETTING_FOLDER_PATH, self.__SETTING_FILE_NAME = os.path.split(path)
    #重新加载设置数据
    def reload(self) -> None:
        #如果配置文件setting.yaml存在
        if os.path.exists(self.get_config_path()): self.__SETTING_DATA = load_config(self.get_config_path())
        #如果不存在就创建一个
        else:
            #导入local,查看默认语言
            import locale
            self.__SETTING_DATA = load_config(os.path.join(os.path.dirname(__file__), "setting.json"))
            self.__SETTING_DATA["Language"] = "SimplifiedChinese" if locale.getdefaultlocale()[0] == "zh_CN" else "English"
            #保存设置
            self.save()
    #保存设置数据
    def save(self) -> None: save_config(self.get_config_path(), self.__SETTING_DATA)
    #获取设置数据
    def get(self, *key:str) -> any: return self.get_by_keys(key)
    def get_by_keys(self, keys:tuple) -> any: return get_value_by_keys(self.__SETTING_DATA, keys)
    #在不确定的情况下尝试获取设置数据
    def try_get(self, *key:str) -> any: return get_value_by_keys(self.__SETTING_DATA, key, False)
    #修改设置数据
    def set(self, key:str, key2:str=None, value:any=None) -> None:
        if value is not None:
            if key2 is None:
                self.__SETTING_DATA[key] = value
            else:
                self.__SETTING_DATA[key][key2] = value
        else:
            throw_exception("error", "You need to enter a valid value!")
    def set_and_save(self, key:str, key2:str=None, value:any=None) -> None:
        self.set(key, key2, value)
        self.save()
    """其他常用的重要参数"""
    #获取文字信息
    @property
    def font(self) -> str: return str(self.__SETTING_DATA["Font"])
    #获取文字类型
    @property
    def font_type(self) -> str: return str(self.__SETTING_DATA["FontType"])
    #获取抗锯齿参数
    @property
    def antialias(self) -> bool: return self.__SETTING_DATA["Antialias"] is True

Setting:SettingSystem = SettingSystem()

"""即将弃置"""
#重新加载设置配置文件，请勿在引擎外调用，重置配置文件请用reload_setting()
def reload_setting() -> None: Setting.reload()
#保存设置参数
def save_setting() -> None: Setting.save()
#获取配置文件保存的路径
def get_setting_path() -> str: return Setting.get_config_path()
#设置配置文件保存的路径
def set_setting_path(path:str) -> None: Setting.set_config_path(path)
#获取设置配置文件
def get_setting(*keys:str) -> any: return  Setting.get_by_keys(keys)
#在不确定的情况下尝试获取设置配置文件
def try_get_setting(*keys:str) -> any: throw_exception("error", "No longer variable!")
#修改设置参数
def set_setting(key:str, key2:str=None, value:any=None) -> None: Setting.set(key, key2, value)
#修改设置参数并保存
def set_and_save_setting(key:str, key2:str=None, value:any=None) -> None: Setting.set_and_save(key, key2, value)
#获取抗锯齿参数
def get_antialias() -> bool: return Setting.antialias
#获取文字信息
def get_font() -> str: return Setting.font
#设置文字信息
def set_font(value:str) -> None: throw_exception("error", "No longer variable!")
#获取文字类型
def get_font_type() -> str: return Setting.font_type
#设置文字类型
def set_font_type(value:str) -> None: throw_exception("error", "No longer variable!")
#获取文字的具体信息
def get_font_details() -> tuple: return throw_exception("error", "No longer variable!")