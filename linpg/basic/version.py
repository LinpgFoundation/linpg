from typing import Final

from ..exception import Exceptions


# 版本信息管理模块
class Version:
    # 引擎主版本号
    __VERSION: Final[int] = 4
    # 引擎次更新版本号
    __REVISION: Final[int] = 0
    # 引擎补丁版本
    __PATCH: Final[int] = 0

    # 确保linpg版本
    @classmethod
    def ensure_linpg_version(cls, action: str, revision: int, patch: int, version: int = 3) -> bool:
        match action:
            case "==":
                return cls.__VERSION == version and cls.__REVISION == revision and cls.__PATCH == patch
            case ">=":
                return cls.__VERSION >= version and cls.__REVISION >= revision and cls.__PATCH >= patch
            case "<=":
                return cls.__VERSION <= version and cls.__REVISION <= revision and cls.__PATCH <= patch
            case _:
                Exceptions.fatal(f'Action "{action}" is not supported!')

    # 获取当前版本号
    @classmethod
    def get_current_version(cls) -> str:
        return f"{cls.__VERSION}.{cls.__REVISION}.{cls.__PATCH}"

    # 获取github项目地址
    @classmethod
    def get_repository_url(cls) -> str:
        return "https://github.com/LinpgFoundation/linpg"
