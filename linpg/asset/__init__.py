from os import path as PATH
from ..exception import EXCEPTION

"""
引擎素材路径
"""
LINPG_INTERNAL_IMAGE_PATH: str = PATH.join(PATH.dirname(__file__), "image")
LINPG_INTERNAL_UI_IMAGE_PATH: str = PATH.join(LINPG_INTERNAL_IMAGE_PATH, "ui")

"""
自定义素材路径
"""
_CUSTOM_UI_IMAGE_PATH: str = PATH.join("Assets", "image", "UI")


def resolve_ui_path(file_name: str) -> str:
    if PATH.exists(path := PATH.join(_CUSTOM_UI_IMAGE_PATH, file_name)) or PATH.exists(
        path := PATH.join(LINPG_INTERNAL_UI_IMAGE_PATH, file_name)
    ):
        return path
    else:
        EXCEPTION.fatal('Cannot find essential ui file "{}"'.format(file_name))
