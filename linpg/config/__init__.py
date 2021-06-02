# cython: language_level=3
from .glob import *

# 加载设置配置文件
reload_setting()

# 整理当前文件夹中的配置文件
# organize_config_in_folder(os.path.join(os.path.dirname(__file__),"*.json"))

"""版本信息"""
_SETUP_INFO: dict = load_config(os.path.join(os.path.dirname(__file__), "info.json"))

# 获取当前版本号
def get_current_version() -> str: return "{0}.{1}.{2}".format(_SETUP_INFO["version"], _SETUP_INFO["revision"], _SETUP_INFO["patch"])

# 获取作者邮箱
def get_author_email() -> str: return deepcopy(_SETUP_INFO["author_email"])

# 获取github项目地址
def get_repository_url() -> str: return deepcopy(_SETUP_INFO["repository_url"])

# 获取项目简介
def get_short_description() -> str: return deepcopy(_SETUP_INFO["short_description"])
