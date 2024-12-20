from .button import *


# Container抽象
class AbstractGameObjectsContainer(AbstractImageSurface, metaclass=ABCMeta):
    def __init__(self, bg_img: PoI | None, x: int_f, y: int_f, width: int, height: int, tag: str = "") -> None:
        super().__init__(StaticImage(bg_img, 0, 0, width, height) if bg_img is not None else None, x, y, width, height, tag)

    # 获取物品container容器（子类需实现）
    @abstractmethod
    def _get_container(self) -> dict | list:
        Exceptions.fatal("_get_container()", 1)

    # 物品数量
    @property
    def item_num(self) -> int:
        return len(self._get_container())

    # 清空物品栏
    def clear(self) -> None:
        self._get_container().clear()

    # 是否为空
    def is_empty(self) -> bool:
        return self.item_num <= 0

    # 设置宽度
    def set_width(self, value: int_f) -> None:
        super().set_width(value)
        if self.is_background_init():
            self._get_image_reference().set_width(value)

    # 设置高度
    def set_height(self, value: int_f) -> None:
        super().set_height(value)
        if self.is_background_init():
            self._get_image_reference().set_height(value)

    # 更新背景（非专业人员勿碰）
    def update_background(self, newImg: Any) -> None:
        self._set_image(newImg)

    # has background been init
    def is_background_init(self) -> bool:
        return self._get_image_reference() is not None and self._get_image_reference().is_not_null()


# 使用Dict储存游戏对象的容器，类似html的div
class GameObjectsDictContainer(AbstractGameObjectsContainer):
    def __init__(self, bg_img: PoI | None, x: int_f, y: int_f, width: int, height: int, tag: str = "") -> None:
        super().__init__(bg_img, x, y, width, height, tag=tag)
        self.__items_container_dict: dict = {}
        self._item_being_hovered: str | None = None

    def __setitem__(self, key: str, new_item: object | None) -> None:
        self.__items_container_dict[key] = new_item

    def __getitem__(self, key: str) -> Any:
        return self.__items_container_dict[key]

    def __len__(self) -> int:
        return len(self.__items_container_dict)

    @property
    def item_being_hovered(self) -> str | None:
        return self._item_being_hovered

    # 获取物品合集
    def _get_container(self) -> dict:
        return self.__items_container_dict

    # 获取key的列表
    def keys(self) -> tuple:
        return tuple(self.__items_container_dict.keys())

    # 新增一个物品
    def set(self, key: str, new_item: object | None) -> None:
        self.__items_container_dict[key] = new_item

    # 获取一个物品
    def get(self, key: str) -> Any:
        return self.__items_container_dict[key]

    # 交换2个key名下的图片
    def swap(self, key1: str, key2: str) -> None:
        temp_reference = self.__items_container_dict[key1]
        self.__items_container_dict[key1] = self.__items_container_dict[key2]
        self.__items_container_dict[key2] = temp_reference

    # 移除一个物品
    def remove(self, key: str) -> None:
        del self.__items_container_dict[key]

    # 是否包括
    def contain(self, key: str) -> bool:
        return key in self.__items_container_dict

    # 更新内容
    def _update(self, new_content: dict) -> None:
        self.__items_container_dict.update(new_content)

    # 把物品画到surface上
    def display(self, _surface: ImageSurface, offSet: tuple[int, int] = ORIGIN) -> None:
        self._item_being_hovered = None
        if self.is_visible():
            current_abs_pos: tuple[int, int] = Coordinates.add(self.pos, offSet)
            # 画出背景
            if self.is_background_init():
                self._get_image_reference().display(_surface, current_abs_pos)
            # 画出物品
            for key_of_game_object, game_object_t in self.__items_container_dict.items():
                game_object_t.display(_surface, current_abs_pos)
                if isinstance(game_object_t, Button):
                    if game_object_t.has_been_hovered() is True:
                        self._item_being_hovered = str(key_of_game_object)
                elif isinstance(game_object_t, GameObject2d):
                    if game_object_t.is_hovered(current_abs_pos):
                        self._item_being_hovered = str(key_of_game_object)


# 使用List储存游戏对象的容器，类似html的div
class GameObjectsListContainer(AbstractGameObjectsContainer):
    def __init__(self, bg_img: PoI | None, x: int_f, y: int_f, width: int, height: int, tag: str = "") -> None:
        super().__init__(bg_img, x, y, width, height, tag=tag)
        self.__items_container_list: list = []
        self._item_being_hovered: int = -1

    def __getitem__(self, index: int) -> Any:
        return self.__items_container_list[index]

    def __setitem__(self, index: int, new_item: object | None) -> None:
        self.__items_container_list[index] = new_item

    def __len__(self) -> int:
        return len(self.__items_container_list)

    @property
    def item_being_hovered(self) -> int:
        return self._item_being_hovered

    # 获取物品合集
    def _get_container(self) -> list:
        return self.__items_container_list

    # 新增一个物品
    def append(self, new_item: object | None) -> None:
        self.__items_container_list.append(new_item)

    # 交换2个key名下的图片
    def swap(self, index1: int, index2: int) -> None:
        temp_reference = self.__items_container_list[index1]
        self.__items_container_list[index1] = self.__items_container_list[index2]
        self.__items_container_list[index2] = temp_reference

    # 移除一个物品
    def remove(self, index: int) -> None:
        self.__items_container_list.pop(index)

    # 把物品画到surface上
    def display(self, _surface: ImageSurface, offSet: tuple[int, int] = ORIGIN) -> None:
        self._item_being_hovered = -1
        if self.is_visible():
            current_abs_pos: tuple[int, int] = Coordinates.add(self.pos, offSet)
            # 画出背景
            if self.is_background_init():
                self._get_image_reference().display(_surface, current_abs_pos)
            # 画出物品
            for i, _item in enumerate(self.__items_container_list):
                _item.display(_surface, current_abs_pos)
                if isinstance(_item, Button):
                    if _item.has_been_hovered() is True:
                        self._item_being_hovered = i
                elif isinstance(_item, GameObject2d):
                    if _item.is_hovered(current_abs_pos):
                        self._item_being_hovered = i
