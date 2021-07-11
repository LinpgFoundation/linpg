# cython: language_level=3
from __future__ import annotations
import json
import os
from copy import deepcopy
from datetime import datetime
from glob import glob
import shutil
# 尝试导入yaml库
_YAML_INITIALIZED:bool = False
try:
    import yaml
    _YAML_INITIALIZED = True
except Exception:
    pass

# Linpg本身错误类
class LinpgError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

# Linpg错误类管理器
class LinpgExceptionHandler:
    def __init__(self):
        #错误报告存储的路径
        self.__CRASH_REPORTS_PATH:str = "crash_reports"
    #严重错误
    def fatal(self, info:str):
        # 生成错误报告
        if not os.path.exists(self.__CRASH_REPORTS_PATH): os.mkdir(self.__CRASH_REPORTS_PATH)
        with open(os.path.join(self.__CRASH_REPORTS_PATH, "crash_{}.txt".format(datetime.now().strftime("%m-%d-%Y_%H-%M-%S"))), "w", encoding='utf-8') as f:
            f.write("Error Message From Linpg: {}".format(info))
        # 打印出错误
        raise LinpgError(info)
    #警告开发者非严重错误
    def warn(self, info:str) -> None:
        # 生成错误报告
        if not os.path.exists(self.__CRASH_REPORTS_PATH): os.mkdir(self.__CRASH_REPORTS_PATH)
        with open(os.path.join(self.__CRASH_REPORTS_PATH,"crash_{}.txt".format(datetime.now().strftime("%m-%d-%Y_%H-%M-%S"))), "w", encoding='utf-8') as f:
            f.write("Warning Message From Linpg: {}".format(info))
        # 打印出警告
        print("LinpgEngine-Warning: {}".format(info))
    #告知不严重但建议查看的问题
    def inform(self, info:str) -> None:
        print('LinpgEngine-Inform: {}'.format(info))

EXCEPTION = LinpgExceptionHandler()

#根据keys查找值，最后返回一个复制的对象
def get_value_by_keys(dict_to_check:dict, keys:tuple, warning:bool=True) -> any:
    pointer = dict_to_check
    for key in keys:
        try:
            pointer = pointer[key]
        except KeyError:
            if warning is True: EXCEPTION.warn(
                'Getting "KeyError" while trying to get {}!\nPlease check your code or report this bug to the developer!'
                .format(key)
                )
            return key
    return deepcopy(pointer)

class ConfigManager:
    def __init__(self) -> None:
        pass
    # 配置文件保存
    def load(self, path:str, *key:str) -> any:
        # 检测配置文件是否存在
        if not os.path.exists(path): EXCEPTION.fatal("Cannot find file on path: {}".format(path))
        # 按照类型加载配置文件
        if path.endswith(".yaml"):
            if _YAML_INITIALIZED is True:
                try:
                    # 尝试使用默认模式加载yaml配置文件
                    with open(path, "r", encoding='utf-8') as f: Data = yaml.load(f.read(), Loader=yaml.FullLoader)
                except yaml.constructor.ConstructorError:
                    EXCEPTION.inform(
                        "Encounter a fatal error while loading the yaml file in path:\n{}\n".format(path) + \
                        "One possible reason is that at least one numpy array exists inside the yaml file.\n" + \
                        "The program will try to load the data using yaml.UnsafeLoader."
                        )
                    # 使用安全模式加载yaml配置文件
                    with open(path, "r", encoding='utf-8') as f: Data = yaml.load(f.read(), Loader=yaml.UnsafeLoader)
            else:
                EXCEPTION.fatal("You cannot load .yaml file because yaml is not imported successfully.")
        elif path.endswith(".json"):
            # 使用json模块加载配置文件
            with open(path, "r", encoding='utf-8') as f: Data = json.load(f)
        else:
            EXCEPTION.fatal("Linpg can only load json and yaml (if pyyaml is installed).")
        # 返回配置文件中的数据
        return Data if len(key) == 0 else get_value_by_keys(Data, key)
    # 加载内部配置文件保存
    def load_internal(self, path:str, *key:str) -> any:
        Data_t = self.load(os.path.join(os.path.dirname(__file__), path))
        return Data_t if len(key) == 0 else get_value_by_keys(Data_t, key)
    # 配置文件保存
    def save(self, path:str, data:any) -> None:
        # 确保用于储存的文件夹存在
        dir_path:str = os.path.dirname(path)
        if len(dir_path) > 0 and not os.path.exists(dir_path): os.makedirs(dir_path)
        # 保存文件
        with open(path, "w", encoding='utf-8') as f:
            if path.endswith(".yaml"):
                if _YAML_INITIALIZED is True:
                    yaml.dump(data, f, allow_unicode=True)
                else:
                    EXCEPTION.fatal("You cannot save .yaml file because yaml is not imported successfully.")
            elif path.endswith(".json"):
                json.dump(data, f, indent=4, ensure_ascii=False, sort_keys=True)
            else:
                EXCEPTION.fatal("Linpg cannot save this kind of config, and can only save json and yaml (if pyyaml is installed).")
    # 整理配置文件（读取了再存）
    def organize(self, pathname:str) -> None:
        for configFilePath in glob(pathname):
            self.save(configFilePath, self.load(configFilePath))
    # 整理内部配置文件
    def organize_internal(self) -> None:
        self.organize(os.path.join(os.path.dirname(__file__), "*.json"))
    #优化中文文档
    def optimize_cn_content(self, filePath:str) -> None:
        #读取原文件的数据
        with open(filePath, "r", encoding='utf-8') as f:
            file_lines = f.readlines()
        #优化字符串
        for i in range(len(file_lines)):
            #如果字符串不为空
            if len(file_lines[i]) > 1:
                #替换字符
                file_lines[i] = file_lines[i]\
                    .replace("。。。","... ")\
                    .replace("。",". ")\
                    .replace("？？：","??: ")\
                    .replace("？？","?? ")\
                    .replace("？","? ")\
                    .replace("！！","!! ")\
                    .replace("！","! ")\
                    .replace("：",": ")\
                    .replace("，",", ")\
                    .replace("“",'"')\
                    .replace("”",'"')\
                    .replace("‘","'")\
                    .replace("’","'")\
                    .replace("（"," (")\
                    .replace("）",") ")\
                    .replace("  "," ")
                #移除末尾的空格
                try:
                    while file_lines[i][-2] == " ":
                        file_lines[i] = file_lines[i][:-2]+"\n"
                except Exception:
                    pass
        #删除原始文件
        os.remove(filePath)
        #创建并写入新数据
        with open(filePath, "w", encoding='utf-8') as f:
            f.writelines(file_lines)
    #优化文件夹中特定文件的中文字符串
    def optimize_cn_content_in_folder(self, pathname:str) -> None:
        for configFilePath in glob(pathname):
            self.optimize_cn_content(configFilePath)
    #删除特定文件夹
    def search_and_remove_folder(self, folder_to_search:str, stuff_to_remove:str) -> None:
        #确保folder_to_search是一个目录
        try:
            assert os.path.isdir(folder_to_search)
        except:
            EXCEPTION.fatal("You can only search a folder!")
        #移除当前文件夹符合条件的目录/文件
        for path in glob(os.path.join(folder_to_search, "*")):
            if path.endswith(stuff_to_remove):
                shutil.rmtree(path)
            elif os.path.isdir(path):
                self.search_and_remove_folder(path, stuff_to_remove)

Config:ConfigManager = ConfigManager()
