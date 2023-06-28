import os

from linpgtoolbox.builder import Builder, SmartAutoModuleCombineMode

# 暂时重命名__init__.py文件以防止其干扰mypy typing生成工具
TEMP_INIT_NAME: str = "TEMP__init__.py"
if os.path.exists("__init__.py"):
    os.rename("__init__.py", TEMP_INIT_NAME)

# 额外需要打包的文件
additional_files: tuple[str, ...] = ("README.md", "LICENSE", "CODE_OF_CONDUCT.md", "doc")

# 开始编译源代码
Builder.compile(
    "linpg",
    additional_files=additional_files,
    smart_auto_module_combine=SmartAutoModuleCombineMode.FOLDER_ONLY,
    update_the_one_in_sitepackages=True,
    include_pyinstaller_program=True,
    options={
        "enable_multiprocessing": True,
        "compiler_directives": {"emit_code_comments": False},
        "hidden_imports": [
            "PIL.Image",
            "PIL.ImageColor",
            "PIL.ImageFilter",
            "PySimpleGUI",
            "numpy",
            "pygame",
            "pygame.gfxdraw",
            "tkinter",
        ],
    },
)
# 如果前面__init__.py已被成功重命名，则把其重命名回去
if os.path.exists(TEMP_INIT_NAME):
    os.rename(TEMP_INIT_NAME, "__init__.py")

# 提示编译完成
for i in range(2):
    print("")
print("--------------------Done!--------------------")
for i in range(2):
    print("")

# 打包上传最新的文件
"""
match input("Do you want to package and upload the latest build (Y/n):"):
    case "Y":
        Builder.upload_package("cp311")
    case "N":
        Builder.delete_file_if_exist("src")
"""
