from .image import *

# 基于ImageSurface的内部窗口
class AbstractFrame(AdvancedAbstractImageSurface):

    # 窗口上方bar的高度
    __bar_height: int = int(Display.get_height() * 0.02)
    # 窗口线条的粗细
    __outline_thickness: int = int(Display.get_height() * 0.002)
    # 放大指示图标
    __rescale_icon_0: StaticImage = None
    __rescale_icon_45: StaticImage = None
    __rescale_icon_90: StaticImage = None
    __rescale_icon_135: StaticImage = None

    def __init__(self, x: int_f, y: int_f, width: int_f, height: int_f, tag: str = ""):
        super().__init__(None, x, y, width, height, tag=tag)
        # 鼠标触碰bar时的相对坐标
        self.__mouse_hovered_offset_pos: tuple = tuple()
        # 放大方向
        self.__rescale_directions: dict[str, bool] = {"left": False, "right": False, "top": False, "bottom": False}
        # 是否重新放大窗口
        self.__if_regenerate_window: bool = True
        # 用于修改并展示内容的surface
        self._content_surface: ImageSurface = None
        # 是否需要更新用于展示内容的surface
        self._if_update_needed: bool = True
        #
        self.__if_move_local_pos: bool = False

    # 内容窗口的坐标
    @property
    def content_container_y(self) -> int:
        return self.y + self.__bar_height

    # 更新窗口
    def __update_window_frame(self) -> None:
        if self.__if_regenerate_window is True:
            self.img = new_surface(self.size)
            self.img.fill(Color.WHITE)
            draw_rect(self.img, Color.LIGHT_GRAY, ((0, 0), (self.get_width(), self.__bar_height)))
            draw_rect(self.img, Color.GRAY, self.img.get_rect(), self.__outline_thickness)
            if self.__rescale_icon_0 is None:
                self.__rescale_icon_0 = StaticImage(
                    "<!ui>rescale.png", 0, 0, self.__bar_height * 1.5, self.__bar_height * 1.5
                )
                self.__rescale_icon_45 = self.__rescale_icon_0.copy()
                self.__rescale_icon_45.rotate(45)
                self.__rescale_icon_45.scale_n_times(1.5)
                self.__rescale_icon_90 = self.__rescale_icon_0.copy()
                self.__rescale_icon_90.rotate(90)
                self.__rescale_icon_135 = self.__rescale_icon_0.copy()
                self.__rescale_icon_135.rotate(135)
                self.__rescale_icon_135.scale_n_times(1.5)
            self.__if_regenerate_window = False

    # 更新内容surface（子类必须实现该功能）
    def _update(self) -> None:
        EXCEPTION.fatal("_update()", 1)

    # 设置宽度
    def set_width(self, value: int_f) -> None:
        super().set_width(value)
        self.__if_regenerate_window = True
        self._if_update_needed = True

    # 设置高度
    def set_height(self, value: int_f) -> None:
        super().set_height(value)
        self.__if_regenerate_window = True
        self._if_update_needed = True

    # 角落是否被触碰
    def __is_corner_hovered(self, side1: str, side2: str = None) -> bool:
        if side2 is None:
            return bool(self.__rescale_directions[side1])
        else:
            return self.__rescale_directions[side1] is True and self.__rescale_directions[side2] is True

    # 是否内容窗口是任何事件被触发（默认为否，如果有需要可以在子类内重写）
    def _any_content_container_event(self) -> bool:
        return False

    # 展示
    def present_on(self, surface: ImageSurface) -> None:
        if not self.hidden:
            # 如果鼠标之前没有被按下
            if not Controller.mouse.get_pressed_previously(0):
                # 查看鼠标是否触碰窗口的边缘
                self.__rescale_directions["left"] = bool(
                    -self.__outline_thickness <= Controller.mouse.x - self.x < self.__outline_thickness * 2
                )
                self.__rescale_directions["right"] = bool(
                    -self.__outline_thickness * 2 < Controller.mouse.x - self.right <= self.__outline_thickness
                )
                self.__rescale_directions["top"] = bool(
                    -self.__outline_thickness <= Controller.mouse.y - self.y < self.__outline_thickness * 2
                )
                self.__rescale_directions["bottom"] = bool(
                    -self.__outline_thickness * 2 < Controller.mouse.y - self.bottom <= self.__outline_thickness
                )
                # 如果鼠标按住bar
                if (
                    True not in self.__rescale_directions.values()
                    and Controller.mouse.get_pressed(0)
                    and not self._any_content_container_event()
                ):
                    if is_hover(new_rect((self.x, self.y), (self.get_width(), self.__bar_height))):
                        self.__mouse_hovered_offset_pos = Pos.subtract(Controller.mouse.get_pos(), self.pos)
                    elif self.is_hovered():
                        self.__if_move_local_pos = True
                        self.__mouse_hovered_offset_pos = Pos.subtract(Controller.mouse.get_pos(), self.local_pos)
            elif Controller.mouse.get_pressed(0):
                # 根据鼠标位置修改本地坐标
                if self.__if_move_local_pos is True:
                    self.locally_move_to(Pos.subtract(Controller.mouse.get_pos(), self.__mouse_hovered_offset_pos))

                # 移动窗口
                elif len(self.__mouse_hovered_offset_pos) > 0:
                    self.move_to(Pos.subtract(Controller.mouse.get_pos(), self.__mouse_hovered_offset_pos))
                else:
                    # 向左放大
                    if self.__rescale_directions["left"] is True:
                        if Controller.mouse.x < self.right:
                            self.set_width(self.right - Controller.mouse.x)
                            self.set_left(Controller.mouse.x)
                        else:
                            self.__rescale_directions["left"] = False
                            self.__rescale_directions["right"] = True
                    # 向右放大
                    if self.__rescale_directions["right"] is True:
                        if Controller.mouse.x > self.left:
                            self.set_width(Controller.mouse.x - self.left)
                        else:
                            self.__rescale_directions["right"] = False
                            self.__rescale_directions["left"] = True
                    # 向上放大
                    if self.__rescale_directions["top"] is True:
                        if Controller.mouse.y < self.bottom - self.__bar_height:
                            self.set_height(self.bottom - Controller.mouse.y)
                            self.set_top(Controller.mouse.y)
                        else:
                            self.__rescale_directions["top"] = False
                            self.__rescale_directions["bottom"] = True
                    # 向下放大
                    if self.__rescale_directions["bottom"] is True:
                        if Controller.mouse.y > self.top:
                            self.set_height(Controller.mouse.y - self.top)
                        else:
                            self.__rescale_directions["bottom"] = False
                            self.__rescale_directions["top"] = True
            else:
                for key in self.__rescale_directions:
                    self.__rescale_directions[key] = False
                self.__mouse_hovered_offset_pos = tuple()
                self.__if_move_local_pos = False
            # 更新窗口
            self.__update_window_frame()
            # 画出窗口
            surface.blit(self.img, self.pos)
            # 如果需要，则先更新内容surface
            if self._if_update_needed is True:
                self._update()
            # 画出内容
            if self._content_surface is not None:
                # 计算坐标
                abs_pos_x: int = self.x + self.__outline_thickness
                abs_pos_y: int = self.content_container_y + self.__outline_thickness
                real_local_x: int = 0
                real_local_y: int = 0
                if self.local_x < 0:
                    abs_pos_x -= self.local_x
                else:
                    real_local_x = self.local_x
                if self.local_y < 0:
                    abs_pos_y -= self.local_y
                else:
                    real_local_y = self.local_y
                # 计算尺寸
                width_of_sub: int = keep_in_range(
                    self.get_width() - self.__outline_thickness + self.local_x,
                    0,
                    min(self._content_surface.get_width() - real_local_x, self.get_width() - self.__outline_thickness),
                )
                height_of_sub: int = keep_in_range(
                    self.get_height() - self.__bar_height - self.__outline_thickness + self.local_y,
                    0,
                    min(
                        self._content_surface.get_height() - real_local_y,
                        self.get_height() - self.__bar_height - self.__outline_thickness,
                    ),
                )
                # 展示内容
                if width_of_sub > 0 and height_of_sub > 0:
                    surface.blit(
                        get_img_subsurface(self._content_surface, (real_local_x, real_local_y, width_of_sub, height_of_sub)),
                        (abs_pos_x, abs_pos_y),
                    )
            # 画出放大icon
            if True in self.__rescale_directions.values():
                # 如果鼠标触碰了边框，则旋转放大icon至对应角度
                if self.__is_corner_hovered("top", "right") or self.__is_corner_hovered("bottom", "left"):
                    rescale_icon = self.__rescale_icon_45
                elif self.__is_corner_hovered("top", "left") or self.__is_corner_hovered("bottom", "right"):
                    rescale_icon = self.__rescale_icon_135
                elif self.__is_corner_hovered("top") or self.__is_corner_hovered("bottom"):
                    rescale_icon = self.__rescale_icon_90
                else:
                    rescale_icon = self.__rescale_icon_0
                rescale_icon.set_center(Controller.mouse.x, Controller.mouse.y)
                rescale_icon.draw(surface)
