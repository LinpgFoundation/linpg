# Linpg本身错误类
class Error(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


# 未实现子类的错误
class FunctionNotImplement(Error):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


# 对象文件不存在
class FileNotExists(Error):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


# 工具不存在
class ToolIsMissing(Error):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
