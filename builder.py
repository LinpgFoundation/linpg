from os import path as PATH
from linpgtoolbox.builder import Builder  # type: ignore

# 编译源代码
if not PATH.exists("src") or input("Do you want to recompile everything (Y/n):") == "Y":
    # 编译所有文件
    additional_files: tuple[str, ...] = ("README.md", "LICENSE", "CODE_OF_CONDUCT.md", "doc")
    Builder.compile(
        "linpg",
        additional_files=additional_files,
        smart_auto_module_combine=True,
        update_the_one_in_sitepackages=False,
        include_default_pyinstaller_program=True,
        options={"enable_multiprocessing": True, "compiler_directives": {"emit_code_comments": False}},
    )

# 提示编译完成
for i in range(2):
    print("")
print("--------------------Done!--------------------")
for i in range(2):
    print("")

# 打包上传最新的文件
action: str = input("Do you want to package and upload the latest build (Y/n):")
if action == "Y":
    Builder.upload_package()
elif action != "N":
    Builder.delete_file_if_exist("src")
