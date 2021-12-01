from .setting import *

# 全局数据
class GlobalValueManager:

    __DATA: dict = {}

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


# 版本信息管理模块
class InfoManager:

    __INFO: dict = dict(Config.load_internal("info.json"))

    # 确保linpg版本
    def ensure_linpg_version(self, action: str, revision: int, patch: int, version: int = 3) -> bool:
        if action == "==":
            return (
                version == int(self.__INFO["version"])
                and revision == int(self.__INFO["revision"])
                and patch == int(self.__INFO["patch"])
            )
        elif action == ">=":
            return (
                version >= int(self.__INFO["version"])
                and revision >= int(self.__INFO["revision"])
                and patch >= int(self.__INFO["patch"])
            )
        elif action == "<=":
            return (
                version <= int(self.__INFO["version"])
                and revision <= int(self.__INFO["revision"])
                and patch <= int(self.__INFO["patch"])
            )

    # 获取当前版本号
    @property
    def current_version(self) -> str:
        return "{0}.{1}.{2}".format(self.__INFO["version"], self.__INFO["revision"], self.__INFO["patch"])

    # 获取作者邮箱
    @property
    def author_email(self) -> str:
        return self.__INFO["author_email"]

    # 获取github项目地址
    @property
    def repository_url(self) -> str:
        return self.__INFO["repository_url"]

    # 获取项目简介
    @property
    def short_description(self) -> str:
        return self.__INFO["short_description"]

    # 获取详细信息
    @property
    def details(self) -> dict:
        return {
            "version": self.current_version,
            "author_email": self.author_email,
            "description": self.short_description,
            "url": self.repository_url,
        }


Info: InfoManager = InfoManager()
