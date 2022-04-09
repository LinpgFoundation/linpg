from os import path as PATH
from linpg import Builder  # type: ignore

# 编译源代码
if not PATH.exists("src") or input("Do you want to recompile everything (Y/n):") == "Y":
    # 编译所有文件
    additional_files: tuple[str, ...] = ("README.md", "LICENSE", "CODE_OF_CONDUCT.md", "doc")
    Builder.compile("linpg", additional_files=additional_files, ignore_key_words=("compiler.py",))

# 提示编译完成
for i in range(2):
    print("")
print("--------------------Done!--------------------")
for i in range(2):
    print("")

# 打包上传最新的文件
action: str = input("Do you want to package and upload the lastest build (Y/n):")
if action == "Y":
    Builder.upload_package()
elif action != "N":
    Builder.delete_file_if_exist("src")
