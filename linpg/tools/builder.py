from .abstract import *

# 搭建和打包文件的系统
class BuilderManager(AbstractToolSystem):
    def __init__(self) -> None:
        super().__init__("*", os.path.join(os.path.dirname(__file__), "compiler.py"))

    # 移除指定文件夹中的pycache文件夹
    @classmethod
    def __remove_cache(cls, path: str) -> None:
        for file_path in glob(os.path.join(path, "*")):
            if os.path.isdir(file_path):
                if "pycache" in file_path or "mypy_cache" in file_path:
                    shutil.rmtree(file_path)
                else:
                    cls.__remove_cache(file_path)

    # 删除特定文件夹
    @classmethod
    def search_and_remove_folder(cls, folder_to_search: str, stuff_to_remove: str) -> None:
        # 确保folder_to_search是一个目录
        if not os.path.isdir(folder_to_search):
            EXCEPTION.fatal("You can only search a folder!", 2)
        # 移除当前文件夹符合条件的目录/文件
        for path in glob(os.path.join(folder_to_search, "*")):
            if path.endswith(stuff_to_remove):
                shutil.rmtree(path)
            elif os.path.isdir(path):
                cls.search_and_remove_folder(path, stuff_to_remove)

    # 如果指定文件夹存在，则移除
    @staticmethod
    def delete_file_if_exist(path: str) -> None:
        Cache.delete_file_if_exist(path)

    # 复制文件
    @staticmethod
    def copy(files: tuple, target_folder: str) -> None:
        for the_file in files:
            # 如果是文件夹
            if os.path.isdir(the_file):
                shutil.copytree(the_file, os.path.join(target_folder, os.path.basename(the_file)))
            else:
                shutil.copy(the_file, os.path.join(target_folder, os.path.basename(the_file)))

    # 删除缓存
    @staticmethod
    def __clean_up() -> None:
        folders_need_remove: tuple = ("dist", "Save", "build", "crash_reports", "Cache")
        for _path in folders_need_remove:
            Cache.delete_file_if_exist(_path)

    # 编译
    def compile(
        self,
        source_folder: str,
        target_folder: str = "src",
        additional_files: tuple = tuple(),
        ignore_key_words: tuple = tuple(),
        enable_multiprocessing: bool = True,
        remove_building_cache: bool = True,
        update_the_one_in_sitepackages: bool = True,
    ) -> None:
        self.delete_file_if_exist(target_folder)
        # 复制文件到新建的src文件夹中，准备开始编译
        os.makedirs(target_folder)
        source_path_in_target_folder: str = os.path.join(target_folder, source_folder)
        shutil.copytree(source_folder, source_path_in_target_folder)
        # 移除不必要的py缓存
        self.__remove_cache(source_path_in_target_folder)
        # 把数据写入缓存文件以供编译器读取
        with open("builder_data_cache.json", "w", encoding="utf-8") as f:
            json.dump(
                {
                    "enable_multiprocessing": enable_multiprocessing,
                    "source_folder": source_path_in_target_folder,
                    "ignore_key_words": ignore_key_words,
                },
                f,
            )
        # 编译源代码
        self._run_cmd(["build_ext", "--build-lib", target_folder], True)
        # 删除缓存
        self.__clean_up()
        # 复制额外文件
        self.copy(additional_files, source_path_in_target_folder)
        # 通过复制init修复打包工具无法定位包的bug
        # self.copy(tuple([os.path.join(source_folder, "__init__.py")]), source_path_in_target_folder)
        # 删除build文件夹
        if remove_building_cache is True:
            self.delete_file_if_exist("build")
        # 删除在sitepackages中的旧build，同时复制新的build
        if update_the_one_in_sitepackages is True:
            # 移除旧的build
            self._run_py_cmd(["pip", "uninstall", os.path.basename(source_folder)])
            # 安装新的build
            self._run_py_cmd(["pip", "install", "."])

    # 打包上传最新的文件
    def upload_package(self) -> None:
        if os.path.exists("setup.py") or os.path.exists("setup.cfg"):
            # 升级build工具
            self._run_py_cmd(["pip", "install", "--upgrade", "build"])
            # 打包文件
            self._run_py_cmd(["build", "--no-isolation"])
            # 升级twine
            self._run_py_cmd(["pip", "install", "--upgrade", "twine"])
            # 要求用户确认dist文件夹中的打包好的文件之后在继续
            if input('Please confirm the files in "dist" folder and enter Y to continue:') == "Y":
                # 用twine上传文件
                self._run_raw_cmd(["twine", "upload", "dist/*"])
            # 删除缓存
            self.__clean_up()
        else:
            EXCEPTION.fatal("Cannot find setup file!", 2)


Builder: BuilderManager = BuilderManager()
