# cython: language_level=3
from .ui import *

#版本信息管理模块
class InfoManager:
    def __init__(self) -> None:
        self.__INFO: dict = Config.load(os.path.join(os.path.dirname(__file__), "info.json"))
    # 获取当前版本号
    @property
    def current_version(self) -> str:
        return "{0}.{1}.{2}".format(self.__INFO["version"], self.__INFO["revision"], self.__INFO["patch"])
    # 获取作者邮箱
    @property
    def author_email(self) -> str: return deepcopy(self.__INFO["author_email"])
    # 获取github项目地址
    @property
    def repository_url(self) -> str: return deepcopy(self.__INFO["repository_url"])
    # 获取项目简介
    @property
    def short_description(self) -> str: return deepcopy(self.__INFO["short_description"])
    # 获取详细信息
    @property
    def details(self) -> dict: return {
        "version": self.current_version,
        "author_email": self.author_email,
        "description": self.short_description,
        "url": self.repository_url
        }

Info:InfoManager = InfoManager()

"""即将弃置"""
# 获取当前版本号
def get_current_version() -> str: return Info.current_version
# 获取作者邮箱
def get_author_email() -> str: return Info.author_email
# 获取github项目地址
def get_repository_url() -> str: return Info.repository_url
# 获取项目简介
def get_short_description() -> str: return Info.short_description