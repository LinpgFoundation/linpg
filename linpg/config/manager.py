import hashlib
from .setting import *

# 全局数据
class GlobalValue:

    # 用于存放全局数据的字典
    __GLOBAL_VALUES_DICT: dict = {}
    # 读取本地的全局数据
    if os.path.exists(_path := os.path.join("save", "global.yaml")):
        __GLOBAL_VALUES_DICT.update(Config.load_file(_path))

    # 获取特定的全局数据
    @classmethod
    def get(cls, key: str) -> object:
        return cls.__GLOBAL_VALUES_DICT[key]

    # 设置特定的全局数据
    @classmethod
    def set(cls, key: str, value: object) -> None:
        cls.__GLOBAL_VALUES_DICT[key] = value

    # 删除特定的全局数据
    @classmethod
    def remove(cls, key: str) -> None:
        del cls.__GLOBAL_VALUES_DICT[key]

    # 清空所有全局数据
    @classmethod
    def clear(cls) -> None:
        cls.__GLOBAL_VALUES_DICT.clear()

    # 如果不是对应的值，则设置为对应的值，返回是否对应
    @classmethod
    def if_get_set(cls, key: str, valueToGet: object, valueToSet: object) -> bool:
        if cls.__GLOBAL_VALUES_DICT[key] == valueToGet:
            cls.__GLOBAL_VALUES_DICT[key] = valueToSet
            return True
        else:
            return False


# 数据库
class DataBase:

    # 用于存放数据库数据的字典
    __DATA_BASE_DICT: dict = Config.load_internal_file("database.json")

    # 初始化数据库
    if len(_path := Config.resolve_path(os.path.join("Data", "database"))) > 0:
        for key, value in Config.load_file(_path).items():
            if key not in __DATA_BASE_DICT:
                __DATA_BASE_DICT[key] = value
            else:
                __DATA_BASE_DICT[key].update(value)

    @classmethod
    def get(cls, *key: str) -> Any:
        try:
            return get_value_by_keys(cls.__DATA_BASE_DICT, key)
        except KeyError:
            EXCEPTION.fatal('Cannot find key "{}" in the database'.format(key))


# 版本信息管理模块
class Info:

    __INFO_DATA_DICT: dict = Config.load_internal_file("info.json")

    # 确保linpg版本
    @classmethod
    def ensure_linpg_version(cls, action: str, revision: int, patch: int, version: int = 3) -> bool:
        if action == "==":
            return (
                version == int(cls.__INFO_DATA_DICT["version"])
                and revision == int(cls.__INFO_DATA_DICT["revision"])
                and patch == int(cls.__INFO_DATA_DICT["patch"])
            )
        elif action == ">=":
            return (
                version >= int(cls.__INFO_DATA_DICT["version"])
                and revision >= int(cls.__INFO_DATA_DICT["revision"])
                and patch >= int(cls.__INFO_DATA_DICT["patch"])
            )
        elif action == "<=":
            return (
                version <= int(cls.__INFO_DATA_DICT["version"])
                and revision <= int(cls.__INFO_DATA_DICT["revision"])
                and patch <= int(cls.__INFO_DATA_DICT["patch"])
            )
        else:
            EXCEPTION.fatal('Action "{}" is not supported!'.format(action))

    # 获取当前版本号
    @classmethod
    def get_current_version(cls) -> str:
        return "{0}.{1}.{2}".format(
            cls.__INFO_DATA_DICT["version"], cls.__INFO_DATA_DICT["revision"], cls.__INFO_DATA_DICT["patch"]
        )

    # 获取作者邮箱
    @classmethod
    def get_author_email(cls) -> str:
        return str(cls.__INFO_DATA_DICT["author_email"])

    # 获取github项目地址
    @classmethod
    def get_repository_url(cls) -> str:
        return str(cls.__INFO_DATA_DICT["repository_url"])

    # 获取项目简介
    @classmethod
    def get_short_description(cls) -> str:
        return str(cls.__INFO_DATA_DICT["short_description"])


class Cache:

    # 缓存文件夹路径
    __CACHE_FOLDER: str = "Cache"

    # 如果允许缓存，但缓存文件夹不存在
    if Setting.get("AllowCache") is True and not os.path.exists(__CACHE_FOLDER):
        # 则创建缓存文件夹
        os.mkdir(__CACHE_FOLDER)

    # 缓存文件目录数据
    __CACHE_FILES_DATA: dict = {}
    # 缓存文件目录
    __CACHE_FILES_DATA_PATH: str = os.path.join(__CACHE_FOLDER, "files.{}".format(Config.get_file_type()))

    # 如果允许缓存
    if Setting.allow_cache is True:
        # 但缓存文件目录不存在
        if not os.path.exists(__CACHE_FILES_DATA_PATH):
            # 则创建缓存文件夹
            Config.save(__CACHE_FILES_DATA_PATH, __CACHE_FILES_DATA)
        else:
            __CACHE_FILES_DATA = Config.load_file(__CACHE_FILES_DATA_PATH)

    # 为一个文件夹生产md5值
    @staticmethod
    def generate_md5(path: str) -> str:
        with open(path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    # 根据md5值获取数据
    @classmethod
    def get_data(cls, md5: str) -> object:
        try:
            return cls.__CACHE_FILES_DATA[md5]
        except KeyError:
            return None
