import os
import shutil
from glob import glob
from linpgtoolkit import Builder

# 编译源代码
if not os.path.exists("src") or input("Do you want to recompile everything (Y/n):") == "Y":
    # 删除旧的build
    for path in glob(r"../linpg/*"):
        # 如果是文件夹
        if os.path.isdir(path):
            if ".git" not in path:
                shutil.rmtree(path)
        else:
            os.remove(path)
    additional_files: tuple[str] = ("README.md", "LICENSE", "CODE_OF_CONDUCT.md", "doc")
    # 编译所有文件
    Builder.compile("linpg", additional_files=additional_files)
    Builder.copy(tuple(glob(os.path.join("src", "linpg", "*"))), r"../linpg")

# 提示编译完成
for i in range(2):
    print("")
print("--------------------Done!--------------------")
for i in range(2):
    print("")

# 打包上传最新的文件
if input("Do you want to package and upload the lastest build (Y/n):") == "Y":
    Builder.upload_package()
