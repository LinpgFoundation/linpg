from .render import *

# 视觉小说数据管理模块
class DialogContentManager:
    def __init__(self) -> None:
        # 视觉小说数据
        self.__dialog_data: Final[dict[str, dict[str, dict]]] = {}
        # 当前部分
        self.__part: str = ""
        # 当前对话的id
        self.__id: str = "head"

    def is_empty(self) -> bool:
        return len(self.__dialog_data) <= 0

    def clear(self) -> None:
        self.__dialog_data.clear()

    def update(self, _data: dict[str, dict[str, dict]]) -> None:
        self.__dialog_data.update(_data)

    def set(self, _data: dict) -> None:
        self.__dialog_data.clear()
        self.__dialog_data.update(_data)

    def get(self) -> dict[str, dict[str, dict]]:
        return self.__dialog_data

    def remove(self, _id: Optional[str] = None) -> None:
        self.__dialog_data[self.__part].pop(self.__id if _id is None else _id)

    def get_id(self) -> str:
        return self.__id

    def set_id(self, _id: str) -> None:
        self.__id = _id

    def get_part(self) -> str:
        return self.__part

    def set_part(self, _part: str) -> None:
        self.__part = _part

    def get_section(self, _part: Optional[str] = None) -> dict:
        return self.__dialog_data[self.__part if _part is None else _part]

    def set_section(self, _data: dict, _part: Optional[str] = None) -> None:
        _ref: dict[str, dict] = self.__dialog_data[self.__part if _part is None else _part]
        _ref.clear()
        _ref.update(_data)

    def get_dialog(self, _part: Optional[str] = None, _id: Optional[str] = None) -> dict:
        return self.__dialog_data[self.__part if _part is None else _part][self.__id if _id is None else _id]

    def set_dialog(self, _data: dict, _part: Optional[str] = None, _id: Optional[str] = None) -> None:
        _ref: dict = self.__dialog_data[self.__part if _part is None else _part][self.__id if _id is None else _id]
        _ref.clear()
        _ref.update(_data)

    def remove_dialog(self, _part: Optional[str] = None, _id: Optional[str] = None) -> None:
        self.__dialog_data[self.__part if _part is None else _part].pop(self.__id if _id is None else _id)
