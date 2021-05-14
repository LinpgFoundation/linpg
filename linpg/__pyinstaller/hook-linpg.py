import os
import linpg

LINPG_PATH: str = linpg.__path__[0]
LINPG_NAME: str = "linpg"

datas: list = []

for folder in os.listdir(LINPG_PATH):
    if os.path.isdir(os.path.join(LINPG_PATH, folder)):
        datas.append(
            (os.path.join(LINPG_PATH, folder, "*"), os.path.join(LINPG_NAME, folder))
        )
    else:
        datas.append((os.path.join(LINPG_PATH, folder), os.path.join(LINPG_NAME)))
