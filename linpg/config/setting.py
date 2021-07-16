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
        #加载内部默认的设置配置文件
        self.__SETTING_DATA = Config.load_internal("setting.json")
        #如果自定义的设置配置文件存在，则加载
        if os.path.exists(self.get_config_path()):
            self.__SETTING_DATA.update(Config.load(self.get_config_path()))
        #如果不存在自定义的设置配置文件，则应该创建一个
        else:
            #导入local,查看默认语言
            import locale
            self.__SETTING_DATA["Language"] = "SimplifiedChinese" if locale.getdefaultlocale()[0] == "zh_CN" else "English"
            #保存设置
            self.save()
    #保存设置数据
    def save(self) -> None: Config.save(self.get_config_path(), self.__SETTING_DATA)
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
            EXCEPTION.fatal("You need to enter a valid value!")
    def set_by_keys(self, keys:tuple, value:any=None) -> None: set_value_by_keys(self.__SETTING_DATA, keys, value)
    #设置参数并立即保存
    def set_and_save(self, key:str, key2:str=None, value:any=None) -> None:
        self.set(key, key2, value)
        self.save()
    """其他常用的重要参数"""
    #文字信息
    @property
    def font(self) -> str: return str(self.__SETTING_DATA["Font"])
    def set_font(self, font_name:str) -> None: self.__SETTING_DATA["Font"] = font_name
    #文字类型
    @property
    def font_type(self) -> str: return str(self.__SETTING_DATA["FontType"])
    def set_font_type(self, font_type:str) -> None: self.__SETTING_DATA["FontType"] = font_type
    #抗锯齿参数
    @property
    def antialias(self) -> bool: return self.__SETTING_DATA["Antialias"] is True
    #语言
    @property
    def language(self) -> str: return self.__SETTING_DATA["Language"]
    @property
    def developer_mode(self) -> bool: return self.__SETTING_DATA["DeveloperMode"] is True

Setting:SettingSystem = SettingSystem()
