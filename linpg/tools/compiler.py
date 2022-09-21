# 编译方法
def compile_file(_path: str, keep_c: bool, debug_mode: bool, _compiler_directives: dict, _functions: tuple) -> None:
    if debug_mode is True:
        _functions[0](ext_modules=_functions[1](_path, show_all_warnings=True, annotate=True, language_level="3", compiler_directives=_compiler_directives))
    else:
        _functions[0](ext_modules=_functions[1](_path, language_level="3", compiler_directives=_compiler_directives))
    # 删除c文件
    if not keep_c:
        _functions[2](_path.replace(".py", ".c"))
    # 删除原始py文件
    _functions[2](_path)


if __name__ == "__main__":

    import json
    import os
    from glob import glob
    from multiprocessing import Process
    from setuptools import setup  # 此import不可以在Cython.Build之后
    from Cython.Build import cythonize  # type: ignore

    # 编译进程管理模组
    class CompileProcessManager:
        # 加载参数
        with open("builder_data_cache.json", "r", encoding="utf-8") as f:
            Data: dict = json.load(f)
            # 是否启用多线程
            __enable_multiprocessing: bool = bool(Data["enable_multiprocessing"])
            # 储存源代码的文件的路径
            __source_folder: str = str(Data["source_folder"])
            # 需要忽略的文件的关键词
            __ignore_key_words: tuple = tuple(Data["ignore_key_words"])
            # 是否启用debug模式
            __debug_mode: bool = bool(Data["debug_mode"])
            # 是否保存c文件
            __keep_c: bool = bool(Data["keep_c"])
            # 其他次要参数
            __compiler_directives: dict = dict(Data["compiler_directives"])
        # 移除参数文件
        os.remove("builder_data_cache.json")
        # 储存进程的文件夹
        __compile_processes: list[Process] = []
        # 编译用到的方法
        __FUNCTIONS: tuple = (setup, cythonize, os.remove)

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
                            Process(target=compile_file, args=(path, cls.__keep_c, cls.__debug_mode, cls.__compiler_directives, cls.__FUNCTIONS))
                        )
                    # 如果不使用多线程
                    else:
                        compile_file(path, cls.__keep_c, cls.__debug_mode, cls.__compiler_directives, cls.__FUNCTIONS)
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
