# cython: language_level=3
#python库
import os, json
from copy import deepcopy
from datetime import datetime
from glob import glob
#尝试导入yaml库
YAML_INITIALIZED:bool = False
try:
    import yaml
    YAML_INITIALIZED = True
except:
    pass

#Linpg本身错误类
class Error(Exception):
    def __init__(self, message:str):
        super().__init__(message)

#抛出引擎内的异常
def throw_exception(exception_type:str, info:str) -> None:
    exception_type_lower:str = exception_type.lower()
    if exception_type_lower == "error":
        #生成错误报告
        if not os.path.exists("crash_reports"): os.mkdir("crash_reports")
        with open(os.path.join("crash_reports","crash_{}.txt".format(datetime.now().strftime("%m-%d-%Y_%H-%M-%S"))), "w", encoding='utf-8') as f:
            f.write("Error Message From Linpg: {}".format(info))
        #打印出错误
        raise Error('LinpgEngine-Error: {}'.format(info))
    elif exception_type_lower == "warning":
        #只在开发者模式开启时显示警告
        if get_setting("DeveloperMode") is True:
            #生成错误报告
            if not os.path.exists("crash_reports"): os.mkdir("crash_reports")
            with open(os.path.join("crash_reports","crash_{}.txt".format(datetime.now().strftime("%m-%d-%Y_%H-%M-%S"))), "w", encoding='utf-8') as f:
                f.write("Warning Message From Linpg: {}".format(info))
            #打印出警告
            print("LinpgEngine-Warning: {}".format(info))
        else:
            pass
    elif exception_type_lower == "info":
        print('LinpgEngine-Info: {}'.format(info))
    else:
        throw_exception("error","Hey, the exception_type '{}' is not acceptable!".format(exception_type))

#配置文件加载
def load_config(path:str, key:str=None) -> any:
    #检测配置文件是否存在
    if not os.path.exists(path): throw_exception("error","Cannot find file on path: {}".format(path))
    #按照类型加载配置文件
    if path.endswith(".yaml"):
        if YAML_INITIALIZED is True:
            try:
                #尝试使用默认模式加载yaml配置文件
                with open(path, "r", encoding='utf-8') as f: Data = yaml.load(f.read(), Loader=yaml.FullLoader)
            except yaml.constructor.ConstructorError:
                throw_exception("warning","Encounter a fatal error while loading the yaml file in path:\n'{}'\n\
                    One possible reason is that at least one numpy array exists inside the yaml file.\n\
                    The program will try to load the data using yaml.UnsafeLoader.".format(path))
                #使用安全模式加载yaml配置文件
                with open(path, "r", encoding='utf-8') as f: Data = yaml.load(f.read(), Loader=yaml.UnsafeLoader)
        else:
            throw_exception("error","You cannot load .yaml file because yaml is not imported successfully.")
    elif path.endswith(".json"):
        #使用json模块加载配置文件
        with open(path, "r", encoding='utf-8') as f: Data = json.load(f)
    else:
        throw_exception("error","Linpg can only load json and yaml (if pyyaml is installed).")
    #返回配置文件中的数据
    return Data if key is None else Data[key]

#配置文件保存
def save_config(path:str, data:any) -> None:
    with open(path, "w", encoding='utf-8') as f:
        if path.endswith(".yaml"):
            if YAML_INITIALIZED:
                yaml.dump(data, f, allow_unicode=True)
            else:
                throw_exception("error","You cannot save .yaml file because yaml is not imported successfully.")
        elif path.endswith(".json"):
            json.dump(data, f, indent=4, ensure_ascii=False, sort_keys=True)
        else:
            throw_exception("error","Linpg cannot save this kind of config, and can only save json and yaml (if pyyaml is installed).")

#整理配置文件（读取了再存）
def organize_config_in_folder(pathname:str) -> None:
    for configFilePath in glob(pathname):
        data = load_config(configFilePath)
        save_config(configFilePath,data)

#整理当前文件夹中的配置文件
#organize_config_in_folder(os.path.join(os.path.dirname(__file__),"*.json"))

#初始化储存设置配置文件的变量
_LINPG_SETTING:dict = None

#在不确定的情况下尝试获取设置配置文件
def try_get_setting(key:str, key2:str=None) -> any:
    if key in _LINPG_SETTING:
        if key2 is None:
            return deepcopy(_LINPG_SETTING[key])
        elif key2 in _LINPG_SETTING[key]:
            return deepcopy(_LINPG_SETTING[key][key2])
    return None

#获取设置配置文件
def get_setting(key:str=None, key2:str=None) -> any:
    if key is None:
        return deepcopy(_LINPG_SETTING)
    elif key2 is None:
        return deepcopy(_LINPG_SETTING[key])
    else:
        return deepcopy(_LINPG_SETTING[key][key2])

#修改设置参数
def set_setting(key:str, key2:str=None, value:any=None) -> None:
    if value is not None:
        if key2 is None:
            _LINPG_SETTING[key] = value
        else:
            _LINPG_SETTING[key][key2] = value

#保存设置参数
def save_setting() -> None: save_config("Save/setting.yaml",_LINPG_SETTING)

#修改设置参数并保存
def set_and_save_setting(key:str, key2:str=None, value:any=None) -> None:
    set_setting(key, key2, value)
    save_setting()

#重新加载设置配置文件，请勿在引擎外调用，重置配置文件请用reload_setting()
def reload_setting() -> None:
    global _LINPG_SETTING
    #如果配置文件setting.yaml存在
    if os.path.exists("Save/setting.yaml"): _LINPG_SETTING = load_config("Save/setting.yaml")
    #如果不存在就创建一个
    else:
        #导入local,查看默认语言
        import locale
        _LINPG_SETTING = load_config(os.path.join(os.path.dirname(__file__),"setting.json"))
        _LINPG_SETTING["Language"] = "SimplifiedChinese" if locale.getdefaultlocale()[0] == "zh_CN" else "English"
        #别忘了看看Save文件夹是不是都不存在
        if not os.path.exists("Save"): os.makedirs("Save")
        #保存设置
        save_setting()

#加载设置配置文件
reload_setting()

"""重要参数"""
#获取抗锯齿参数
def get_antialias() -> bool: return True if _LINPG_SETTING["Antialias"] is True else False
#获取文字信息
def get_font() -> str: return _LINPG_SETTING["Font"]
#设置文字信息
def set_font(value:str) -> None: _LINPG_SETTING["Font"] = value
#获取文字类型
def get_font_type() -> str: return _LINPG_SETTING["FontType"]
#设置文字类型
def set_font_type(value:str) -> None: _LINPG_SETTING["FontType"] = value
#获取文字的具体信息
def get_font_details() -> tuple: return get_font(), get_font_type(), get_antialias()

"""全局数据"""
_LINPG_GLOBAL_DATA:dict = {}
#设置特定的全局数据
def set_glob_value(key:str, value:any) -> None:
    global _LINPG_GLOBAL_DATA
    _LINPG_GLOBAL_DATA[key] = value
#获取特定的全局数据
def get_glob_value(key:str) -> any: return deepcopy(_LINPG_GLOBAL_DATA[key])
#如果不是对应的值，则设置为对应的值，返回是否对应
def if_get_set_value(key:str, valueToGet:any, valueToSet:any) -> bool:
    global _LINPG_GLOBAL_DATA
    if _LINPG_GLOBAL_DATA[key] == valueToGet:
        _LINPG_GLOBAL_DATA[key] = valueToSet
        return True
    else:
        return False
#删除特定的全局数据
def remove_glob_value(key:str) -> None:
    global _LINPG_GLOBAL_DATA
    del _LINPG_GLOBAL_DATA[key]

"""版本信息"""
_SETUP_INFO:dict = load_config(os.path.join(os.path.dirname(__file__),"info.json"))
#获取当前版本号
def get_current_version() -> str: return "{0}.{1}.{2}".format(_SETUP_INFO["version"],_SETUP_INFO["revision"],_SETUP_INFO["patch"])
#获取作者邮箱
def get_author_email() -> str: return deepcopy(_SETUP_INFO["author_email"])
#获取github项目地址
def get_repository_url() -> str: return deepcopy(_SETUP_INFO["repository_url"])
#获取项目简介
def get_short_description() -> str:  return deepcopy(_SETUP_INFO["short_description"])