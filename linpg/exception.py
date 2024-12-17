import os
import platform
from datetime import datetime
from typing import NoReturn


# Linpg错误类管理器
class EXCEPTION:
    # 错误报告存储的路径
    __CRASH_REPORTS_PATH: str = "crash_reports"
    # 引擎启动时的时间戳
    __TIME_STAMP_WHEN_LINPG_STARTED: str = datetime.now().strftime("%Y%m%d")

    # Linpg本身错误类
    class Error(Exception):
        def __init__(self, *args: object):
            super().__init__(*args)

    # 对象文件不存在
    class FileNotExists(Exception):
        def __init__(self, *args: object):
            super().__init__(*args)

    # 未实现子类的错误
    class FunctionIsNotImplemented(Exception):
        def __init__(self, *args: object):
            super().__init__(*args)

    # 工具不存在
    class ToolIsMissing(Exception):
        def __init__(self, *args: object):
            super().__init__(*args)

    # 第三方库不存在
    class SitePackageNotExists(Exception):
        def __init__(self, *args: object):
            super().__init__(*args)

    # 生成错误报告
    @classmethod
    def __log(cls, msg: str) -> None:
        # 如果存储错误报告的文件夹不存在
        if not os.path.exists(cls.__CRASH_REPORTS_PATH):
            os.mkdir(cls.__CRASH_REPORTS_PATH)
        # 写入讯息
        with open(os.path.join(cls.__CRASH_REPORTS_PATH, f"crash_{cls.__TIME_STAMP_WHEN_LINPG_STARTED}.txt"), "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%Y/%m/%d %H:%M:%S')}]\n{msg}\n")
            f.write(f"Environment: {platform.platform()} with {cls.get_python_version()}")

    # 获取python版本
    @staticmethod
    def get_python_version() -> str:
        return platform.python_version()

    # 告知不严重但建议查看的问题
    @staticmethod
    def inform(info: str) -> None:
        print(f"Linpg Engine wants to inform you: {info}")

    # 警告开发者非严重错误
    @classmethod
    def warn(cls, info: str) -> None:
        cls.__log(f"Warning Message From Linpg: {info}")
        # 打印出警告
        print(f"Linpg Engine Internal Warning: {info}")

    # 严重错误
    @classmethod
    def fatal(cls, info: str, error_type_id: int = 0) -> NoReturn:
        cls.__log(f"Error Message From Linpg: {info}")
        # 打印出错误，并停止进程
        if error_type_id == 1:
            raise cls.FunctionIsNotImplemented(f'A parent class requires you to implement "{info}" function before you can use it')
        elif error_type_id == 2:
            raise cls.FileNotExists(info)
        elif error_type_id == 3:
            raise cls.ToolIsMissing(info)
        elif error_type_id == 4:
            raise cls.SitePackageNotExists(info)
        else:
            raise cls.Error(info)
