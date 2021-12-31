from .Error import Error

# 未实现子类的错误
class FunctionIsNotImplemented(Error):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
