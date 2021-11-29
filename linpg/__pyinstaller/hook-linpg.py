import os
import linpg

__LINPG_PATH: str = linpg.__path__[0]
__LINPG_NAME: str = "linpg"

datas: list = []
folder_ignore: tuple = ("__pyinstaller", "__pycache__", ".git")

for file_name in os.listdir(__LINPG_PATH):
    # 文件夹
    if os.path.isdir(os.path.join(__LINPG_PATH, file_name)):
        ingore_this_folder: bool = False
        for folder_name_t in folder_ignore:
            if folder_name_t in file_name:
                ingore_this_folder = True
                break
        if not ingore_this_folder:
            datas.append((os.path.join(__LINPG_PATH, file_name), os.path.join(__LINPG_NAME, file_name)))
    # 文件
    elif "gitignore" not in file_name:
        datas.append((os.path.join(__LINPG_PATH, file_name), os.path.join(__LINPG_NAME)))
