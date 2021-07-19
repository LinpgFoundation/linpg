from .setting import *

# 全局数据
class GlobalValueManager:
    def __init__(self) -> None:
        self.__DATA: dict = {}

    # 获取特定的全局数据
    def get(self, key: str) -> any:
        return self.__DATA[key]

    # 设置特定的全局数据
    def set(self, key: str, value: any) -> None:
        self.__DATA[key] = value

    # 删除特定的全局数据
    def remove(self, key: str) -> None:
        del self.__DATA[key]

    # 清空所有全局数据
    def clear(self) -> None:
        self.__DATA.clear()

    # 如果不是对应的值，则设置为对应的值，返回是否对应
    def if_get_set(self, key: str, valueToGet: any, valueToSet: any) -> bool:
        if self.__DATA[key] == valueToGet:
            self.__DATA[key] = valueToSet
            return True
        else:
            return False


GlobalValue: GlobalValueManager = GlobalValueManager()
