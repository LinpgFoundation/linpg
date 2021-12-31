from .Error import Error

# 对象文件不存在
class FileNotExists(Error):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
