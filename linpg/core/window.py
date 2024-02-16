from tkinter import messagebox

from .frame import *


# 确认窗口
class ConfirmationDialogBox:
    def __init__(self, title: str, message: str) -> None:
        self.__title: str = title
        self.__message: str = message

    # 更新标题
    def set_title(self, title: str) -> None:
        self.__title = title

    # 更新信息
    def set_message(self, message: str) -> None:
        self.__message = message

    # 展示窗口
    def show(self) -> bool:
        return messagebox.askyesno(self.__title, self.__message, icon="question")


# 警告窗口
class LinpgVersionChecker:
    def __init__(self, action: str, recommended_revision: int, recommended_patch: int, recommended_version: int = 3) -> None:
        if not Info.ensure_linpg_version(action, recommended_revision, recommended_patch, recommended_version):
            if not ConfirmationDialogBox(
                Lang.get_text("Global", "warning"),
                Lang.get_text("LinpgVersionIncorrectMessage").format(f"3.{recommended_revision}.{recommended_patch}", Info.get_current_version()),
            ).show():
                from sys import exit

                exit()
