# cython: language_level=3
from __future__ import annotations
import json
import os
from copy import deepcopy
from datetime import datetime
from glob import glob
# 尝试导入yaml库
_YAML_INITIALIZED:bool = False
try:
    import yaml
    _YAML_INITIALIZED = True
except Exception:
    pass

#错误报告存储的路径
_CRASH_REPORTS_PATH:str = "crash_reports"

# Linpg本身错误类
class Error(Exception):
    def __init__(self, message:str):
        super().__init__(message)

# 抛出引擎内的异常
def throw_exception(exception_type:str, info:str) -> None:
    exception_type_lower:str = exception_type.lower()
    if exception_type_lower == "error":
        # 生成错误报告
        if not os.path.exists(_CRASH_REPORTS_PATH): os.mkdir(_CRASH_REPORTS_PATH)
        with open(os.path.join(_CRASH_REPORTS_PATH, "crash_{}.txt".format(datetime.now().strftime("%m-%d-%Y_%H-%M-%S"))), "w", encoding='utf-8') as f:
            f.write("Error Message From Linpg: {}".format(info))
        # 打印出错误
        raise Error('LinpgEngine-Error: {}'.format(info))
    elif exception_type_lower == "warning":
        # 生成错误报告
        if not os.path.exists(_CRASH_REPORTS_PATH): os.mkdir(_CRASH_REPORTS_PATH)
        with open(os.path.join(_CRASH_REPORTS_PATH,"crash_{}.txt".format(datetime.now().strftime("%m-%d-%Y_%H-%M-%S"))), "w", encoding='utf-8') as f:
            f.write("Warning Message From Linpg: {}".format(info))
        # 打印出警告
        print("LinpgEngine-Warning: {}".format(info))
    elif exception_type_lower == "info":
        print('LinpgEngine-Info: {}'.format(info))
    else:
        throw_exception("error","Hey, the exception_type '{}' is not acceptable!".format(exception_type))

#根据keys查找值，最后返回一个复制的对象
def get_value_by_keys(dict_to_check:dict, keys:tuple, warning:bool=True) -> any:
    pointer = dict_to_check
    for key in keys:
        try:
            pointer = pointer[key]
        except KeyError:
            if warning is True: throw_exception(
                "warning",
                'Getting "KeyError" while trying to get {}!\nPlease check your code or report this bug to the developer!'
                .format(key)
                )
            return key
    return deepcopy(pointer)

# 配置文件加载
def load_config(path:str, *keys:str) -> any:
    # 检测配置文件是否存在
    if not os.path.exists(path): throw_exception("error","Cannot find file on path: {}".format(path))
    # 按照类型加载配置文件
    if path.endswith(".yaml"):
        if _YAML_INITIALIZED is True:
            try:
                # 尝试使用默认模式加载yaml配置文件
                with open(path, "r", encoding='utf-8') as f: Data = yaml.load(f.read(), Loader=yaml.FullLoader)
            except yaml.constructor.ConstructorError:
                throw_exception("warning","Encounter a fatal error while loading the yaml file in path:\n'{}'\n\
                    One possible reason is that at least one numpy array exists inside the yaml file.\n\
                    The program will try to load the data using yaml.UnsafeLoader.".format(path))
                # 使用安全模式加载yaml配置文件
                with open(path, "r", encoding='utf-8') as f: Data = yaml.load(f.read(), Loader=yaml.UnsafeLoader)
        else:
            throw_exception("error","You cannot load .yaml file because yaml is not imported successfully.")
    elif path.endswith(".json"):
        # 使用json模块加载配置文件
        with open(path, "r", encoding='utf-8') as f: Data = json.load(f)
    else:
        throw_exception("error","Linpg can only load json and yaml (if pyyaml is installed).")
    # 返回配置文件中的数据
    return Data if len(keys) == 0 else get_value_by_keys(Data,keys)

# 配置文件保存
def save_config(path:str, data:any) -> None:
    # 确保用于储存的文件夹存在
    dir_path:str = os.path.dirname(path)
    if len(dir_path) > 0 and not os.path.exists(dir_path): os.makedirs(dir_path)
    # 保存文件
    with open(path, "w", encoding='utf-8') as f:
        if path.endswith(".yaml"):
            if _YAML_INITIALIZED is True:
                yaml.dump(data, f, allow_unicode=True)
            else:
                throw_exception("error","You cannot save .yaml file because yaml is not imported successfully.")
        elif path.endswith(".json"):
            json.dump(data, f, indent=4, ensure_ascii=False, sort_keys=True)
        else:
            throw_exception("error","Linpg cannot save this kind of config, and can only save json and yaml (if pyyaml is installed).")

# 整理配置文件（读取了再存）
def organize_config_in_folder(pathname:str) -> None:
    for configFilePath in glob(pathname):
        data = load_config(configFilePath)
        save_config(configFilePath,data)
