from .render import *


# 视觉小说数据操作接口
class _DialogContent:
    def __init__(self, _data: dict, _id: str) -> None:
        # id
        self.__id: str = _id
        # 背景图片
        self.background_image: Optional[str] = _data.get("background_image")
        # 背景音乐
        self.background_music: Optional[str] = _data.get("background_music")
        # 角色立绘
        self.character_images: list[str] = _data.get("character_images", [])
        # 对话
        self.contents: list[str] = _data.get("contents", [])
        # 讲述人
        self.narrator: str = _data.get("narrator", "")
        # 上一个
        self.last: Optional[str] = _data.get("last_dialog_id")
        # 下一个
        _next: Optional[dict] = _data.get("next_dialog_id")
        self.next: dict = _next if _next is not None else {}

    @property
    def id(self) -> str:
        return self.__id

    # 当前对话是否带有合法的下一个对话对象的id
    def has_next(self) -> bool:
        _target: Optional[str | list[dict]] = self.next.get("target") if self.next is not None else None
        return _target is not None and len(_target) > 0

    # 当前对话是否带有多个合法的下一个对话对象的id
    def has_multiple_next(self) -> bool:
        _target: Optional[str | list[dict]] = self.next.get("target") if self.next is not None else None
        return isinstance(_target, list) and len(_target) > 1

    def to_dict(self) -> dict:
        return {
            "background_image": self.background_image,
            "background_music": self.background_music,
            "character_images": self.character_images,
            "contents": self.contents,
            "last_dialog_id": self.last,
            "narrator": self.narrator,
            "next_dialog_id": self.next,
        }


# 视觉小说数据管理模块
class DialogContentManager:
    def __init__(self) -> None:
        # 视觉小说数据
        self.__dialog_data: Final[dict[str, dict[str, dict]]] = {}
        # 当前部分
        self.__section: str = ""
        # 当前对话的id
        self.__id: str = "head"
        # 当前对话的接口模块
        self.__current: Optional[_DialogContent] = None
        # 之前对话的接口模块
        self.__last: Optional[_DialogContent] = None
        # 上一次对话的接口模块
        self.__previous: Optional[_DialogContent] = None

    # 如果指向当前对话数据的指针不存在，则更新指针
    def __refresh_current(self) -> None:
        if self.__current is None:
            self.__previous = self.__current
            self.__current = _DialogContent(self.__dialog_data[self.__section][self.__id], self.__id)

    # 上一个对话的缓存
    @property
    def previous(self) -> Optional[_DialogContent]:
        self.__refresh_current()
        return self.__previous

    # 指向当前对话数据的指针
    @property
    def current(self) -> _DialogContent:
        self.__refresh_current()
        return self.__current  # type: ignore

    # 指向之前对话数据的指针
    @property
    def last(self) -> Optional[_DialogContent]:
        # 如果指针不存在，则更新接口
        if self.__last is None and self.current.last is not None:
            self.__last = _DialogContent(self.__dialog_data[self.__section][self.current.last], self.current.last)
        return self.__last

    # 保存对当前对话的接口的修改
    def save_current_changes(self) -> None:
        self.__dialog_data[self.__section][self.__id] = self.current.to_dict()

    # 是否数据为空
    def is_empty(self) -> bool:
        return len(self.__dialog_data) <= 0

    # 清空数据
    def clear(self) -> None:
        self.__dialog_data.clear()

    # 更新数据
    def update(self, _data: dict[str, dict[str, dict]]) -> None:
        self.__dialog_data.update(_data)

    # 获取数据
    def get(self) -> dict[str, dict[str, dict]]:
        return self.__dialog_data

    # 获取当前id
    def get_id(self) -> str:
        return self.__id

    # 更新当前id
    def set_id(self, _id: str) -> None:
        self.__id = _id
        self.__current = None
        self.__last = None

    # 获取当前所在部分
    def get_section(self) -> str:
        return self.__section

    # 更新当前所在部分
    def set_section(self, _section: str) -> None:
        self.__section = _section
        self.__current = None
        self.__last = None

    # 移除段落
    def remove_section(self, _id: Optional[str] = None) -> None:
        self.__dialog_data[self.__section].pop(self.__id if _id is None else _id)

    # 获取段落
    def get_section_content(self, _section: Optional[str] = None) -> dict:
        return self.__dialog_data[self.__section if _section is None else _section]

    # 设置段落
    def set_section_content(self, _data: dict, _section: Optional[str] = None) -> None:
        self.__dialog_data[self.__section if _section is None else _section] = _data

    # 获取对话数据
    def get_dialog(self, _section: Optional[str] = None, _id: Optional[str] = None) -> dict:
        return self.__dialog_data[self.__section if _section is None else _section][self.__id if _id is None else _id]

    # 移除对话数据
    def remove_dialog(self, _section: Optional[str] = None, _id: Optional[str] = None) -> None:
        self.__dialog_data[self.__section if _section is None else _section].pop(self.__id if _id is None else _id)
