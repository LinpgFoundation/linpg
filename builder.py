from glob import glob
from os import path as PATH
from site import getsitepackages
from linpg.tools.builder import Builder

# 编译源代码
if not PATH.exists("src") or input("Do you want to recompile everything (Y/n):") == "Y":
    # 编译所有文件
    additional_files: tuple[str] = ("README.md", "LICENSE", "CODE_OF_CONDUCT.md", "doc")
    Builder.compile("linpg", additional_files=additional_files)
    # 删除旧的build
    for path in glob(PATH.join(getsitepackages()[1], "linpg", "*")):
        # 如果是文件夹
        if PATH.isdir(path):
            if ".git" not in path:
                Builder.delete_file_if_exist(path)
        else:
            Builder.delete_file_if_exist(path)
    # 复制新的build
    Builder.copy(tuple(glob(PATH.join("src", "linpg", "*"))), PATH.join(getsitepackages()[1], "linpg"))

# 删除不需要的文件
cache_files: tuple[str] = ("crash_reports", "Save")
for folder_p in cache_files:
    Builder.delete_file_if_exist(folder_p)


# 提示编译完成
for i in range(2):
    print("")
print("--------------------Done!--------------------")
for i in range(2):
    print("")

# 打包上传最新的文件
action:str = input("Do you want to package and upload the lastest build (Y/n):")
if action == "Y":
    Builder.upload_package()
elif action != "N":
    Builder.delete_file_if_exist("src")
