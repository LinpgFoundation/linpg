from subprocess import DEVNULL, STDOUT, check_call
from ..lang import *


class AbstractToolSystem:

    _TOOL_FOLDER: str = str(DataBase.get("Paths", "ThirdPartyLibrariesFolder"))
    _TOOL_LIBRARIES: dict = dict(DataBase.get("Paths", "ThirdPartyLibraries"))

    def __init__(self, recommend_version: str, tool_path: str) -> None:
        self.__RECOMMENDED_VERSION: str = recommend_version
        self.__TOOL_PATH: str = tool_path

    # 获取ffmpeg库版本
    def get_recommended_version(self) -> str:
        return self.__RECOMMENDED_VERSION

    # 检测
    def _check_path(self, input_path: str) -> None:
        if not os.path.exists(input_path):
            raise FileNotExists()
        elif not os.path.exists(self.__TOOL_PATH):
            raise ToolIsMissing()

    # 运行命令
    def _run_cmd(self, command_line: list[str], show_cmd_output: bool = False) -> None:
        command_line.insert(0, self.__TOOL_PATH)
        if self.__TOOL_PATH.endswith(".py") or self.__TOOL_PATH.endswith(".pyd"):
            command_line.insert(0, "python")
        if not show_cmd_output:
            check_call(command_line, stdout=DEVNULL, stderr=STDOUT)
        else:
            self._run_raw_cmd(command_line)

    # 直接运行命令
    def _run_raw_cmd(self, command_line: list[str], shell: bool = False) -> None:
        check_call(command_line, shell=shell)
