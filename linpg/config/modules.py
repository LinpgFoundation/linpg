import hashlib
import shutil
import sys
from .setting import *

# debug模块
class Debug:

    # 是否开启开发者模式
    __ENABLE_DEVELOPER_MODE: bool = bool(Setting.get("DeveloperMode"))
    # 是否开启作弊
    __ENABLE_CHEATING: bool = False
    # 是否展示Fps
    __SHOW_FPS: bool = False
    # 是否在windows上运行
    __RUNNING_WINDOWS: bool = sys.platform.startswith("win")

    # 开发者模式
    @classmethod
    def get_developer_mode(cls) -> bool:
        return cls.__ENABLE_DEVELOPER_MODE

    @classmethod
    def set_developer_mode(cls, value: bool) -> None:
        cls.__ENABLE_DEVELOPER_MODE = value

    # 作弊模式
    @classmethod
    def get_cheat_mode(cls) -> bool:
        return cls.__ENABLE_CHEATING

    @classmethod
    def set_cheat_mode(cls, value: bool) -> None:
        cls.__ENABLE_CHEATING = value

    # 展示Fps
    @classmethod
    def get_show_fps(cls) -> bool:
        return cls.__SHOW_FPS

    @classmethod
    def set_show_fps(cls, value: bool) -> None:
        cls.__SHOW_FPS = value

    # 是否在windows上运行
    @classmethod
    def is_running_on_windows(cls) -> bool:
        return cls.__RUNNING_WINDOWS


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
    __DATA_BASE_DICT: dict = {"Blocks": {}, "Decorations": {}, "Npc": {}, "Filters": {}}

    @classmethod
    def get(cls, *key: str) -> Any:
        return get_value_by_keys(cls.__DATA_BASE_DICT, key)

    @classmethod
    def update(cls, _value: dict) -> None:
        for key, value in _value.items():
            if key not in cls.__DATA_BASE_DICT:
                cls.__DATA_BASE_DICT[key] = value
            else:
                cls.__DATA_BASE_DICT[key].update(value)


# 版本信息管理模块
class Info:

    # 引擎主版本号
    __VERSION: Final[int] = 3
    # 引擎次更新版本号
    __REVISION: Final[int] = 4
    # 引擎补丁版本
    __PATCH: Final[int] = 0

    # 确保linpg版本
    @classmethod
    def ensure_linpg_version(cls, action: str, revision: int, patch: int, version: int = 3) -> bool:
        if action == "==":
            return version == cls.__VERSION and revision == cls.__REVISION and patch == cls.__PATCH
        elif action == ">=":
            return version >= cls.__VERSION and revision >= cls.__REVISION and patch >= cls.__PATCH
        elif action == "<=":
            return version <= cls.__VERSION and revision <= cls.__REVISION and patch <= cls.__PATCH
        else:
            EXCEPTION.fatal('Action "{}" is not supported!'.format(action))

    # 获取当前版本号
    @classmethod
    def get_current_version(cls) -> str:
        return "{0}.{1}.{2}".format(cls.__VERSION, cls.__REVISION, cls.__PATCH)

    # 获取github项目地址
    @classmethod
    def get_repository_url(cls) -> str:
        return "https://github.com/Tigeia-Workshop/linpg"


class Cache:

    # 缓存文件夹路径
    __CACHE_FOLDER: Final[str] = Specification.get_directory("cache")
    # 缓存文件清单路径
    __CACHE_FILES_DATA_PATH: Final[str] = os.path.join(__CACHE_FOLDER, "files.{}".format(Config.get_file_type()))
    # 如果缓存文件目录存在, 则加载数据， 否则初始化一个新的空字典
    __CACHE_FILES_DATA: dict = Config.load_file(__CACHE_FILES_DATA_PATH) if os.path.exists(__CACHE_FILES_DATA_PATH) else {}

    # 获取缓存文件夹路径
    @classmethod
    def get_directory(cls) -> str:
        # 如果缓存文件夹不存在， 则创建缓存文件夹
        if not os.path.exists(cls.__CACHE_FOLDER):
            os.mkdir(cls.__CACHE_FOLDER)
        # 返回文件夹路径
        return cls.__CACHE_FOLDER

    @staticmethod
    def delete_file_if_exist(path: str) -> None:
        if os.path.exists(path):
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)

    # 为一个文件夹生产md5值
    @staticmethod
    def __generate_md5(path: str) -> str:
        if os.path.exists(path):
            with open(path, "rb") as f:
                return hashlib.md5(f.read()).hexdigest()
        else:
            EXCEPTION.fatal("Cannot generate md5 for a file that does not exist in path: {}".format(path))

    # 新建一个对比关系
    @classmethod
    def new(cls, key: str, source_file_path: str, target_file_path: str) -> None:
        if key not in cls.__CACHE_FILES_DATA:
            cls.__CACHE_FILES_DATA[key] = {
                "source": {"path": source_file_path, "md5": cls.__generate_md5(source_file_path)},
                "target": {"path": target_file_path, "md5": cls.__generate_md5(target_file_path)},
                "version": Info.get_current_version(),
            }
            # 保存缓存文件的相关数据
            Config.save(cls.__CACHE_FILES_DATA_PATH, cls.__CACHE_FILES_DATA)
        else:
            EXCEPTION.fatal('The key named "{}" already exists. Please create a new unique one!'.format(key))

    # 移除
    @classmethod
    def remove(cls, key: str) -> None:
        cls.delete_file_if_exist(cls.__CACHE_FILES_DATA[key]["target"]["path"])
        del cls.__CACHE_FILES_DATA[key]
        Config.save(cls.__CACHE_FILES_DATA_PATH, cls.__CACHE_FILES_DATA)

    @classmethod
    def get_cache_path(cls, key: str) -> str:
        return str(cls.__CACHE_FILES_DATA[key]["target"]["path"])

    # 对比数据
    @classmethod
    def match(cls, key: str, source_file_path: str) -> bool:
        if key in cls.__CACHE_FILES_DATA:
            if (
                Info.get_current_version() == cls.__CACHE_FILES_DATA[key]["version"]
                and os.path.exists(source_file_path)
                and source_file_path == cls.__CACHE_FILES_DATA[key]["source"]["path"]
                and cls.__generate_md5(source_file_path) == cls.__CACHE_FILES_DATA[key]["source"]["md5"]
                and os.path.exists(cls.__CACHE_FILES_DATA[key]["target"]["path"])
                and cls.__generate_md5(cls.__CACHE_FILES_DATA[key]["target"]["path"])
                == cls.__CACHE_FILES_DATA[key]["target"]["md5"]
            ):
                return True
            else:
                cls.remove(key)
        return False
