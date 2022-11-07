import hashlib
import re
import shutil
from typing import Callable

from .setting import *


# debug模块
class Debug:

    # 是否开启开发者模式
    __ENABLE_DEVELOPER_MODE: bool = False
    # 是否开启作弊
    __ENABLE_CHEATING: bool = False
    # 是否展示Fps
    __SHOW_FPS: bool = False

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


# 版本信息管理模块
class Info:

    # 引擎主版本号
    __VERSION: Final[int] = 3
    # 引擎次更新版本号
    __REVISION: Final[int] = 5
    # 引擎补丁版本
    __PATCH: Final[int] = 1

    # 确保linpg版本
    @classmethod
    def ensure_linpg_version(cls, action: str, revision: int, patch: int, version: int = 3) -> bool:
        if action == "==":
            return cls.__VERSION == version and cls.__REVISION == revision and cls.__PATCH == patch
        elif action == ">=":
            return cls.__VERSION >= version and cls.__REVISION >= revision and cls.__PATCH >= patch
        elif action == "<=":
            return cls.__VERSION <= version and cls.__REVISION <= revision and cls.__PATCH <= patch
        else:
            EXCEPTION.fatal('Action "{}" is not supported!'.format(action))

    # 获取当前版本号
    @classmethod
    def get_current_version(cls) -> str:
        return "{0}.{1}.{2}".format(cls.__VERSION, cls.__REVISION, cls.__PATCH)

    # 获取github项目地址
    @classmethod
    def get_repository_url(cls) -> str:
        return "https://github.com/LinpgFoundation/linpg"


class Files:

    # 一个简单的 natural sort 实现
    @staticmethod
    def natural_sort(_files: list[str]) -> list[str]:
        convert: Callable[[str], int | str] = lambda text: int(text) if text.isdigit() else text.lower()
        _key: Callable[[str], list[int | str]] = lambda key: [convert(c) for c in re.split("([0-9]+)", key)]
        return sorted(sorted(_files), key=_key)

    # 删除特定patten的文件夹
    @classmethod
    def search_and_remove_folder(cls, folder_to_search: str, stuff_to_remove: str) -> None:
        # 确保folder_to_search是一个目录
        if not os.path.isdir(folder_to_search):
            raise NotADirectoryError("You can only search a folder!")
        # 移除当前文件夹符合条件的目录/文件
        for path in glob(os.path.join(folder_to_search, "*")):
            if path.endswith(stuff_to_remove):
                shutil.rmtree(path)
            elif os.path.isdir(path):
                cls.search_and_remove_folder(path, stuff_to_remove)

    # 根据地址删除文件夹
    @staticmethod
    def delete_if_exist(path: str) -> None:
        if os.path.exists(path):
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)

    # 为一个文件生产md5值
    @staticmethod
    def generate_md5(path: str) -> str:
        if os.path.exists(path):
            with open(path, "rb") as f:
                return hashlib.md5(f.read()).hexdigest()
        else:
            EXCEPTION.fatal("Cannot generate md5 for a file that does not exist in path: {}".format(path))


class Cache:

    # 缓存文件夹路径
    __CACHE_FOLDER: Final[str] = Specification.get_directory("cache")
    # 缓存文件清单路径
    __CACHE_FILES_DATA_PATH: Final[str] = os.path.join(__CACHE_FOLDER, "files.{}".format(Config.get_file_type()))
    # 如果缓存文件目录存在, 则加载数据， 否则初始化一个新的空字典
    __CACHE_FILES_DATA: Final[dict] = Config.load_file(__CACHE_FILES_DATA_PATH) if os.path.exists(__CACHE_FILES_DATA_PATH) else {}

    # 获取缓存文件夹路径
    @classmethod
    def get_directory(cls) -> str:
        # 如果缓存文件夹不存在， 则创建缓存文件夹
        if not os.path.exists(cls.__CACHE_FOLDER):
            os.mkdir(cls.__CACHE_FOLDER)
        # 返回文件夹路径
        return cls.__CACHE_FOLDER

    # 新建一个对比关系
    @classmethod
    def new(cls, _key: str, source_file_path: str, target_file_path: str) -> None:
        if _key not in cls.__CACHE_FILES_DATA:
            cls.__CACHE_FILES_DATA[_key] = {
                "source": {"path": source_file_path, "md5": Files.generate_md5(source_file_path)},
                "target": {"path": target_file_path, "md5": Files.generate_md5(target_file_path)},
                "version": Info.get_current_version(),
            }
            # 保存缓存文件的相关数据
            Config.save(cls.__CACHE_FILES_DATA_PATH, cls.__CACHE_FILES_DATA)
        else:
            EXCEPTION.fatal('The key named "{}" already exists. Please create a new unique one!'.format(_key))

    # 移除
    @classmethod
    def remove(cls, _key: str) -> None:
        Files.delete_if_exist(cls.__CACHE_FILES_DATA[_key]["target"]["path"])
        del cls.__CACHE_FILES_DATA[_key]
        Config.save(cls.__CACHE_FILES_DATA_PATH, cls.__CACHE_FILES_DATA)

    @classmethod
    def get_cache_path(cls, _key: str) -> str:
        return str(cls.__CACHE_FILES_DATA[_key]["target"]["path"])

    # 对比数据
    @classmethod
    def match(cls, _key: str, source_file_path: str) -> bool:
        if _key in cls.__CACHE_FILES_DATA:
            if (
                Info.get_current_version() == cls.__CACHE_FILES_DATA[_key]["version"]
                and os.path.exists(source_file_path)
                and source_file_path == cls.__CACHE_FILES_DATA[_key]["source"]["path"]
                and Files.generate_md5(source_file_path) == cls.__CACHE_FILES_DATA[_key]["source"]["md5"]
                and os.path.exists(cls.__CACHE_FILES_DATA[_key]["target"]["path"])
                and Files.generate_md5(cls.__CACHE_FILES_DATA[_key]["target"]["path"]) == cls.__CACHE_FILES_DATA[_key]["target"]["md5"]
            ):
                return True
            else:
                cls.remove(_key)
        return False
