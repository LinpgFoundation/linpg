from .menu import *


# 翻页指示动态图标数据管理模块
class NextPageIndicatorIcon:
    def __init__(self) -> None:
        self.__status: bool = False
        self.__x_offset: float = 0
        self.__y_offset: float = 0

    def draw_to(self, _surface: ImageSurface, _x: int, _y: int, _width: int) -> None:
        # 更新坐标数值
        if not self.__status:
            self.__x_offset += Display.get_delta_time() / 30
            self.__y_offset += Display.get_delta_time() / 20
            if self.__y_offset >= _width / 2:
                self.__status = True
        else:
            self.__x_offset -= Display.get_delta_time() / 30
            self.__y_offset -= Display.get_delta_time() / 20
            if self.__y_offset <= 0:
                self.__status = False
        final_y: int = int(_y + self.__y_offset)
        # 渲染
        Draw.polygon(
            _surface,
            Colors.WHITE,
            (
                (_x + int(self.__x_offset), final_y),
                (_x + _width - int(self.__x_offset), final_y),
                (_x + _width // 2, final_y + _width),
            ),
        )
