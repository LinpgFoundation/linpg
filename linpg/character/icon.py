from .image import *

# 角色被察觉和警觉的图标管理模块
class EntityDynamicProgressBarSurface(DynamicProgressBarSurface):

    # 指向储存角色被察觉和警觉的图标的指针
    __BEING_NOTICED_IMG: ImageSurface = None
    __FULLY_EXPOSED_IMG: ImageSurface = None
    __ORANGE_VIGILANCE_IMG: ImageSurface = None
    __RED_VIGILANCE_IMG: ImageSurface = None

    def __init__(self, mode: str = "horizontal"):
        super().__init__(None, None, 0, 0, 0, 0, mode)
        # 检测被察觉的图标是否生产，如果没有则生成
        # 被察觉图标
        if self.__BEING_NOTICED_IMG is None:
            self.__BEING_NOTICED_IMG = IMG.quickly_load(r"Assets/image/UI/eye_orange.png")
        if self.__FULLY_EXPOSED_IMG is None:
            self.__FULLY_EXPOSED_IMG = IMG.quickly_load(r"Assets/image/UI/eye_red.png")
        # 警觉图标
        if self.__ORANGE_VIGILANCE_IMG is None:
            self.__ORANGE_VIGILANCE_IMG = IMG.quickly_load(r"Assets/image/UI/vigilance_orange.png")
        if self.__RED_VIGILANCE_IMG is None:
            self.__RED_VIGILANCE_IMG = IMG.quickly_load(r"Assets/image/UI/vigilance_red.png")

    def draw(self, surface: ImageSurface, isFriendlyCharacter: bool = True) -> None:
        if not isFriendlyCharacter:
            self._draw_bar(surface, self.__RED_VIGILANCE_IMG, self.__ORANGE_VIGILANCE_IMG, self.pos)
        else:
            self._draw_bar(surface, self.__FULLY_EXPOSED_IMG, self.__BEING_NOTICED_IMG, self.pos)


# 角色血条图片管理模块
class EntityHpBar(DynamicProgressBarSurface):

    # 指向储存血条图片的指针（不初始化直到Entity或其子类被调用）
    __HP_GREEN_IMG: ImageSurface = None
    __HP_RED_IMG: ImageSurface = None
    __HP_EMPTY_IMG: ImageSurface = None

    def __init__(self) -> None:
        super().__init__(None, None, 0, 0, 0, 0)
        # 检测被察觉的图标是否生产，如果没有则生成
        if self.__HP_GREEN_IMG is None:
            self.__HP_GREEN_IMG = IMG.quickly_load(r"Assets/image/UI/hp_green.png")
        if self.__HP_RED_IMG is None:
            self.__HP_RED_IMG = IMG.quickly_load(r"Assets/image/UI/hp_red.png")
        if self.__HP_EMPTY_IMG is None:
            self.__HP_EMPTY_IMG = IMG.quickly_load(r"Assets/image/UI/hp_empty.png")

    def draw(self, surface: ImageSurface, isDying: bool) -> None:
        self._draw_bar(surface, self.__HP_GREEN_IMG if not isDying else self.__HP_RED_IMG, self.__HP_EMPTY_IMG, self.pos)
