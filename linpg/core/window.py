import PySimpleGUI  # type: ignore
from .frame import *

# 设置PySimpleGUI主题
PySimpleGUI.theme(Specification.get("PySimpleGUITheme"))


# 确认窗口
class ConfirmMessageWindow:
    def __init__(self, title: str, message: str, keep_on_top: bool = True) -> None:
        self.__title: str = title
        self.__message: str = message
        self.__keep_on_top: bool = keep_on_top

    @staticmethod
    def YES() -> str:
        return Lang.get_text("Global", "yes")

    @staticmethod
    def NO() -> str:
        return Lang.get_text("Global", "no")

    # 更新信息
    def update_message(self, message: str) -> None:
        self.__message = message

    # 展示窗口
    def show(self) -> str:
        return str(
            PySimpleGUI.Window(
                self.__title,
                [[PySimpleGUI.Text(self.__message)], [PySimpleGUI.Submit(self.YES()), PySimpleGUI.Cancel(self.NO())]],
                keep_on_top=self.__keep_on_top,
            ).read(close=True)[0]
        )


# 警告窗口
class LinpgVersionChecker:
    def __init__(self, action: str, recommended_revision: int, recommended_patch: int, recommended_version: int = 3) -> None:
        if not Info.ensure_linpg_version(action, recommended_revision, recommended_patch, recommended_version):
            _quit_text: str = Lang.get_text("LinpgVersionIncorrect", "exit_button")
            if (
                PySimpleGUI.Window(
                    Lang.get_text("Global", "warning"),
                    [
                        [
                            PySimpleGUI.Text(
                                Lang.get_text("LinpgVersionIncorrect", "message").format(
                                    "3.{0}.{1}".format(recommended_revision, recommended_patch), Info.get_current_version()
                                )
                            )
                        ],
                        [
                            PySimpleGUI.Submit(Lang.get_text("LinpgVersionIncorrect", "continue_button")),
                            PySimpleGUI.Cancel(_quit_text),
                        ],
                    ],
                    keep_on_top=True,
                ).read(close=True)[0]
                == _quit_text
            ):
                from sys import exit

                exit()
