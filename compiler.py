from distutils.core import setup
from Cython.Build import cythonize
import glob
import os
import shutil

#py compiler.py build_ext --inplace

if __name__ == '__main__':

    #是否保留c文件
    keep_c_files:bool = False
    #是否产生html文件
    keep_html_files:bool = False
    #是否在编译后删除现有的pyd文件
    remove_all_pyd_at_the_end:bool = True

    #如果linpg文件夹不存在
    if not os.path.exists("../linpg"): os.makedirs("../linpg")
    #如果linpg文件夹存在
    else:
        #删除旧的build
        for path in glob.glob(r"../linpg/*"):
            if ".git" not in path:
                try:
                    shutil.rmtree(path)
                except NotADirectoryError:
                    os.remove(path)
    """编译python文件"""
    for the_folder in glob.glob(r"linpg/*"):
        if os.path.isdir(the_folder) and "__pyinstaller" not in the_folder:
            #生成pyd文件
            for path in glob.glob('{}/*.py'.format(the_folder)):
                setup(ext_modules=cythonize(path,show_all_warnings=True,annotate=True))
                #删除c文件
                if not keep_c_files: os.remove(path.replace(".py",".c"))
                #删除html文件
                if not keep_html_files: os.remove(path.replace(".html",".c"))
    #移动已经生成的pyd到对应文件夹中
    path_perfix = os.path.join("linpgdev","linpg")
    for folder_name in os.listdir(path_perfix):
        shutil.move(os.path.join(path_perfix,folder_name),"../linpg")

    """把不需要编译的文件拷贝到linpg中"""
    #基础文件
    files_for_setup = ["linpg/info.json","linpg/__init__.py"]
    for the_file in files_for_setup:
        shutil.copy(the_file,os.path.join("..",the_file))
    #语言文件
    shutil.copytree("linpg/lang","../linpg/lang")
    shutil.copytree("linpg/__pyinstaller","../linpg/__pyinstaller")

    #删除build文件夹
    if os.path.exists("build"): shutil.rmtree('build')
    if remove_all_pyd_at_the_end: shutil.rmtree('linpgdev')
