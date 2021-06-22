# cython: language_level=3
from .ui import *

"""版本信息"""
_INFO: dict = load_config(os.path.join(os.path.dirname(__file__), "info.json"))

# 获取当前版本号
def get_current_version() -> str: return "{0}.{1}.{2}".format(_INFO["version"], _INFO["revision"], _INFO["patch"])

# 获取作者邮箱
def get_author_email() -> str: return deepcopy(_INFO["author_email"])

# 获取github项目地址
def get_repository_url() -> str: return deepcopy(_INFO["repository_url"])

# 获取项目简介
def get_short_description() -> str: return deepcopy(_INFO["short_description"])