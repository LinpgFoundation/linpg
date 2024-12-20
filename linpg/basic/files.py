import hashlib
import os
import re
import shutil
from glob import glob
from typing import Callable, Final

from ..exception import Exceptions
from .configurations import Configurations
from .specifications import Specifications
from .version import Version

# the algorithm that will be used for hashing
_HASHING_ALGORITHM: Final[str] = "sha3_256"


class Files:
    # 一个简单的 natural sort 实现
    @staticmethod
    def natural_sort(files: list[str]) -> list[str]:
        convert: Callable[[str], int | str] = lambda text: int(text) if text.isdigit() else text.lower()
        _key: Callable[[str], list[int | str]] = lambda key: [convert(c) for c in re.split("([0-9]+)", key)]
        return sorted(sorted(files), key=_key)

    # 删除特定patten的文件夹
    @classmethod
    def search_and_delete_dir(cls, folder_to_search: str, stuff_to_remove: str) -> None:
        # 确保folder_to_search是一个目录
        if not os.path.isdir(folder_to_search):
            raise NotADirectoryError("You can only search a folder!")
        # 移除当前文件夹符合条件的目录/文件
        for path in glob(os.path.join(folder_to_search, "*")):
            if path.endswith(stuff_to_remove):
                shutil.rmtree(path)
            elif os.path.isdir(path):
                cls.search_and_delete_dir(path, stuff_to_remove)

    # 根据地址删除文件夹
    @staticmethod
    def delete(path: str) -> None:
        if os.path.exists(path):
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)

    # 为一个文件生成hash值
    @staticmethod
    def hash(path: str) -> str:
        if os.path.exists(path):
            with open(path, "rb") as f:
                return hashlib.new(_HASHING_ALGORITHM, f.read()).hexdigest()
        else:
            Exceptions.fatal(f"Cannot generate {_HASHING_ALGORITHM} for a file that does not exist in path: {path}")


class Cache:
    # 缓存文件夹路径
    __CACHE_FOLDER: Final[str] = Specifications.get_directory("cache")
    # 缓存文件清单路径
    __CACHE_FILES_DATA_PATH: Final[str] = os.path.join(__CACHE_FOLDER, "files.json")
    # 如果缓存文件目录存在, 则加载数据， 否则初始化一个新的空字典
    __CACHE_FILES_DATA: Final[dict[str, dict]] = Configurations.try_load_file(__CACHE_FILES_DATA_PATH)

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
                "source": {"path": source_file_path, _HASHING_ALGORITHM: Files.hash(source_file_path)},
                "target": {"path": target_file_path, _HASHING_ALGORITHM: Files.hash(target_file_path)},
                "version": Version.get_current_version(),
            }
            # 保存缓存文件的相关数据
            Configurations.save(cls.__CACHE_FILES_DATA_PATH, cls.__CACHE_FILES_DATA)
        else:
            Exceptions.fatal(f'The key named "{_key}" already exists. Please create a new unique one!')

    # 移除
    @classmethod
    def remove(cls, _key: str) -> None:
        Files.delete(cls.get_cache_path(_key))
        del cls.__CACHE_FILES_DATA[_key]
        Configurations.save(cls.__CACHE_FILES_DATA_PATH, cls.__CACHE_FILES_DATA)

    @classmethod
    def get_cache_path(cls, _key: str) -> str:
        return str(cls.__CACHE_FILES_DATA[_key]["target"]["path"])

    # 对比数据
    @classmethod
    def match(cls, _key: str, source_file_path: str) -> bool:
        cache_info: dict | None = cls.__CACHE_FILES_DATA.get(_key)
        if cache_info is not None:
            if (
                Version.get_current_version() == cache_info["version"]
                and os.path.exists(source_file_path)
                and source_file_path == cache_info["source"]["path"]
                and Files.hash(source_file_path) == cache_info["source"].get(_HASHING_ALGORITHM)
                and os.path.exists(cache_info["target"]["path"])
                and Files.hash(cache_info["target"]["path"]) == cache_info["target"].get(_HASHING_ALGORITHM)
            ):
                return True
            else:
                cls.remove(_key)
        return False
