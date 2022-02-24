from .error import Error

# 未实现子类的错误
class FunctionIsNotImplemented(Error):
    def __init__(self, *args: object):
        super().__init__(*args)
