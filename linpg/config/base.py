from __future__ import annotations
import json
from typing import Any
from copy import deepcopy
from glob import glob
from ..exception import *

# 尝试导入yaml库
_YAML_INITIALIZED: bool = False
try:
    import yaml

    _YAML_INITIALIZED = True
except Exception:
    pass

# 根据keys查找值，最后返回一个复制的对象
def get_value_by_keys(dict_to_check: dict, keys: tuple, warning: bool = True) -> Any:
    pointer = dict_to_check
    for key in keys:
        try:
            pointer = pointer[key]
        except KeyError:
            if warning is True:
                EXCEPTION.warn(
                    'Getting "KeyError" while trying to get {}!\nPlease check your code or report this bug to the developer!'.format(
                        key
                    )
                )
            return key
    return deepcopy(pointer)


# 根据keys查找被设置对应对应对象为指定值
def set_value_by_keys(dict_to_check: dict, keys: tuple, value: Any, warning: bool = True) -> None:
    pointer = dict_to_check
    key_range: int = len(keys)
    last_key_index: int = key_range - 1
    index: int = 0
    for index in range(key_range):
        try:
            if index < last_key_index:
                pointer = pointer[keys[index]]
            else:
                pointer[keys[index]] = value
        except KeyError:
            if warning is True:
                EXCEPTION.warn(
                    'Getting "KeyError" while trying to get {}!\nPlease check your code or report this bug to the developer!'.format(
                        keys[index]
                    )
                )
            return keys[index]


# 配置文件管理模块
class Config:

    # 获取默认配置文件类型
    @staticmethod
    def get_file_type() -> str:
        return str(_SPECIFICATIONS["ConfigFileType"])

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
                        return yaml.load(f.read(), Loader=yaml.Loader)
                    else:
                        EXCEPTION.fatal("You cannot load YAML file because yaml is not imported successfully.")
                # 使用json模块加载配置文件
                elif path.endswith(".json"):
                    return json.load(f)
                else:
                    EXCEPTION.fatal("Linpg can only load json and yaml (when pyyaml is installed).")

    # 加载配置文件
    @staticmethod
    def load_file(path: str) -> dict:
        return Config.__load_file(path)

    # 加载配置文件，并根据key（s）返回对应的数据
    @staticmethod
    def load(path: str, *key: str) -> Any:
        return get_value_by_keys(Config.__load_file(path), key)

    # 加载内部配置文件
    @staticmethod
    def load_internal_file(path: str) -> dict:
        return Config.__load_file(os.path.join(os.path.dirname(__file__), path))

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
                    EXCEPTION.fatal("You cannot save .yaml file because yaml is not imported successfully.")
            elif path.endswith(".json"):
                json.dump(data, f, indent=4, ensure_ascii=False, sort_keys=True)
            else:
                EXCEPTION.fatal(
                    "Linpg cannot save this kind of config, and can only save json and yaml (if pyyaml is installed)."
                )

    # 整理配置文件（读取了再存）
    @staticmethod
    def organize(pathname: str) -> None:
        for configFilePath in glob(pathname):
            Config.save(configFilePath, Config.load_file(configFilePath))

    # 整理内部配置文件
    @staticmethod
    def organize_internal() -> None:
        Config.organize(os.path.join(os.path.dirname(__file__), "*.json"))

    # 优化中文文档
    @staticmethod
    def optimize_cn_content(filePath: str) -> None:
        # 读取原文件的数据
        with open(filePath, "r", encoding="utf-8") as f:
            file_lines = f.readlines()
        # 优化字符串
        for i in range(len(file_lines)):
            # 如果字符串不为空
            if len(file_lines[i]) > 1:
                # 替换字符
                file_lines[i] = (
                    file_lines[i]
                    .replace("。。。", "... ")
                    .replace("。", ". ")
                    .replace("？？：", "??: ")
                    .replace("？？", "?? ")
                    .replace("？", "? ")
                    .replace("！！", "!! ")
                    .replace("！", "! ")
                    .replace("：", ": ")
                    .replace("，", ", ")
                    .replace("“", '"')
                    .replace("”", '"')
                    .replace("‘", "'")
                    .replace("’", "'")
                    .replace("（", " (")
                    .replace("）", ") ")
                    .replace("  ", " ")
                )
                # 移除末尾的空格
                try:
                    while file_lines[i][-2] == " ":
                        file_lines[i] = file_lines[i][:-2] + "\n"
                except Exception:
                    pass
        # 删除原始文件
        os.remove(filePath)
        # 创建并写入新数据
        with open(filePath, "w", encoding="utf-8") as f:
            f.writelines(file_lines)

    # 优化文件夹中特定文件的中文字符串
    @staticmethod
    def optimize_cn_content_in_folder(pathname: str) -> None:
        for configFilePath in glob(pathname):
            Config.optimize_cn_content(configFilePath)

    # 解决路径冲突
    @staticmethod
    def resolve_path(file_location: str) -> str:
        path: str
        if (
            os.path.exists(path := file_location + ".yml")
            or os.path.exists(path := file_location + ".yaml")
            or os.path.exists(path := file_location + ".json")
        ):
            return path
        else:
            return ""


_SPECIFICATIONS: dict = Config.load_internal_file("specifications.json")

# 使用引擎开发游戏的用户可以自定义的参数
class Specification:
    @staticmethod
    def get(key: str) -> Any:
        return _SPECIFICATIONS[key]


_TEMPLATE: dict = Config.load_internal_file("template.json")

# 引擎部分生产的配置文件的模板
class Template:
    @staticmethod
    def get(key: str) -> dict:
        return dict(_TEMPLATE[key])
