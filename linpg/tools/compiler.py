import json
import os
from glob import glob
from setuptools import setup  # type: ignore
from Cython.Build import cythonize  # type: ignore

# py编译模块
with open("builder_data_cache.json", "r", encoding="utf-8") as f:
    Data: dict = json.load(f)
    # 是否保留c文件
    _keep_c: bool = bool(Data["keep_c"])
    # 是否产生html文件
    _generate_html: bool = bool(Data["generate_html"])
    # 展示所有警告
    _show_all_warnings: bool = bool(Data["show_all_warnings"])
    # 语言版本
    _language_level: str = str(Data["language_level"])
    # 储存源代码的文件的路径
    _source_folder: str = str(Data["source_folder"])
    # 需要忽略的文件的关键词
    _ignore_key_words: tuple = tuple(Data["ignore_key_words"])

os.remove("builder_data_cache.json")

# 是否忽略文件
def _if_ignore(path: str) -> bool:
    for key_word in _ignore_key_words:
        if key_word in path:
            return True
    return False


# 编译
def _compile(path: str) -> None:
    if not os.path.isdir(path):
        if path.endswith(".py") and not _if_ignore(path):
            setup(
                ext_modules=cythonize(
                    path,
                    show_all_warnings=_show_all_warnings,
                    annotate=_generate_html,
                    language_level=_language_level,
                )
            )
            # 删除c文件
            if not _keep_c:
                os.remove(path.replace(".py", ".c"))
            os.remove(path)
    elif "pyinstaller" not in path and "pycache" not in path:
        if not _if_ignore(path):
            for file_in_dir in glob(os.path.join(path, "*")):
                _compile(file_in_dir)


# 开始编译目标文件
_compile(_source_folder)
