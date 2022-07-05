from .base import *

# 设置参数管理系统
class Setting:

    # 储存设置配置文件的数据
    __SETTING_DATA: Final[dict] = {}
    # 当前配置文件保存路径的参数
    __SETTING_FILE_NAME: Final[str] = Specification.get_directory("setting", "setting." + Config.get_file_type())

    # 重新加载设置数据
    @classmethod
    def reload(cls) -> None:
        # 加载内部默认的设置配置文件
        cls.__SETTING_DATA.clear()
        cls.__SETTING_DATA.update(Template.get("setting"))
        # 如果自定义的设置配置文件存在，则加载
        if os.path.exists(cls.__SETTING_FILE_NAME):
            cls.__SETTING_DATA.update(Config.load_file(cls.__SETTING_FILE_NAME))
        # 如果不存在自定义的设置配置文件，则应该创建一个
        else:
            # 导入local,查看默认语言
            import locale

            # 如果是中文
            if locale.getdefaultlocale()[0] == "zh_CN":
                cls.__SETTING_DATA["Language"] = "SimplifiedChinese"
            elif locale.getdefaultlocale()[0] == "zh_TW":
                cls.__SETTING_DATA["Language"] = "TraditionalChinese"
            # 保存设置
            cls.save()

    # 保存设置数据
    @classmethod
    def save(cls) -> None:
        Config.save(cls.__SETTING_FILE_NAME, cls.__SETTING_DATA)

    # 获取设置数据
    @classmethod
    def get(cls, *key: str) -> Any:
        return get_value_by_keys(cls.__SETTING_DATA, key)

    # 在不确定的情况下尝试获取设置数据
    @classmethod
    def try_get(cls, *key: str) -> Any:
        return get_value_by_keys(cls.__SETTING_DATA, key, False)

    # 修改设置数据
    @classmethod
    def set(cls, *key: str, value: object) -> None:
        set_value_by_keys(cls.__SETTING_DATA, key, value)

    """其他常用的重要参数"""
    # 文字名称
    @classmethod
    def get_font(cls) -> str:
        return str(cls.__SETTING_DATA["Font"])

    # 设置文字名称
    @classmethod
    def set_font(cls, font_name: str) -> None:
        cls.__SETTING_DATA["Font"] = font_name

    # 文字类型
    @classmethod
    def get_font_type(cls) -> str:
        return str(cls.__SETTING_DATA["FontType"])

    # 设置文字类型
    @classmethod
    def set_font_type(cls, font_type: str) -> None:
        cls.__SETTING_DATA["FontType"] = font_type

    # 抗锯齿参数
    @classmethod
    def get_antialias(cls) -> bool:
        return bool(cls.__SETTING_DATA["Antialias"])

    # 语言
    @classmethod
    def get_language(cls) -> str:
        return str(cls.__SETTING_DATA["Language"])

    # 低内存模式
    @classmethod
    def get_low_memory_mode(cls) -> bool:
        return bool(cls.__SETTING_DATA["LowMemoryMode"])


# 初始化
Setting.reload()
