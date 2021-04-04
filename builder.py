import os
import shutil

#先编译所有文件
os.system("python compiler.py build_ext --inplace")

#复制现有文件
if os.path.exists("linpg_pkg"): shutil.rmtree('linpg_pkg')
shutil.copytree("../linpg","linpg_pkg")

#升级build工具
os.system("python -m pip install --upgrade build")

#打包文件
os.system("python -m build --no-isolation")

#升级twine
os.system("python -m pip install --user --upgrade twine")

#用twine上传文件
os.system("twine upload dist/*")

#删除不需要的文件
folders_need_remove = ["dist","linpg_pkg.egg-info","Save","build","linpg_pkg"]
for path in folders_need_remove:
    shutil.rmtree(path)