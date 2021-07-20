from distutils.core import setup
from Cython.Build import cythonize
import glob
import os
import shutil

if __name__ == "__main__":

    # 是否保留c文件
    keep_c_files: bool = False
    # 是否产生html文件
    keep_html_files: bool = False
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
    files_for_setup = ["linpg/__init__.py", "linpg/__pyinstaller"]

    """编译python文件"""
    for folder_name in glob.glob(r"linpg/*"):
        if os.path.isdir(folder_name) and "__pyinstaller" not in folder_name:
            # 生成pyd文件
            for path in glob.glob(os.path.join(folder_name, "*")):
                if "__pycache__" not in path:
                    # 如果是需要编译的py文件
                    if path.endswith(".py"):
                        setup(
                            ext_modules=cythonize(
                                path,
                                show_all_warnings=True,
                                annotate=keep_html_files,
                                language_level="3",
                            )
                        )
                        # 删除c文件
                        if not keep_c_files:
                            os.remove(path.replace(".py", ".c"))
                    # 如果是文本文件
                    else:
                        files_for_setup.append(path)

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
