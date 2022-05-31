from .image import *

# 角色被察觉和警觉的图标管理模块
class FriendlyCharacterDynamicProgressBarSurface(DynamicProgressBarSurface):

    # 指向储存角色被察觉图标的指针
    __FULLY_EXPOSED_IMG: ImageSurface = Surfaces.NULL
    __BEING_NOTICED_IMG: ImageSurface = Surfaces.NULL
    __img_initialized: bool = False

    def __init__(self) -> None:
        # 检测图标是否生成，如果没有则生成
        if not self.__img_initialized:
            self.__FULLY_EXPOSED_IMG = Images.quickly_load("<&ui>eye_red.png")
            self.__BEING_NOTICED_IMG = Images.quickly_load("<&ui>eye_orange.png")
            # 完成初始化
            self.__img_initialized = True
        super().__init__(self.__FULLY_EXPOSED_IMG, self.__BEING_NOTICED_IMG, 0, 0, 0, 0)


class HostileCharacterDynamicProgressBarSurface(DynamicProgressBarSurface):

    # 指向储存敌方角色警觉程度图标的指针
    __ORANGE_VIGILANCE_IMG: ImageSurface = Surfaces.NULL
    __RED_VIGILANCE_IMG: ImageSurface = Surfaces.NULL
    __img_initialized: bool = False

    def __init__(self) -> None:
        # 检测图标是否生成，如果没有则生成
        if not self.__img_initialized:
            self.__ORANGE_VIGILANCE_IMG = Images.quickly_load("<&ui>vigilance_orange.png")
            self.__RED_VIGILANCE_IMG = Images.quickly_load("<&ui>vigilance_red.png")
            # 完成初始化
            self.__img_initialized = True
        super().__init__(self.__RED_VIGILANCE_IMG, self.__ORANGE_VIGILANCE_IMG, 0, 0, 0, 0, "vertical")


# 角色血条图片管理模块
class EntityHpBar(DynamicProgressBarSurface):

    # 指向储存血条图片的指针（不初始化直到Entity或其子类被调用）
    __HP_GREEN_IMG: ImageSurface = Surfaces.NULL
    __HP_RED_IMG: ImageSurface = Surfaces.NULL
    __HP_EMPTY_IMG: ImageSurface = Surfaces.NULL
    __img_initialized: bool = False

    def __init__(self) -> None:
        # 检测被察觉的图标是否生产，如果没有则生成
        if not self.__img_initialized:
            self.__HP_GREEN_IMG = Images.quickly_load("<&ui>hp_green.png")
            self.__HP_RED_IMG = Images.quickly_load("<&ui>hp_red.png")
            self.__HP_EMPTY_IMG = Images.quickly_load("<&ui>hp_empty.png")
            # 完成初始化
            self.__img_initialized = True
        # 是否角色死亡
        self.__is_dying: bool = False
        # 初始化父类
        super().__init__(self.__HP_GREEN_IMG, self.__HP_EMPTY_IMG, 0, 0, 0, 0)

    # 获取上方图片
    def _get_img_on_top(self) -> ImageSurface:
        return super()._get_img_on_top() if not self.__is_dying else self.__HP_RED_IMG

    def set_dying(self, value: bool) -> None:
        self.__is_dying = value
