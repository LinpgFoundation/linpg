# cython: language_level=3
from copy import deepcopy
#尝试导入yaml库
YAML_INITIALIZED:bool = False
try:
    import yaml
    YAML_INITIALIZED = True
except:
    pass
#导入json库
import json
#导入basic模块
from .basic import *

#配置文件加载
def loadConfig(path:str, key:str=None) -> any:
    #检测配置文件是否存在
    if not os.path.exists(path): throwException("error","Cannot find file on path: {}".format(path))
    #按照类型加载配置文件
    if path.endswith(".yaml"):
        if YAML_INITIALIZED:
            try:
                #尝试使用默认模式加载yaml配置文件
                with open(path, "r", encoding='utf-8') as f: Data = yaml.load(f.read(),Loader=yaml.FullLoader)
            except yaml.constructor.ConstructorError:
                throwException("warning","Encounter a fatal error while loading the yaml file in path:\n'{}'\n\
                    One possible reason is that at least one numpy array exists inside the yaml file.\n\
                    The program will try to load the data using yaml.UnsafeLoader.".format(path))
                #使用安全模式加载yaml配置文件
                with open(path, "r", encoding='utf-8') as f: Data = yaml.load(f.read(), Loader=yaml.UnsafeLoader)
        else:
            throwException("error","You cannot load .yaml file because yaml is not imported successfully.")
    elif path.endswith(".json"):
        #使用json模块加载配置文件
        with open(path, "r", encoding='utf-8') as f: Data = json.load(f)
    else:
        throwException("error","Linpg cannot load this kind of config, and can only load json and yaml (if pyyaml is installed).")
    #返回配置文件中的数据
    return Data if key is None else Data[key]

#配置文件保存
def saveConfig(path:str, data:any) -> None:
    with open(path, "w", encoding='utf-8') as f:
        if path.endswith(".yaml"):
            if YAML_INITIALIZED:
                yaml.dump(data, f, allow_unicode=True)
            else:
                throwException("error","You cannot save .yaml file because yaml is not imported successfully.")
        elif path.endswith(".json"):
            json.dump(data, f, indent=4, ensure_ascii=False, sort_keys=True)
        else:
            throwException("error","Linpg cannot save this kind of config, and can only save json and yaml (if pyyaml is installed).")

#整理配置文件（读取了再存）
def organizeConfigInFolder(pathname:str) -> None:
    for configFilePath in glob(pathname):
        data = loadConfig(configFilePath)
        saveConfig(configFilePath,data)

#初始化储存设置配置文件的变量
_LINPG_DATA:dict = None

#在不确定的情况下尝试获取设置配置文件
def try_get_setting(key:str, key2:str=None) -> any:
    if key in _LINPG_DATA:
        if key2 is None:
            return deepcopy(_LINPG_DATA[key])
        elif key2 in _LINPG_DATA[key]:
            return deepcopy(_LINPG_DATA[key][key2])
    return None

#获取设置配置文件
def get_setting(key:str=None, key2:str=None) -> any:
    if key is None:
        return deepcopy(_LINPG_DATA)
    elif key2 is None:
        return deepcopy(_LINPG_DATA[key])
    else:
        return deepcopy(_LINPG_DATA[key][key2])

#修改设置参数
def set_setting(key:str, key2:str=None, value:any=None) -> None:
    if value is not None:
        if key2 is None:
            _LINPG_DATA[key] = value
        else:
            _LINPG_DATA[key][key2] = value

#保存设置参数
def save_setting() -> None: saveConfig("Save/setting.yaml",_LINPG_DATA)

#重新加载设置配置文件，请勿在引擎外调用，重置配置文件请用reload_setting()
def reload_DATA() -> None:
    global _LINPG_DATA
    #如果配置文件setting.yaml存在
    if os.path.exists("Save/setting.yaml"): _LINPG_DATA = loadConfig("Save/setting.yaml")
    #如果不存在就创建一个
    else:
        #导入local,查看默认语言
        import locale
        _LINPG_DATA = {
            "Antialias": True,
            "FPS": 60,
            "Font": "MicrosoftYaHei-2",
            "FontType": "custom",
            "FullScreen": True,
            "KeepVedioCache": True,
            "Language": locale.getdefaultlocale(),
            "MouseIconWidth": 18,
            "MouseMoveSpeed": 30,
            "ReadingSpeed": 0.5,
            "Screen_size": 120,
            "Sound":{
                "background_music": 100,
                "sound_effects": 100,
                "sound_environment": 100,
            }
        }
        _LINPG_DATA["Language"] = "SimplifiedChinese" if _LINPG_DATA["Language"][0] == "zh_CN" else "English"
        #别忘了看看Save文件夹是不是都不存在
        if not os.path.exists("Save"): os.makedirs("Save")
        #保存设置
        save_setting()

#加载设置配置文件
reload_DATA()

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
_SETUP_INFO:dict = loadConfig(os.path.join(os.path.dirname(__file__),"../info.json"))
#获取当前版本号
def get_current_version() -> str: return "{0}.{1}.{2}".format(_SETUP_INFO["version"],_SETUP_INFO["revision"],_SETUP_INFO["patch"])
#获取作者邮箱
def get_author_email() -> str: return deepcopy(_SETUP_INFO["author_email"])
#获取github项目地址
def get_repository_url() -> str: return deepcopy(_SETUP_INFO["repository_url"])
#获取项目简介
def get_short_description() -> str:  return deepcopy(_SETUP_INFO["short_description"])