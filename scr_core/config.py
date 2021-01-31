# cython: language_level=3
from copy import deepcopy
try:
    import yaml
    _CONFIG_TYPE = "YAML"
except:
    print("LinpgEngine-Warning: Cannot import yaml, we will try json instead.\n"
    "However, some function may be limited, we suggest you install yaml ASAP!")
    import json
    _CONFIG_TYPE = "JSON"
from .basic import *

#配置文件加载
def loadConfig(path:str,key:str=None) -> any:
    if _CONFIG_TYPE == "YAML":
        try:
            with open(path, "r", encoding='utf-8') as f:
                Data = yaml.load(f.read(),Loader=yaml.FullLoader)
        except yaml.constructor.ConstructorError:
            print("LinpgEngine-Warning: Encounter a fatal error while loading the yaml file in path:\n'{}'\n"
            "One possible reason is that at least one numpy array exists inside the yaml file.\n"
            "The program will try to load the data using yaml.UnsafeLoader.".format(path))
            with open(path, "r", encoding='utf-8') as f:
                Data = yaml.load(f.read(), Loader=yaml.UnsafeLoader)
    else:
        with open(path, "r", encoding='utf-8') as f:
            Data = json.load(f)
    if key == None:
        return Data
    else:
        return Data[key]

#配置文件保存
def saveConfig(path:str,data:any) -> None:
    with open(path, "w", encoding='utf-8') as f:
        if _CONFIG_TYPE == "YAML":
            yaml.dump(data, f, allow_unicode=True)
        else:
            json.dump(data, f)

#初始化储存设置配置文件的变量
__LINPG_DATA = None

#获取设置配置文件
def get_setting(key:str=None,key2:str=None) -> any:
    if key == None:
        return deepcopy(__LINPG_DATA)
    elif key2 == None:
        return deepcopy(__LINPG_DATA[key])
    else:
        return deepcopy(__LINPG_DATA[key][key2])

#修改设置参数
def set_setting(key:str,key2:str=None,value:any=None) -> None:
    if value != None:
        if key2 == None:
            __LINPG_DATA[key] = value
        else:
            __LINPG_DATA[key][key2] = value

#保存设置参数
def save_setting() -> None:
    saveConfig("Save/setting.yaml",__LINPG_DATA)

#重新加载设置配置文件，请勿在引擎外调用，重置配置文件请用reload_setting()
def reload_DATA() -> None:
    global __LINPG_DATA
    #如果配置文件setting.yaml存在
    if os.path.exists("Save/setting.yaml"):
        __LINPG_DATA = loadConfig("Save/setting.yaml")
    #如果不存在就创建一个
    else:
        #导入local,查看默认语言
        import locale
        __LINPG_DATA = {
            "Antialias": True,
            "FPS": 60,
            "Font": "MicrosoftYaHei-2",
            "FontType": "custom",
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
        __LINPG_DATA["Language"] = "SimplifiedChinese" if __LINPG_DATA["Language"][0] == "zh_CN" else "English"
        #别忘了看看Save文件夹是不是都不存在
        if not os.path.exists("Save"): os.makedirs("Save")
        #保存设置
        save_setting()

#加载设置配置文件
reload_DATA()

#全局数据
__LINPG_GLOBAL_DATA = {}

#设置特定的全局数据
def set_glob_value(key:str,value:any) -> None:
    global __LINPG_GLOBAL_DATA
    __LINPG_GLOBAL_DATA[key] = value
#获取特定的全局数据
def get_glob_value(key:str) -> any:
    return deepcopy(__LINPG_GLOBAL_DATA[key])
def if_get_set_value(key:str,valueToGet:any,valueToSet:any) -> bool:
    global __LINPG_GLOBAL_DATA
    if __LINPG_GLOBAL_DATA[key] == valueToGet:
        __LINPG_GLOBAL_DATA[key] = valueToSet
        return True
    else:
        return False
#删除特定的全局数据
def remove_glob_value(key:str) -> None:
    global __LINPG_GLOBAL_DATA
    del __LINPG_GLOBAL_DATA[key]
