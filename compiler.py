from distutils.core import setup
from Cython.Build import cythonize
import glob
import os
import shutil

# py编译模块
class PythonCompiler:
    def __init__(self, keep_c: bool, keep_html: bool) -> None:
        # 是否保留c文件
        self.__keep_c: bool = keep_c
        # 是否产生html文件
        self.__keep_html: bool = keep_html
        # 展示所有警告
        self.__show_all_warnings: bool = True
        # 语言版本
        self.__language_level: str = "3"

    # 编译
    def compile(self, path_of_py: str) -> None:
        print("Start compiling file: {}".format(path_of_py))
        setup(
            ext_modules=cythonize(
                path_of_py,
                show_all_warnings=self.__show_all_warnings,
                annotate=self.__keep_html,
                language_level=self.__language_level,
            )
        )
        # 删除c文件
        if not self.__keep_c:
            os.remove(path_of_py.replace(".py", ".c"))


if __name__ == "__main__":
    # 初始化py编译模块
    PyCompiler = PythonCompiler(False, False)

    # 是否在编译后删除现有的pyd文件
    remove_all_pyd_at_the_end: bool = True
    if os.path.exists("../linpg/building_key.txt"):
        remove_all_pyd_at_the_end = False
        os.remove("../linpg/building_key.txt")
    if os.path.exists("src"):
        shutil.rmtree("src")

    """清空旧的Build"""
    # 如果linpg文件夹不存在
    if not os.path.exists("../linpg"):
        os.makedirs("../linpg")
    # 如果linpg文件夹存在
    else:
        # 删除旧的build
        for path in glob.glob(r"../linpg/*"):
            # 如果是文件夹
            if os.path.isdir(path):
                if ".git" not in path:
                    shutil.rmtree(path)
            else:
                os.remove(path)

    # 如果上一次编译的文件夹还存在，则删除
    if os.path.exists("linpgdev"):
        shutil.rmtree("linpgdev")

    # 不需要编译的本体文件
    files_for_setup = ["linpg/__pyinstaller"]

    """编译python文件"""
    for folder_name in glob.glob(r"linpg/*"):
        if os.path.isdir(folder_name):
            if "pyinstaller" not in folder_name and "pycache" not in folder_name:
                # 生成pyd文件
                for path in glob.glob(os.path.join(folder_name, "*")):
                    if "pycache" not in path:
                        # 如果是需要编译的py文件
                        if path.endswith(".py"):
                            PyCompiler.compile(path)
                        # 如果是文本文件
                        else:
                            files_for_setup.append(path)
        else:
            # 如果是需要编译的py文件
            if folder_name.endswith(".py"):
                PyCompiler.compile(folder_name)
            # 如果是文本文件
            else:
                files_for_setup.append(folder_name)

    """把不需要编译的文件拷贝到linpgdev/linpg中,等待复制"""
    for the_file in files_for_setup:
        # 如果是文件夹
        if os.path.isdir(the_file):
            shutil.copytree(the_file, os.path.join("linpgdev", the_file))
        else:
            shutil.copy(the_file, os.path.join("linpgdev", the_file))
    # 其他需要复制的解释性文件
    files_for_setup = ["README.md", "LICENSE", "CODE_OF_CONDUCT.md", "doc"]
    for the_file in files_for_setup:
        # 如果是文件夹
        if os.path.isdir(the_file):
            shutil.copytree(the_file, os.path.join("linpgdev", "linpg", the_file))
        else:
            shutil.copy(the_file, os.path.join("linpgdev", "linpg", the_file))

    """编译完成，cleanup"""
    # 把编译好的linpg拷贝到文件夹中
    if not remove_all_pyd_at_the_end:
        for file_or_folder in glob.glob(r"linpgdev/linpg/*"):
            if os.path.isdir(file_or_folder):
                shutil.copytree(
                    file_or_folder,
                    os.path.join(file_or_folder.replace("linpgdev", "..")),
                )
            else:
                shutil.copy(
                    file_or_folder,
                    os.path.join(file_or_folder.replace("linpgdev", "..")),
                )
        os.rename("linpgdev", "src")
    else:
        for file_or_folder in glob.glob(r"linpgdev/linpg/*"):
            shutil.move(file_or_folder, "../linpg")
        shutil.rmtree("linpgdev")
    # 删除build文件夹
    if os.path.exists("build"):
        shutil.rmtree("build")
