from .environment import *

# 管理场景装饰物的类
class DecorationObject(GameObject):
    def __init__(self, x: int, y: int, itemType: str, image: str):
        super().__init__(x, y)
        self.type = itemType
        self.image: str = image
        self.__status: dict = {}
        self.scale: float = 0.5

    def is_on_pos(self, pos: any) -> bool:
        return Pos.is_same(self.get_pos(), pos)

    def get_status(self, key: str) -> any:
        return self.__status[key]

    def set_status(self, key: str, value: any) -> None:
        self.__status[key] = value

    def remove_status(self, key: str) -> None:
        try:
            del self.__status[key]
        except KeyError:
            EXCEPTION.warn('Cannot remove status "{}" because it does not exist'.format(key))

    def blit(self, surface: ImageSurface, pos: tuple[int], is_dark: bool, alpha: int) -> None:
        imgToBlit = MAP_ENV_IMAGE.get_decoration_image(self.type, self.image, is_dark)
        imgToBlit.set_size(MAP_ENV_IMAGE.get_block_width() * self.scale, MAP_ENV_IMAGE.get_block_width() * self.scale)
        imgToBlit.set_alpha(alpha)
        imgToBlit.move_to(pos)
        imgToBlit.draw(surface)


# 篝火
class CampfireObject(DecorationObject):
    def __init__(self, x: int, y: int, itemType: str, lit_range: int):
        super().__init__(x, y, itemType, "campfire")
        self.range: int = lit_range
        self.__alpha: int = 255
        self.__img_id: int = get_random_int(0, 90)
        self.set_status("lit", True)

    @property
    def img_id(self) -> float:
        return self.__img_id / 10.0

    # 画出篝火（注意，alpha不会被使用，它只因为兼容性和一致性而存在）
    def blit(self, surface: ImageSurface, pos: tuple[int], is_dark: bool, alpha: int) -> None:
        # 查看篝火的状态是否正在变化，并调整对应的alpha值
        if self.get_status("lit") is True:
            if self.__alpha < 255:
                self.__alpha += 15
        else:
            if self.__alpha > 0:
                self.__alpha -= 15
        # 底层 - 未燃烧的图片
        if self.__alpha < 255:
            self.image = "extinguished"
            super().blit(surface, pos, is_dark, 255)
        # 顶层 - 燃烧的图片
        if self.__alpha > 0:
            self.image = "lit_{}".format(int(self.img_id))
            super().blit(surface, pos, is_dark, self.__alpha)
            if self.img_id >= MAP_ENV_IMAGE.get_decoration_num(self.type) - 2:
                self.__img_id = 0
            else:
                self.__img_id += 1


# 箱子
class ChestObject(DecorationObject):
    def __init__(self, x: int, y: int, itemType: str, items: dict, whitelist: list):
        super().__init__(x, y, itemType, itemType)
        # 箱内物品
        self.items: dict = items
        # 是否箱子有白名单（只能被特定角色拾取）
        self.whitelist: list = whitelist