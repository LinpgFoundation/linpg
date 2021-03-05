# cython: language_level=3
from .experimental import *
from .config import loadConfig,saveConfig,glob
from os import remove

#整理配置文件（读取了再存）
def organizeConfigInFolder(pathname:str) -> None:
    for configFilePath in glob.glob(pathname):
        saveConfig(configFilePath,loadConfig(configFilePath))

#优化中文文档
def optimizeCNContent(filePath:str) -> None:
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
            except:
                pass
    #删除原始文件
    remove(filePath)
    #创建并写入新数据
    with open(filePath, "w", encoding='utf-8') as f:
        f.writelines(file_lines)

#优化文件夹中特定文件的中文字符串
def optimizeCNContenInFolder(pathname:str) -> None:
    for configFilePath in glob.glob(pathname):
        optimizeCNContent(configFilePath)