# cython: language_level=3
import os
import pygame
import yaml
from pygame.locals import *
from copy import deepcopy
#初始化pygame
pygame.init()

#配置文件加载
def loadConfig(path,key=None):
    try:
        with open(path, "r", encoding='utf-8') as f:
            Data = yaml.load(f.read(),Loader=yaml.FullLoader)
    except yaml.constructor.ConstructorError:
        print("ZeroEngine-Warning: Encounter a fatal error while loading the yaml file in path:")
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
def saveConfig(path,data):
    with open(path, "w", encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True)

#初始化储存设置配置文件的变量
__ZERO_DATA = None

#获取设置配置文件
def get_setting(key=None,key2=None):
    if key == None:
        return deepcopy(__ZERO_DATA)
    elif key2 == None:
        return deepcopy(__ZERO_DATA[key])
    else:
        return deepcopy(__ZERO_DATA[key][key2])

#修改设置参数
def set_setting(key,key2=None,value=None):
    if value != None:
        if key2 == None:
            __ZERO_DATA[key] = value
        else:
            __ZERO_DATA[key][key2] = value

#保存设置参数
def save_setting():
    saveConfig("Save/setting.yaml",__ZERO_DATA)

#重新加载设置配置文件，请勿在引擎外调用，重置配置文件请用reload_setting()
def reload_DATA():
    global __ZERO_DATA
    #如果配置文件setting.yaml存在
    if os.path.exists("Save/setting.yaml"):
        __ZERO_DATA = loadConfig("Save/setting.yaml")
    #如果不存在就创建一个
    else:
        #导入local,查看默认语言
        import locale
        __ZERO_DATA = {
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
        if __ZERO_DATA["Language"][0] == "zh_CN":
            __ZERO_DATA["Language"] = "SimplifiedChinese"
        else:
            __ZERO_DATA["Language"] = "English"
        #别忘了看看Save文件夹是不是都不存在
        if not os.path.exists("Save"):
            os.makedirs("Save")
        save_setting()

#加载设置配置文件
reload_DATA()

#语言配置文件
__ZERO_LANG = None

#重新加载语言配置文件
def reload_lang():
    global __ZERO_LANG
    __ZERO_LANG = loadConfig("Lang/{}.yaml".format(__ZERO_DATA["Language"]))

#引擎初始化时应重新加载语言配置文件
reload_lang()

#获取语言配置文件
def get_lang(key,key2=None):
    if key2 == None:
        if key in __ZERO_LANG:
            return deepcopy(__ZERO_LANG[key])
        else:
            return None
    else:
        return deepcopy(__ZERO_LANG[key][key2])

#初始化屏幕
def screen_init(flags):
    return pygame.display.set_mode((__ZERO_DATA["Screen_size_x"], __ZERO_DATA["Screen_size_y"]),flags)
