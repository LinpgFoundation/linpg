from .setting import *
import hashlib

# 用于存放全局数据的字典
_GLOBAL_VALUES_DICT: dict = {}

# 全局数据
class GlobalValue:

    # 获取特定的全局数据
    @staticmethod
    def get(key: str) -> Any:
        return _GLOBAL_VALUES_DICT[key]

    # 设置特定的全局数据
    @staticmethod
    def set(key: str, value: Any) -> None:
        _GLOBAL_VALUES_DICT[key] = value

    # 删除特定的全局数据
    @staticmethod
    def remove(key: str) -> None:
        del _GLOBAL_VALUES_DICT[key]

    # 清空所有全局数据
    @staticmethod
    def clear() -> None:
        _GLOBAL_VALUES_DICT.clear()

    # 如果不是对应的值，则设置为对应的值，返回是否对应
    @staticmethod
    def if_get_set(key: str, valueToGet: Any, valueToSet: Any) -> bool:
        if _GLOBAL_VALUES_DICT[key] == valueToGet:
            _GLOBAL_VALUES_DICT[key] = valueToSet
            return True
        else:
            return False


# 用于存放数据库数据的字典
_DATA_BASE_DICT: dict = dict(Config.load_internal("database.json"))

# 初始化数据库
if len(path := Config.resolve_path(os.path.join("Data", "database"))) > 0:
    for key, value in dict(Config.load(path)).items():
        if key not in _DATA_BASE_DICT:
            _DATA_BASE_DICT[key] = value
        else:
            _DATA_BASE_DICT[key].update(value)

# 数据库
class DataBase:
    @staticmethod
    def get(*key: str) -> Any:
        try:
            return get_value_by_keys(_DATA_BASE_DICT, key)
        except KeyError:
            EXCEPTION.fatal('Cannot find key "{}" in the database'.format(key))


_INFO_DATA_DICT: dict = dict(Config.load_internal("info.json"))

# 版本信息管理模块
class Info:

    # 确保linpg版本
    @staticmethod
    def ensure_linpg_version(action: str, revision: int, patch: int, version: int = 3) -> bool:
        if action == "==":
            return (
                version == int(_INFO_DATA_DICT["version"])
                and revision == int(_INFO_DATA_DICT["revision"])
                and patch == int(_INFO_DATA_DICT["patch"])
            )
        elif action == ">=":
            return (
                version >= int(_INFO_DATA_DICT["version"])
                and revision >= int(_INFO_DATA_DICT["revision"])
                and patch >= int(_INFO_DATA_DICT["patch"])
            )
        elif action == "<=":
            return (
                version <= int(_INFO_DATA_DICT["version"])
                and revision <= int(_INFO_DATA_DICT["revision"])
                and patch <= int(_INFO_DATA_DICT["patch"])
            )
        else:
            EXCEPTION.fatal('Action "{}" is not supported!'.format(action))

    # 获取当前版本号
    @staticmethod
    def get_current_version() -> str:
        return "{0}.{1}.{2}".format(_INFO_DATA_DICT["version"], _INFO_DATA_DICT["revision"], _INFO_DATA_DICT["patch"])

    # 获取作者邮箱
    @staticmethod
    def get_author_email() -> str:
        return _INFO_DATA_DICT["author_email"]

    # 获取github项目地址
    @staticmethod
    def get_repository_url() -> str:
        return _INFO_DATA_DICT["repository_url"]

    # 获取项目简介
    @staticmethod
    def get_short_description() -> str:
        return _INFO_DATA_DICT["short_description"]


# 缓存文件夹路径
__CACHE_FOLDER: str = "Cache"

# 如果允许缓存，但缓存文件夹不存在
if Setting.get("AllowCache") is True and not os.path.exists(__CACHE_FOLDER):
    # 则创建缓存文件夹
    os.mkdir(__CACHE_FOLDER)

# 缓存文件目录数据
_CACHE_FILES_DATA: dict = {}
# 缓存文件目录
__CACHE_FILES_DATA_PATH: str = os.path.join(__CACHE_FOLDER, "files.{}".format(Config.get_file_type()))

# 如果允许缓存
if Setting.get("AllowCache") is True:
    # 但缓存文件目录不存在
    if not os.path.exists(__CACHE_FILES_DATA_PATH):
        # 则创建缓存文件夹
        Config.save(__CACHE_FILES_DATA_PATH, _CACHE_FILES_DATA)
    else:
        _CACHE_FILES_DATA = dict(Config.load(__CACHE_FILES_DATA_PATH))


class Cache:

    # 为一个文件夹生产md5值
    @staticmethod
    def generate_md5(path: str) -> str:
        with open(path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    # 根据md5值获取数据
    @staticmethod
    def get_data(md5: str) -> Optional[Any]:
        try:
            return _CACHE_FILES_DATA[md5]
        except KeyError:
            return None
