from .setting import *

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
