from os import path as PATH
from ..exception import EXCEPTION

__all__ = ["ASSET"]

"""
引擎素材路径
"""
_LINPG_INTERNAL_IMAGE_PATH: str = PATH.join(PATH.dirname(__file__), "image")
_LINPG_INTERNAL_UI_IMAGE_PATH: str = PATH.join(_LINPG_INTERNAL_IMAGE_PATH, "ui")

"""
自定义素材路径
"""
_CUSTOM_UI_IMAGE_PATH: str = PATH.join("Assets", "image", "UI")

# 资源管理模块
class AssetManager:
    @staticmethod
    def resolve_path(file_path: str) -> str:
        file_path = PATH.join(file_path)
        file_name: str
        if not file_path.startswith("<!"):
            return file_path
        elif file_path.startswith("<!ui>"):
            file_name = file_path[5:]
            if PATH.exists((internal_path := PATH.join(_CUSTOM_UI_IMAGE_PATH, file_name))) or PATH.exists(
                (internal_path := PATH.join(_LINPG_INTERNAL_UI_IMAGE_PATH, file_name))
            ):
                return internal_path
            else:
                EXCEPTION.fatal('Cannot find (essential) ui file "{}"'.format(file_name))
        else:
            EXCEPTION.fatal('Invaid tag: "{}"'.format(file_path))


ASSET = AssetManager()
