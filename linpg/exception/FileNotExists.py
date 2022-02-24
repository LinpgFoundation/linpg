from .error import Error

# 对象文件不存在
class FileNotExists(Error):
    def __init__(self, *args: object):
        super().__init__(*args)
