from .error import Error

# 工具不存在
class ToolIsMissing(Error):
    def __init__(self, *args: object):
        super().__init__(*args)
