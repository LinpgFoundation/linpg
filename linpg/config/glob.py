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

# 全局数据库
class DataBaseManager:

    # 初始化数据库
    __DATA: dict[str, dict] = dict(Config.load_internal("database.json"))
    if len(path := Config.resolve_path(os.path.join("Data", "database"))) > 0:
        for key, value in dict(Config.load(path)).items():
            if key not in __DATA:
                __DATA[key] = value
            else:
                __DATA[key].update(value)

    def get(self, key: str) -> dict:
        try:
            return self.__DATA[key]
        except KeyError:
            EXCEPTION.fatal('Cannot find key "{}" in the database'.format(key))


DataBase: DataBaseManager = DataBaseManager()
