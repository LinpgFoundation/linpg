import os
import shutil

#现编译文件
os.system("python compiler.py build_ext --inplace")

#复制现有文件
if os.path.exists("linpg"): shutil.rmtree('linpg')
shutil.copytree("../linpg","linpg")
os.remove("linpg/setup.py")

#升级build工具
os.system("python -m pip install --upgrade build")

os.system("python -m build --no-isolation")

os.system("python -m pip install --user --upgrade twine")

os.system("twine upload dist/*")

folders_need_remove = ["dist","linpg.egg-info","Save","build","linpg"]
for path in folders_need_remove:
    shutil.rmtree(path)