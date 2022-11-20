import json
from functools import reduce
from glob import glob
from operator import getitem
from typing import Any, Final, Optional, Sequence

from ..exception import EXCEPTION, os

# 尝试导入yaml库
_YAML_INITIALIZED: bool = False
try:
    import yaml

    _YAML_INITIALIZED = True
except Exception:
    pass


# 根据keys查找值，最后返回一个复制的对象
def get_value_by_keys(_dict: dict, _keys: Sequence, _default: Optional[Any] = None) -> Any:
    try:
        return reduce(getitem, _keys, _dict)
    except KeyError:
        if _default is None:
            EXCEPTION.fatal('Getting "KeyError" while trying to get keys {} from dict!'.format(_keys))
        return _default


# 根据keys查找被设置对应对应对象为指定值
def set_value_by_keys(_dict: dict, _keys: Sequence, value: object, assumeKeyExists: bool = True) -> None:
    if len(_keys) < 1:
        EXCEPTION.fatal("Keys' length has to be greater than 0.")
    pointer: dict = _dict
    last_key_index: int = len(_keys) - 1
    for index in range(last_key_index):
        _item: Optional[object] = pointer.get(_keys[index])
        if isinstance(_item, dict):
            pointer = _item
        elif _item is None:
            if assumeKeyExists is True:
                EXCEPTION.fatal('Getting "KeyError" while trying to set keys {} to dict!'.format(_keys))
            pointer[_keys[index]] = {}
            pointer = pointer[_keys[index]]
        else:
            EXCEPTION.fatal("Getting not dict object {0} while trying to set keys {1} to dict!".format(_item, _keys))
    pointer[_keys[last_key_index]] = value


# 配置文件管理模块
class Config:

    # 支持的配置文件后缀
    __EXTENSIONS_SUPPORTED: Final[tuple[str, ...]] = (".yml", ".yaml", ".json")

    # 获取默认配置文件类型
    @staticmethod
    def get_file_type() -> str:
        return str(Specification.get("ConfigFileType"))

    # 加载配置文件
    @staticmethod
    def __load_file(path: str) -> dict:
        # 如果路径不存在
        if not os.path.exists(path):
            EXCEPTION.fatal("Cannot find file on path: {}".format(path))
        else:
            # 按照类型加载配置文件
            with open(path, "r", encoding="utf-8") as f:
                # 使用yaml模块加载配置文件
                if path.endswith(".yaml") or path.endswith(".yml"):
                    if _YAML_INITIALIZED is True:
                        _result: Any = yaml.load(f.read(), Loader=yaml.Loader)
                        return dict(_result) if _result is not None else {}
                    else:
                        EXCEPTION.fatal("You cannot load YAML file because yaml is not imported successfully.")
                # 使用json模块加载配置文件
                elif path.endswith(".json") or path.endswith(".linpg.meta"):
                    return dict(json.load(f))
                else:
                    EXCEPTION.fatal("Linpg can only load json and yaml (when pyyaml is installed).")

    # 加载配置文件
    @classmethod
    def load_file(cls, path: str) -> dict:
        return cls.__load_file(path)

    # 尝试加载可能不存在的配置文件，如果不存在则返回一个空字典
    @classmethod
    def try_load_file_if_exists(cls, _path: str, _default: dict = {}) -> dict:
        return cls.__load_file(_path) if os.path.exists(_path) else _default

    # 加载配置文件，并根据key（s）返回对应的数据
    @classmethod
    def load(cls, path: str, *key: str) -> Any:
        return get_value_by_keys(cls.__load_file(path), key)

    # 加载内部配置文件
    @classmethod
    def load_internal_file(cls, path: str) -> dict:
        return cls.__load_file(os.path.join(os.path.dirname(__file__), path))

    # 配置文件保存
    @staticmethod
    def save(path: str, data: dict) -> None:
        # 确保用于储存的文件夹存在
        dir_path: str = os.path.dirname(path)
        if len(dir_path) > 0 and not os.path.exists(dir_path):
            os.makedirs(dir_path)
        # 保存文件
        with open(path, "w", encoding="utf-8") as f:
            if path.endswith(".yaml") or path.endswith(".yml"):
                if _YAML_INITIALIZED is True:
                    yaml.dump(data, f, allow_unicode=True)
                else:
                    EXCEPTION.fatal("You cannot save .yaml file because yaml is not imported successfully. Maybe try to reinstall PyYaml and try again.")
            elif path.endswith(".json") or path.endswith(".linpg.meta"):
                json.dump(data, f, indent=4, ensure_ascii=False, sort_keys=True)
            else:
                EXCEPTION.fatal("Linpg cannot save this kind of config, and can only save json and yaml (if pyyaml is installed).")

    # 整理配置文件（读取了再存）
    @classmethod
    def organize(cls, pathname: str) -> None:
        for configFilePath in glob(pathname):
            cls.save(configFilePath, cls.load_file(configFilePath))

    # 整理内部配置文件
    @classmethod
    def organize_internal(cls) -> None:
        cls.organize(os.path.join(os.path.dirname(__file__), "*.json"))

    # 解决路径冲突
    @classmethod
    def resolve_path(cls, file_location: str) -> str:
        path: str
        for fileType in cls.__EXTENSIONS_SUPPORTED:
            if os.path.exists(path := file_location + fileType):
                return path
        return ""

    # 解决路径冲突并加载
    @classmethod
    def resolve_path_and_load_file(cls, file_location: str) -> dict:
        path: str = cls.resolve_path(file_location)
        return cls.load_file(path) if len(path) > 0 else {}


# 使用引擎的开发者可以自定义的参数
class Specification:

    __SPECIFICATIONS: Final[dict] = Config.load_internal_file("specifications.json")
    # 尝试加载项目自定义的参数
    __SPECIFICATIONS.update(Config.resolve_path_and_load_file(os.path.join("Data", "specifications")))

    @classmethod
    def get(cls, *key: str) -> Any:
        return get_value_by_keys(cls.__SPECIFICATIONS, key)

    @classmethod
    def get_directory(cls, category: str, *_sub: str) -> str:
        return str(os.path.join(*cls.__SPECIFICATIONS["Directory"][category], *_sub))
