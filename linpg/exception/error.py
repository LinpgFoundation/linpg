# Linpg本身错误类
class Error(Exception):
    def __init__(self, *args: object):
        super().__init__(*args)
