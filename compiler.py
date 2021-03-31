from distutils.core import setup
from Cython.Build import cythonize
import glob
import os
import shutil

#py compiler.py build_ext --inplace

if __name__ == '__main__':

    #是否compile所有代码
    choice = input("Do you want to compile all the files (y/n):")
    if choice != "quit": compile_all = True if choice.lower() == "y" or len(choice) == 0 else False
    #是否保留c文件
    debug_c = False
    #是否产生html文件
    produce_html_files = False

    #如果仅是compile基础pyx文件
    if not compile_all:
        #删除旧的pyd文件
        if os.path.exists("scr_pyd"): shutil.rmtree('scr_pyd')
        #生成Linpg引擎的c和pyd文件
        for path in glob.glob(r'scr_pyx/*.pyx'):
            setup(ext_modules=cythonize(path,show_all_warnings=True,annotate=produce_html_files))
            #删除c文件
            if not debug_c: os.remove(path.replace(".pyx",".c"))
        #新建一个scr_pyd文件夹用于储存编译完的文件
        os.makedirs("scr_pyd")
        for path in glob.glob(r'*.pyd'): shutil.move(path,"scr_pyd")
    else:
        #如果linpg文件夹不存在
        if not os.path.exists("../linpg"):
            os.makedirs("../linpg")
        #如果linpg文件夹存在
        else:
            #删除旧的build
            for path in glob.glob(r'../linpg/*'):
                try:
                    shutil.rmtree(path)
                except NotADirectoryError:
                    os.remove(path)
        """处理python文件"""
        folders_need_process = ["scr_core","scr_py"]
        for the_folder in folders_need_process:
            #生成pyd文件
            for path in glob.glob('{}/*.py'.format(the_folder)):
                setup(ext_modules=cythonize(path,show_all_warnings=True,annotate=produce_html_files))
                #删除c文件
                os.remove(path.replace(".py",".c"))
            #移动已经生成的pyd到对应文件夹中
            folder_path = "../linpg/{}".format(the_folder)
            os.makedirs(folder_path)
            for path in glob.glob(r'*.pyd'): shutil.move(path,folder_path)
        """处理cython文件"""
        #生成pyd文件
        for path in glob.glob(r'scr_pyx/*.pyx'):
            setup(ext_modules=cythonize(path,show_all_warnings=True,annotate=produce_html_files))
            #删除c文件
            os.remove(path.replace(".pyx",".c"))
        #移动已经生成的pyd到对应文件夹中
        os.makedirs("../linpg/scr_pyd")
        for path in glob.glob(r'*.pyd'): shutil.move(path,"../linpg/scr_pyd")
        #把不需要编译的文件拷贝到linpg中
        files_for_setup = ["LICENSE","README.md","__init__.py","setup.py","pyproject.toml","setup.yaml"]
        for the_file in files_for_setup:
            shutil.copy(the_file,os.path.join("../linpg",the_file))
        shutil.copytree("lang","../linpg/lang")

    #删除build文件夹
    shutil.rmtree('build')