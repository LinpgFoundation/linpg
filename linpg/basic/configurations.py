import json
import os
from typing import Any

from ..exception import Exceptions
from .getter import TypeSafeGetter


# 配置文件管理模块
class Configurations:
    # 加载配置文件
    @staticmethod
    def __load_file(path: str) -> dict:
        # 如果路径不存在
        if not os.path.exists(path):
            Exceptions.fatal(f"Cannot find file on path: {path}")
        else:
            # 使用json模块加载配置文件
            with open(path, "r", encoding="utf-8") as f:
                return dict(json.load(f))

    # 加载配置文件
    @classmethod
    def load_file(cls, path: str) -> dict[str, Any]:
        return cls.__load_file(path)

    # 尝试加载可能不存在的配置文件，如果不存在则返回一个空字典
    @classmethod
    def try_load_file(cls, path: str, _default: dict = {}) -> dict[str, Any]:
        return cls.__load_file(path) if os.path.exists(path) else _default

    # 加载配置文件，并根据key（s）返回对应的数据
    @classmethod
    def load(cls, path: str, *key: str) -> Any:
        return TypeSafeGetter.get_by_keys(cls.__load_file(path), key)

    # 配置文件保存
    @staticmethod
    def save(path: str, data: dict) -> None:
        # 确保用于储存的文件夹存在
        dir_path: str = os.path.dirname(path)
        if len(dir_path) > 0 and not os.path.exists(dir_path):
            os.makedirs(dir_path)
        # 保存文件
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False, sort_keys=True)
