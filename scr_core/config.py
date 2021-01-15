# cython: language_level=3
from __future__ import annotations
#python本体库
import os
from copy import deepcopy
from typing import Any,List
#额外库
import pygame
from pygame.locals import *
import yaml
#初始化pygame
pygame.init()

#配置文件加载
def loadConfig(path:str,key:str=None) -> Any:
    try:
        with open(path, "r", encoding='utf-8') as f:
            Data = yaml.load(f.read(),Loader=yaml.FullLoader)
    except yaml.constructor.ConstructorError:
        print("LinpgEngine-Warning: Encounter a fatal error while loading the yaml file in path:")
        print("'{}'".format(path))
        print("One possible reason is that at least one numpy array exists inside the yaml file.")
        print("The program will try to load the data using yaml.UnsafeLoader.")
        with open(path, "r", encoding='utf-8') as f:
            Data = yaml.load(f.read(), Loader=yaml.UnsafeLoader)
    if key == None:
        return Data
    else:
        return Data[key]

#配置文件保存
def saveConfig(path:str,data:Any) -> None:
    with open(path, "w", encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True)

#初始化储存设置配置文件的变量
__LINPG_DATA = None

#获取设置配置文件
def get_setting(key:str=None,key2:str=None) -> Any:
    if key == None:
        return deepcopy(__LINPG_DATA)
    elif key2 == None:
        return deepcopy(__LINPG_DATA[key])
    else:
        return deepcopy(__LINPG_DATA[key][key2])

#修改设置参数
def set_setting(key:str,key2:str=None,value:Any=None) -> None:
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
            "Screen_size_x": 1920,
            "Screen_size_y": 1080,
            "Sound":{
                "background_music": 100,
                "sound_effects": 100,
                "sound_environment": 100,
            }
        }
        if __LINPG_DATA["Language"][0] == "zh_CN":
            __LINPG_DATA["Language"] = "SimplifiedChinese"
        else:
            __LINPG_DATA["Language"] = "English"
        #别忘了看看Save文件夹是不是都不存在
        if not os.path.exists("Save"):
            os.makedirs("Save")
        save_setting()

#加载设置配置文件
reload_DATA()

#语言配置文件
__LINPG_LANG = None

#重新加载语言配置文件
def reload_lang() -> None:
    global __LINPG_LANG
    __LINPG_LANG = loadConfig("Lang/{}.yaml".format(__LINPG_DATA["Language"]))

#引擎初始化时应重新加载语言配置文件
reload_lang()

#获取语言配置文件
def get_lang(key:str,key2:str=None) -> Any:
    if key2 == None:
        if key in __LINPG_LANG:
            return deepcopy(__LINPG_LANG[key])
        else:
            return None
    else:
        return deepcopy(__LINPG_LANG[key][key2])

#初始化屏幕
def screen_init(flags:Any) -> Any:
    return pygame.display.set_mode((__LINPG_DATA["Screen_size_x"], __LINPG_DATA["Screen_size_y"]),flags)

#全局数据
__LINPG_GLOBAL_DATA = {}

#设置特定的全局数据
def set_glob_value(key:str,value:Any) -> None:
    global __LINPG_GLOBAL_DATA
    __LINPG_GLOBAL_DATA[key] = value
#获取特定的全局数据
def get_glob_value(key:str) -> Any:
    return deepcopy(__LINPG_GLOBAL_DATA[key])
def if_get_set_value(key:str,valueToGet:Any,valueToSet:Any) -> bool:
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
