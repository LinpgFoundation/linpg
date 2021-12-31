import os
from datetime import datetime
from typing import NoReturn
from .Error import Error
from .FileNotExists import FileNotExists
from .FunctionIsNotImplemented import FunctionIsNotImplemented
from .ToolIsMissing import ToolIsMissing


# Linpg错误类管理器
class LinpgExceptionHandler:

    # 错误报告存储的路径
    __CRASH_REPORTS_PATH: str = "crash_reports"
    # 引擎启动时的时间戳
    __TIME_STAMP_WHEN_LINPG_STARTED: str = datetime.now().strftime("%Y%m%d")

    # 生成错误报告
    def __log(self, msg: str) -> None:
        # 如果存储错误报告的文件夹不存在
        if not os.path.exists(self.__CRASH_REPORTS_PATH):
            os.mkdir(self.__CRASH_REPORTS_PATH)
        # 写入讯息
        with open(
            os.path.join(self.__CRASH_REPORTS_PATH, "crash_{}.txt".format(self.__TIME_STAMP_WHEN_LINPG_STARTED)),
            "a",
            encoding="utf-8",
        ) as f:
            f.write("[{0}]\n{1}\n".format(datetime.now().strftime("%Y/%m/%d %H:%M:%S"), msg))

    # 告知不严重但建议查看的问题
    @staticmethod
    def inform(info: str) -> None:
        print("LinpgEngine wants to inform you: {}".format(info))

    # 警告开发者非严重错误
    def warn(self, info: str) -> None:
        self.__log("Warning Message From Linpg: {}".format(info))
        # 打印出警告
        print("LinpgEngine-Warning: {}".format(info))

    # 严重错误
    def fatal(self, info: str, error_type_id: int = 0) -> NoReturn:
        self.__log("Error Message From Linpg: {}".format(info))
        # 打印出错误，并停止进程
        if error_type_id == 1:
            raise FunctionIsNotImplemented(
                'A parent class requires you to implement "{}" function before you can use it'.format(info)
            )
        elif error_type_id == 2:
            raise FileNotExists(info)
        elif error_type_id == 3:
            raise ToolIsMissing(info)
        else:
            raise Error(info)


EXCEPTION: LinpgExceptionHandler = LinpgExceptionHandler()
