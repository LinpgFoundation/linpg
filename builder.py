import os
import shutil

#新建一个key,以告诉编译器需要保留pyd文件
with open("../linpg/building_key.txt", "r", encoding='utf-8') as f: pass

#编译所有文件
os.system("python compiler.py build_ext --inplace")

#升级build工具
os.system("python -m pip install --upgrade build")

#打包文件
os.system("python -m build --no-isolation")

#升级twine
os.system("python -m pip install --user --upgrade twine")

#用twine上传文件
os.system("twine upload dist/*")

#删除不需要的文件
folders_need_remove = ["dist","linpg.egg-info","Save","build"]
for path in folders_need_remove:
    shutil.rmtree(path)