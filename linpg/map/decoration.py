from .image import *

# 管理场景装饰物的类
class DecorationObject(GameObject2d):
    def __init__(self, x: int, y: int, _id: str, itemType: str, image: str, status: dict):
        super().__init__(x, y)
        self.__id: str = _id
        self.__type: str = itemType
        self.image: strint = image
        self.__status: dict = status
        self.scale: float = 0.5

    def get_id(self) -> str:
        return self.__id

    def get_type(self) -> str:
        return self.__type

    def to_dict(self) -> dict:
        data_t: dict = {"x": self.x, "y": self.y, "image": self.image}
        if len(self.__status) > 0:
            data_t["status"] = deepcopy(self.__status)
        return data_t

    def is_on_pos(self, pos: object) -> bool:
        return Coordinates.is_same(self.get_pos(), pos)

    def _has_status(self, key: str) -> bool:
        return key in self.__status

    def get_status(self, key: str) -> object:
        return self.__status[key]

    def set_status(self, key: str, value: object) -> None:
        self.__status[key] = value

    def remove_status(self, key: str) -> None:
        try:
            del self.__status[key]
        except KeyError:
            EXCEPTION.warn('Cannot remove status "{}" because it does not exist'.format(key))

    def blit(self, surface: ImageSurface, pos: tuple[int, int], is_dark: bool, alpha: int) -> None:  # type: ignore[override]
        imgToBlit = DecorationImagesModule.get_image(self.__type, self.image, is_dark)
        imgToBlit.set_size(MapImageParameters.get_block_width() * self.scale, MapImageParameters.get_block_width() * self.scale)
        imgToBlit.set_alpha(alpha)
        imgToBlit.move_to(pos)
        imgToBlit.draw(surface)


# 篝火
class CampfireObject(DecorationObject):
    def __init__(self, x: int, y: int, _id: str, itemType: str, _range: int, status: dict):
        super().__init__(x, y, _id, itemType, itemType, status)
        self.range: int = _range
        self.__alpha: int = 255
        self.__img_id: int = get_random_int(0, 90)
        if not self._has_status("lit"):
            self.set_status("lit", True)

    def to_dict(self) -> dict:
        data_t: dict = super().to_dict()
        del data_t["image"]
        data_t["range"] = self.range
        if "status" in data_t and data_t["status"]["lit"] is True:
            del data_t["status"]["lit"]
            if len(data_t["status"]) <= 0:
                del data_t["status"]
        return data_t

    # 画出篝火（注意，alpha不会被使用，它只因为兼容性和一致性而存在）
    def blit(self, surface: ImageSurface, pos: tuple[int, int], is_dark: bool, alpha: int) -> None:  # type: ignore[override]
        # 查看篝火的状态是否正在变化，并调整对应的alpha值
        if self.get_status("lit") is True:
            if self.__alpha < 255:
                self.__alpha += 15
        elif self.__alpha > 0:
            self.__alpha -= 15
        # 底层 - 未燃烧的图片
        if self.__alpha < 255:
            self.image = 0
            super().blit(surface, pos, is_dark, 255)
        # 顶层 - 燃烧的图片
        if self.__alpha > 0:
            self.image = self.__img_id // 10
            super().blit(surface, pos, is_dark, self.__alpha)
            if self.image < DecorationImagesModule.get_image_num(self.get_type()) - 1:
                self.__img_id += 1
            else:
                self.__img_id = 10


# 箱子
class ChestObject(DecorationObject):
    def __init__(self, x: int, y: int, _id: str, itemType: str, items: dict, whitelist: list, status: dict):
        super().__init__(x, y, _id, itemType, itemType, status)
        # 箱内物品
        self.items: dict = items
        # 是否箱子有白名单（只能被特定角色拾取）
        self.whitelist: list = whitelist

    def to_dict(self) -> dict:
        data_t: dict = super().to_dict()
        del data_t["image"]
        if len(self.items) > 0:
            data_t["items"] = deepcopy(self.items)
        if len(self.whitelist) > 0:
            data_t["whitelist"] = deepcopy(self.whitelist)
        return data_t
