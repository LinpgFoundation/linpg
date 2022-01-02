from .button import *

# Container抽象
class AbstractGameObjectsContainer(AbstractImageSurface):
    def __init__(self, bg_img: PoI, x: int_f, y: int_f, width: int, height: int, tag: str = "") -> None:
        super().__init__(StaticImage(bg_img, 0, 0, width, height) if bg_img is not None else bg_img, x, y, width, height, tag)

    # 获取物品container容器（子类需实现）
    def _get_container(self) -> Union[dict, list]:
        EXCEPTION.fatal("_get_container()", 1)

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
        if self.img is not None:
            self.img.set_width(value)

    # 设置高度
    def set_height(self, value: int_f) -> None:
        super().set_height(value)
        if self.img is not None:
            self.img.set_height(value)


# 使用Dict储存游戏对象的容器，类似html的div
class GameObjectsDictContainer(AbstractGameObjectsContainer):
    def __init__(self, bg_img: PoI, x: int_f, y: int_f, width: int, height: int, tag: str = "") -> None:
        super().__init__(bg_img, x, y, width, height, tag=tag)
        self.__items_container_dict: dict = {}
        self._item_being_hovered: Optional[str] = None

    @property
    def item_being_hovered(self) -> Optional[str]:
        return self._item_being_hovered

    # 获取物品合集
    def _get_container(self) -> dict:
        return self.__items_container_dict

    # 获取key的列表
    def keys(self) -> tuple:
        return tuple(self.__items_container_dict.keys())

    # 新增一个物品
    def set(self, key: str, new_item: Any) -> None:
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
    def display(self, surface: ImageSurface, offSet: tuple = ORIGIN) -> None:
        self._item_being_hovered = None
        if self.is_visible():
            current_abs_pos: tuple = Coordinates.add(self.pos, offSet)
            # 画出背景
            if self.img is not None and self.img is not NULL_SURFACE:
                self.img.display(surface, current_abs_pos)
            # 画出物品
            for key_of_game_object, game_object_t in self.__items_container_dict.items():
                game_object_t.display(surface, current_abs_pos)
                if isinstance(game_object_t, Button):
                    if game_object_t.has_been_hovered() is True:
                        self._item_being_hovered = str(key_of_game_object)
                elif isinstance(game_object_t, GameObject2d):
                    if game_object_t.is_hovered(current_abs_pos):
                        self._item_being_hovered = str(key_of_game_object)


# Dict容器占位符
NULL_DICT_CONTAINER: GameObjectsDictContainer = GameObjectsDictContainer(NULL_SURFACE, 0, 0, 0, 0)

# 使用List储存游戏对象的容器，类似html的div
class GameObjectsListContainer(AbstractGameObjectsContainer):
    def __init__(self, bg_img: PoI, x: int_f, y: int_f, width: int, height: int, tag: str = "") -> None:
        super().__init__(bg_img, x, y, width, height, tag=tag)
        self.__items_container_list: list = []
        self._item_being_hovered: int = -1

    @property
    def item_being_hovered(self) -> int:
        return self._item_being_hovered

    # 获取物品合集
    def _get_container(self) -> list:
        return self.__items_container_list

    # 新增一个物品
    def append(self, new_item: Any) -> None:
        self.__items_container_list.append(new_item)

    # 获取一个物品
    def get(self, index: int) -> Any:
        return self.__items_container_list[index]

    # 交换2个key名下的图片
    def swap(self, index1: int, index2: int) -> None:
        temp_reference = self.__items_container_list[index1]
        self.__items_container_list[index1] = self.__items_container_list[index2]
        self.__items_container_list[index2] = temp_reference

    # 移除一个物品
    def remove(self, index: int) -> None:
        self.__items_container_list.remove(index)

    # 把物品画到surface上
    def display(self, surface: ImageSurface, offSet: tuple = ORIGIN) -> None:
        self._item_being_hovered = -1
        if self.is_visible():
            current_abs_pos: tuple = Coordinates.add(self.pos, offSet)
            # 画出背景
            if self.img is not None and self.img is not NULL_SURFACE:
                self.img.display(surface, current_abs_pos)
            # 画出物品
            for i in range(len(self.__items_container_list)):
                self.__items_container_list[i].display(surface, current_abs_pos)
                if isinstance(self.__items_container_list[i], Button):
                    if self.__items_container_list[i].has_been_hovered() is True:
                        self._item_being_hovered = i
                elif isinstance(self.__items_container_list[i], GameObject):
                    if self.__items_container_list[i].is_hovered(current_abs_pos):
                        self._item_being_hovered = i
