from distutils.core import setup
from Cython.Build import cythonize
import glob
import os
import shutil

#py compiler.py build_ext --inplace

#是否编译Source中的游戏本体
debug_c = False
produce_html_files = False

#删除旧的pyd文件
if os.path.exists("scr_pyd"):
    shutil.rmtree('scr_pyd')

#生成Zero引擎的c和pyd文件
for path in glob.glob(r'scr_pyx/*.pyx'):
    setup(ext_modules=cythonize(path,show_all_warnings=True,annotate=produce_html_files))
    #删除Zero引擎的c文件
    if not debug_c:
        os.remove(path.replace(".pyx",".c"))

os.makedirs("scr_pyd")
for path in glob.glob(r'*.pyd'):
    shutil.move(path,"scr_pyd")
