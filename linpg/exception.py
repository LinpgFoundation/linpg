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

    # 生成错误报告
    @classmethod
    def __log(cls, msg: str) -> None:
        # 如果存储错误报告的文件夹不存在
        if not os.path.exists(cls.__CRASH_REPORTS_PATH):
            os.mkdir(cls.__CRASH_REPORTS_PATH)
        # 写入讯息
        with open(os.path.join(cls.__CRASH_REPORTS_PATH, "crash_{}.txt".format(cls.__TIME_STAMP_WHEN_LINPG_STARTED)), "a", encoding="utf-8") as f:
            f.write("[{0}]\n{1}\n".format(datetime.now().strftime("%Y/%m/%d %H:%M:%S"), msg))
            f.write("Environment: {0} with {1}".format(platform.platform(), cls.get_python_version()))

    # 获取python版本
    @staticmethod
    def get_python_version() -> str:
        return platform.python_version()

    # 告知不严重但建议查看的问题
    @staticmethod
    def inform(info: str) -> None:
        print("LinpgEngine wants to inform you: {}".format(info))

    # 警告开发者非严重错误
    @classmethod
    def warn(cls, info: str) -> None:
        cls.__log("Warning Message From Linpg: {}".format(info))
        # 打印出警告
        print("LinpgEngine-Warning: {}".format(info))

    # 严重错误
    @classmethod
    def fatal(cls, info: str, error_type_id: int = 0) -> NoReturn:
        cls.__log("Error Message From Linpg: {}".format(info))
        # 打印出错误，并停止进程
        if error_type_id == 1:
            raise cls.FunctionIsNotImplemented('A parent class requires you to implement "{}" function before you can use it'.format(info))
        elif error_type_id == 2:
            raise cls.FileNotExists(info)
        elif error_type_id == 3:
            raise cls.ToolIsMissing(info)
        else:
            raise cls.Error(info)
