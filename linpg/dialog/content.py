from .render import *


# 视觉小说数据操作接口
class _DialogContent:
    def __init__(self, _data: dict) -> None:
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

    # 当前对话是否带有合法的下一个对话对象的id
    def has_next(self) -> bool:
        _target: Optional[str | list[dict]] = self.next.get("target") if self.next is not None else None
        return _target is not None and len(_target) > 0

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
        self.__part: str = ""
        # 当前对话的id
        self.__id: str = "head"
        # 当前对话的接口模块
        self.__current: Optional[_DialogContent] = None

    # 指向当前对话的数据的指针
    @property
    def current(self) -> _DialogContent:
        # 如果指针不存在，则更新当前对话的接口
        if self.__current is None:
            self.__current = _DialogContent(self.__dialog_data[self.__part][self.__id])
        return self.__current

    # 保存对当前对话的接口的修改
    def save_current_changes(self) -> None:
        self.__dialog_data[self.__part][self.__id] = self.current.to_dict()

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

    # 获取当前所在部分
    def get_part(self) -> str:
        return self.__part

    # 更新当前所在部分
    def set_part(self, _part: str) -> None:
        self.__part = _part
        self.__current = None

    # 移除段落
    def remove_section(self, _id: Optional[str] = None) -> None:
        self.__dialog_data[self.__part].pop(self.__id if _id is None else _id)

    # 获取段落
    def get_section(self, _part: Optional[str] = None) -> dict:
        return self.__dialog_data[self.__part if _part is None else _part]

    # 设置段落
    def set_section(self, _data: dict, _part: Optional[str] = None) -> None:
        self.__dialog_data[self.__part if _part is None else _part] = _data

    # 获取对话数据
    def get_dialog(self, _part: Optional[str] = None, _id: Optional[str] = None) -> dict:
        return self.__dialog_data[self.__part if _part is None else _part][self.__id if _id is None else _id]

    # 移除对话数据
    def remove_dialog(self, _part: Optional[str] = None, _id: Optional[str] = None) -> None:
        self.__dialog_data[self.__part if _part is None else _part].pop(self.__id if _id is None else _id)
