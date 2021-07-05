import os
import linpg

LINPG_PATH: str = linpg.__path__[0]
LINPG_NAME: str = "linpg"

datas: list = []
folder_ignore: tuple = ("__pyinstaller", "__pycache__", ".git")

for file_name in os.listdir(LINPG_PATH):
    #文件夹
    if os.path.isdir(os.path.join(LINPG_PATH, file_name)):
        for folder_name_t in folder_ignore:
            if folder_name_t in file_name: continue
        datas.append((os.path.join(LINPG_PATH, file_name, "*"), os.path.join(LINPG_NAME, file_name)))
    #文件
    else:
        if ".gitignore" not in file_name:
            datas.append((os.path.join(LINPG_PATH, file_name), os.path.join(LINPG_NAME)))
