from .base import *


class SettingSystem:

    # 储存设置配置文件的数据
    __SETTING_DATA: dict = {}
    # 内部的配置参数，每次启动初始化
    __INTERNAL_SETTING: dict = {"Cheat": False}
    # 当前配置文件保存路径的参数
    __SETTING_FOLDER_PATH: str = "Save"
    __SETTING_FILE_NAME: str = "setting.{}".format(Config.get_file_type())

    # 初始化
    def __init__(self) -> None:
        self.reload()

    # 获取配置文件保存的路径
    def get_config_path(self) -> str:
        return os.path.join(self.__SETTING_FOLDER_PATH, self.__SETTING_FILE_NAME)

    # 设置配置文件保存的路径
    def set_config_path(self, path: str) -> None:
        self.__SETTING_FOLDER_PATH, self.__SETTING_FILE_NAME = os.path.split(path)

    # 重新加载设置数据
    def reload(self) -> None:
        # 加载内部默认的设置配置文件
        self.__SETTING_DATA = Template.get("setting")
        # 如果自定义的设置配置文件存在，则加载
        if os.path.exists(self.get_config_path()):
            self.__SETTING_DATA.update(Config.load_file(self.get_config_path()))
        # 如果不存在自定义的设置配置文件，则应该创建一个
        else:
            # 导入local,查看默认语言
            import locale

            self.__SETTING_DATA["Language"] = "SimplifiedChinese" if locale.getdefaultlocale()[0] == "zh_CN" else "English"
            # 保存设置
            self.save()

    # 保存设置数据
    def save(self) -> None:
        Config.save(self.get_config_path(), self.__SETTING_DATA)

    # 获取设置数据
    def get(self, *key: str) -> Any:
        return get_value_by_keys(self.__SETTING_DATA, key)

    # 在不确定的情况下尝试获取设置数据
    def try_get(self, *key: str) -> Any:
        return get_value_by_keys(self.__SETTING_DATA, key, False)

    # 修改设置数据
    def set(self, *key: str, value: object) -> None:
        set_value_by_keys(self.__SETTING_DATA, key, value)

    """其他常用的重要参数"""
    # 文字名称
    @property
    def font(self) -> str:
        return str(self.__SETTING_DATA["Font"])

    # 设置文字名称
    def set_font(self, font_name: str) -> None:
        self.__SETTING_DATA["Font"] = font_name

    # 文字类型
    @property
    def font_type(self) -> str:
        return str(self.__SETTING_DATA["FontType"])

    # 设置文字类型
    def set_font_type(self, font_type: str) -> None:
        self.__SETTING_DATA["FontType"] = font_type

    # 抗锯齿参数
    @property
    def antialias(self) -> bool:
        return bool(self.__SETTING_DATA["Antialias"])

    # 语言
    @property
    def language(self) -> str:
        return str(self.__SETTING_DATA["Language"])

    # 是否处于开发者模式
    @property
    def developer_mode(self) -> bool:
        return bool(self.__SETTING_DATA["DeveloperMode"])

    def set_developer_mode(self, value: bool) -> None:
        self.__SETTING_DATA["Cheat"] = bool(value)

    # 低内存模式
    @property
    def low_memory_mode(self) -> bool:
        return bool(self.__SETTING_DATA["LowMemoryMode"])

    # 作弊模式
    @property
    def cheat_mode(self) -> bool:
        return bool(self.__INTERNAL_SETTING["Cheat"])

    def set_cheat_mode(self, value: bool) -> None:
        self.__INTERNAL_SETTING["Cheat"] = bool(value)


Setting: SettingSystem = SettingSystem()
