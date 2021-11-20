from .scrollbar import *


# 带有滚动条的Surface容器
class SurfaceContainerWithScrollbar(GameObjectsContainer, AbstractSurfaceWithScrollbar):
    def __init__(
        self, img: PoI, x: int_f, y: int_f, width: int, height: int, mode: str = "horizontal", tag: str = ""
    ) -> None:
        GameObjectsContainer.__init__(
            self, IMG.load(img, (width, height)) if img is not None else img, x, y, width, height, tag
        )
        AbstractSurfaceWithScrollbar.__init__(self)
        self.__surface_width: int = 0
        self.__surface_height: int = 0
        self.panding: int = 0
        self.distance_between_item: int = 20
        self.set_mode(mode)
        self.__item_per_line: int = 1

    def get_surface_width(self) -> int:
        return self.__surface_width

    def get_surface_height(self) -> int:
        return self.__surface_height

    # 每一行放多少个物品
    @property
    def item_per_line(self) -> int:
        return self.__item_per_line

    def get_item_per_line(self) -> int:
        return self.__item_per_line

    def set_item_per_line(self, value: int) -> None:
        self.__item_per_line = int(value)

    # 把素材画到屏幕上
    def display(self, surface: ImageSurface, off_set: tuple = ORIGIN) -> None:
        self._item_being_hovered = None
        if self.is_visible():
            # 如果有背景图片，则画出
            if self.img is not None:
                surface.blit(self.img, Coordinates.add(self.pos, off_set))
            # 计算出基础坐标
            current_x: int = int(self.abs_x + off_set[0])
            current_y: int = int(self.abs_y + off_set[1])
            if not self._mode:
                current_x += self.panding
            else:
                current_y += self.panding
            # 定义部分用到的变量
            abs_local_y: int
            crop_height: int
            new_height: int
            abs_local_x: int
            crop_width: int
            new_width: int
            item_has_been_dawn_on_this_line: int = 0
            # 画出物品栏里的图片
            for key, item in self._items_container.items():
                if item is not None:
                    if not self._mode:
                        abs_local_y = int(current_y - self.y)
                        if 0 <= abs_local_y < self.get_height():
                            new_height = self.get_height() - abs_local_y
                            if new_height > item.get_height():
                                new_height = item.get_height()
                            new_width = item.get_width()
                            if new_width > self.get_width():
                                new_width = self.get_width()
                            subsurface_rect = Rect(0, 0, new_width, new_height)
                            surface.blit(get_img_subsurface(item, subsurface_rect), (current_x, current_y))
                            if subsurface_rect.is_hovered((current_x, current_y)):
                                self._item_being_hovered = key
                        elif -(item.get_height()) <= abs_local_y < 0:
                            crop_height = -abs_local_y
                            new_height = item.get_height() - crop_height
                            if new_height > self.get_height():
                                new_height = self.get_height()
                            new_width = item.get_width()
                            if new_width > self.get_width():
                                new_width = self.get_width()
                            subsurface_rect = Rect(0, crop_height, new_width, new_height)
                            surface.blit(get_img_subsurface(item, subsurface_rect), (current_x, current_y + crop_height))
                            if subsurface_rect.is_hovered((current_x, current_y)):
                                self._item_being_hovered = key
                        # 换行
                        if item_has_been_dawn_on_this_line >= self.__item_per_line - 1:
                            current_y += self.distance_between_item + item.get_height()
                            current_x = int(self.abs_x + off_set[0] + self.panding)
                            item_has_been_dawn_on_this_line = 0
                        else:
                            current_x += self.distance_between_item + item.get_width()
                            item_has_been_dawn_on_this_line += 1
                    else:
                        abs_local_x = int(current_x - self.x)
                        if 0 <= abs_local_x < self.get_width():
                            new_width = self.get_width() - abs_local_x
                            if new_width > item.get_width():
                                new_width = item.get_width()
                            new_height = item.get_height()
                            if new_height > self.get_height():
                                new_height = self.get_height()
                            subsurface_rect = Rect(0, 0, new_width, new_height)
                            surface.blit(
                                get_img_subsurface(item, subsurface_rect),
                                (current_x, current_y),
                            )
                            if subsurface_rect.is_hovered((current_x, current_y)):
                                self._item_being_hovered = key
                        elif -(item.get_width()) <= abs_local_x < 0:
                            crop_width = -abs_local_x
                            new_width = item.get_width() - crop_width
                            if new_width > self.get_width():
                                new_width = self.get_width()
                            new_height = item.get_height()
                            if new_height > self.get_height():
                                new_height = self.get_height()
                            subsurface_rect = Rect(crop_width, 0, new_width, new_height)
                            surface.blit(get_img_subsurface(item, subsurface_rect), (current_x + crop_width, current_y))
                            if subsurface_rect.is_hovered((current_x, current_y)):
                                self._item_being_hovered = key
                        # 换行
                        if item_has_been_dawn_on_this_line >= self.__item_per_line - 1:
                            current_x += self.distance_between_item + item.get_width()
                            current_y = int(self.abs_y + off_set[1] + self.panding)
                            item_has_been_dawn_on_this_line = 0
                        else:
                            current_y += self.distance_between_item + item.get_height()
                            item_has_been_dawn_on_this_line += 1
            # 处理总长宽
            if not self._mode:
                self.__surface_height = int(current_y - self.abs_y - off_set[1])
                if item_has_been_dawn_on_this_line > 0:
                    self.__surface_height += item.get_height()
                self.__surface_width = self.get_width()
            else:
                self.__surface_width = int(current_x - self.abs_x - off_set[0])
                if item_has_been_dawn_on_this_line > 0:
                    self.__surface_width += item.get_width()
                self.__surface_height = self.get_height()
            self.display_scrollbar(surface, off_set)
