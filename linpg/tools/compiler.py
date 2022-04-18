import json
import os
from glob import glob
from multiprocessing import Process
import setuptools  # type: ignore
from Cython.Build import cythonize  # type: ignore


# 编译进程模块
class CompileProcess(Process):
    def __init__(self, path: str, generate_html: bool, language_level: str, keep_c: bool) -> None:
        super().__init__()
        self.__path: str = path
        self.__generate_html: bool = generate_html
        self.__language_level: str = language_level
        self.__keep_c: bool = keep_c

    def run(self) -> None:
        setuptools.setup(ext_modules=cythonize(self.__path, annotate=self.__generate_html, language_level=self.__language_level))
        # 删除c文件
        if not self.__keep_c:
            os.remove(self.__path.replace(".py", ".c"))
        os.remove(self.__path)


if __name__ == "__main__":

    # 编译进程管理模组
    class CompileProcessManager:
        # 加载参数
        with open("builder_data_cache.json", "r", encoding="utf-8") as f:
            Data: dict = json.load(f)
            # 是否保留c文件
            __keep_c: bool = bool(Data["keep_c"])
            # 是否产生html文件
            __generate_html: bool = bool(Data["generate_html"])
            # 是否启用多线程
            __enable_multiprocessing: bool = bool(Data["enable_multiprocessing"])
            # 语言版本
            __language_level: str = str(Data["language_level"])
            # 储存源代码的文件的路径
            __source_folder: str = str(Data["source_folder"])
            # 需要忽略的文件的关键词
            __ignore_key_words: tuple = tuple(Data["ignore_key_words"])
        # 移除参数文件
        os.remove("builder_data_cache.json")
        # 储存进程的文件夹
        __compile_processes: list[CompileProcess] = []

        # 是否忽略文件
        @classmethod
        def __if_ignore(cls, path: str) -> bool:
            for key_word in cls.__ignore_key_words:
                if key_word in path:
                    return True
            return False

        # 创建编译进程
        @classmethod
        def __generate_process(cls, path: str) -> None:
            if not os.path.isdir(path):
                if path.endswith(".py") and not cls.__if_ignore(path):
                    # 如果使用多线程
                    if cls.__enable_multiprocessing is True:
                        cls.__compile_processes.append(
                            CompileProcess(path, cls.__generate_html, cls.__language_level, cls.__keep_c)
                        )
                    # 如果不使用多线程（用于debug)
                    else:
                        setuptools.setup(
                            ext_modules=cythonize(
                                path, show_all_warnings=True, annotate=cls.__generate_html, language_level=cls.__language_level
                            )
                        )
                        # 删除c文件
                        if not cls.__keep_c:
                            os.remove(path.replace(".py", ".c"))
                        os.remove(path)
            elif "pyinstaller" not in path and "pycache" not in path:
                if not cls.__if_ignore(path):
                    for file_in_dir in glob(os.path.join(path, "*")):
                        cls.__generate_process(file_in_dir)

        # 初始化编译进程
        @classmethod
        def init(cls) -> None:
            cls.__generate_process(cls.__source_folder)

        # 开始所有的进程
        @classmethod
        def start(cls) -> None:
            for _process in cls.__compile_processes:
                _process.start()

        # 确保所有进程执行完后才退出
        @classmethod
        def join(cls) -> None:
            for _process in cls.__compile_processes:
                _process.join()

    # 初始化，创建进程
    CompileProcessManager.init()
    # 启动所有进程
    CompileProcessManager.start()
    # 在进程结束前不要退出
    CompileProcessManager.join()
