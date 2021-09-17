from ..dialog import *
import numpy

# 地图场景模块
class EnvImagesManagement:
    def __init__(self):
        # 背景图层
        self.__BACKGROUND_SURFACE: object = None
        self.__MAP_SURFACE: object = None
        # 方块尺寸
        self.__BLOCK_WIDTH: int = 0
        self.__BLOCK_HEIGHT: int = 0
        # 环境
        self.__ENV_IMAGE_DICT: dict = {}
        self.__ENV_IMAGE_DICT_DARK: dict = {}
        # 场景装饰物
        self.__DECORATION_IMAGE_DICT: dict = {}
        self.__DECORATION_IMAGE_DICT_DARK: dict = {}
        # 背景图片
        self.__BACKGROUND_IMAGE_PATH: str = "Assets/image/dialog_background"
        # 暗度（仅黑夜场景有效，为0时视为白天）
        self.__DARKNESS: int = 0

    # 更新数据
    def update(
        self,
        theMap: numpy.ndarray,
        decorationData: numpy.ndarray,
        bgImgName: str,
        blockSize: tuple,
        darkMode: bool,
        darkness: int = 150,
    ):
        # 环境
        self.__ENV_IMAGE_DICT.clear()
        self.__ENV_IMAGE_DICT_DARK.clear()
        # 场景装饰物
        self.__DECORATION_IMAGE_DICT.clear()
        self.__DECORATION_IMAGE_DICT_DARK.clear()
        # 背景图片
        self.__BACKGROUND_IMAGE: ImageSurface = (
            IMG.quickly_load(os.path.join(self.__BACKGROUND_IMAGE_PATH, bgImgName), False).convert()
            if bgImgName is not None
            else None
        )
        # 更新尺寸
        self.__BLOCK_WIDTH = round(blockSize[0])
        self.__BLOCK_HEIGHT = round(blockSize[1])
        # 暗度（仅黑夜场景有效）
        if darkMode is True:
            if darkness > 0:
                self.__DARKNESS = darkness
            else:
                EXCEPTION.fatal("Darkness needs to be greater than 0, not {}".format(darkness))
        else:
            self.__DARKNESS = 0
        # 确认场景需要用到素材
        all_images_needed: list = []
        for y in range(len(theMap)):
            for x in range(len(theMap[y])):
                if theMap[y][x].name not in all_images_needed:
                    all_images_needed.append(theMap[y][x].name)
        # 加载图片
        for fileName in all_images_needed:
            self.__add_evn_image(fileName)
        for decoration in decorationData:
            self.__add_decoration_image(decoration.type, decoration.image)

    # 加载环境图片
    def __add_evn_image(self, fileName: str) -> None:
        imgPath: str = os.path.join(ASSET.get_internal_environment_image_path("block"), "{}.png".format(fileName))
        if os.path.exists(imgPath):
            self.__ENV_IMAGE_DICT[fileName] = StaticImage(imgPath, 0, 0)
            self.__ENV_IMAGE_DICT[fileName].set_width_with_size_locked(self.__BLOCK_WIDTH)
            # 如果是夜战模式
            if self.__DARKNESS > 0:
                self.__ENV_IMAGE_DICT_DARK[fileName] = self.__ENV_IMAGE_DICT[fileName].copy()
                self.__ENV_IMAGE_DICT_DARK[fileName].add_darkness(self.__DARKNESS)
        else:
            EXCEPTION.fatal(
                'Cannot find image "{0}" in folder "{1}"'.format(
                    fileName, ASSET.get_internal_environment_image_path("block")
                )
            )

    # 加载场景装饰物图片
    def __add_decoration_image(self, decorationType: str, fileName: str) -> None:
        imgPath: str
        # 如果是未被加载过的类型
        if decorationType not in self.__DECORATION_IMAGE_DICT:
            self.__DECORATION_IMAGE_DICT[decorationType] = {}
        # 常规装饰物
        if os.path.exists(
            (imgPath := os.path.join(ASSET.get_internal_environment_image_path("decoration"), "{}.png".format(fileName)))
        ):
            # 最后确认一下是不是需要加载
            if fileName not in self.__DECORATION_IMAGE_DICT[decorationType]:
                # 生成图片
                self.__DECORATION_IMAGE_DICT[decorationType][fileName] = StaticImage(imgPath, 0, 0)
                # 如果是夜战模式
                if self.__DARKNESS > 0:
                    if decorationType not in self.__DECORATION_IMAGE_DICT_DARK:
                        self.__DECORATION_IMAGE_DICT_DARK[decorationType] = {}
                    self.__DECORATION_IMAGE_DICT_DARK[decorationType][fileName] = self.__DECORATION_IMAGE_DICT[
                        decorationType
                    ][fileName].copy()
                    self.__DECORATION_IMAGE_DICT_DARK[decorationType][fileName].add_darkness(self.__DARKNESS)
        # 类Gif形式，decorationType应该与fileName一致
        elif os.path.exists(
            (imgPath := os.path.join(ASSET.get_internal_environment_image_path("decoration"), decorationType))
        ):
            for img_path in glob(os.path.join(imgPath, "*.png")):
                self.__DECORATION_IMAGE_DICT[decorationType][os.path.basename(img_path).replace(".png", "")] = StaticImage(
                    img_path, 0, 0
                )
            if self.__DARKNESS > 0:
                self.__DECORATION_IMAGE_DICT_DARK[decorationType] = {}
                for key in self.__DECORATION_IMAGE_DICT[decorationType]:
                    self.__DECORATION_IMAGE_DICT_DARK[decorationType][key] = self.__DECORATION_IMAGE_DICT[decorationType][
                        key
                    ].copy()
                    self.__DECORATION_IMAGE_DICT_DARK[decorationType][key].add_darkness(self.__DARKNESS)
        else:
            EXCEPTION.fatal(
                'Cannot find image "{0}" in folder "{1}"'.format(
                    fileName, ASSET.get_internal_environment_image_path("decoration")
                )
            )

    # 获取方块尺寸
    def get_block_width(self) -> int:
        return self.__BLOCK_WIDTH

    def get_block_height(self) -> int:
        return self.__BLOCK_HEIGHT

    # 调整尺寸
    def set_block_size(self, newWidth: number, newHeight: number) -> None:
        self.__BLOCK_WIDTH = round(newWidth)
        self.__BLOCK_HEIGHT = round(newHeight)
        # 调整地图方块尺寸
        for key in self.__ENV_IMAGE_DICT:
            self.__ENV_IMAGE_DICT[key].set_width_with_size_locked(self.__BLOCK_WIDTH)
        # 如果是黑夜模式，则应该调整黑夜模式下的地图方块尺寸
        if self.__DARKNESS > 0:
            for key in self.__ENV_IMAGE_DICT_DARK:
                self.__ENV_IMAGE_DICT_DARK[key].set_width_with_size_locked(self.__BLOCK_WIDTH)

    def get_env_image(self, key: str, darkMode: bool) -> StaticImage:
        try:
            return self.__ENV_IMAGE_DICT_DARK[key] if darkMode is True else self.__ENV_IMAGE_DICT[key]
        except Exception:
            EXCEPTION.inform(
                "Cannot find block image '{}', we will try to load it for you right now, but please by aware.".format(key)
            )
            self.__add_evn_image(key)
            return self.__ENV_IMAGE_DICT_DARK[key] if darkMode is True else self.__ENV_IMAGE_DICT[key]

    def get_decoration_image(self, decorationType: str, key: strint, darkMode: bool) -> any:
        try:
            return (
                self.__DECORATION_IMAGE_DICT_DARK[decorationType][key]
                if darkMode is True
                else self.__DECORATION_IMAGE_DICT[decorationType][key]
            )
        # 如果图片没找到
        except Exception:
            EXCEPTION.inform(
                "Cannot find decoration image '{0}' in type '{1}', we will try to load it for you right now, but please by aware.".format(
                    key, decorationType
                )
            )
            self.__add_decoration_image(decorationType, key)
            return (
                self.__DECORATION_IMAGE_DICT_DARK[decorationType][key]
                if darkMode is True
                else self.__DECORATION_IMAGE_DICT[decorationType][key]
            )

    # 获取当前装饰物种类的数量
    def get_decoration_num(self, decorationType: str) -> int:
        return len(self.__DECORATION_IMAGE_DICT[decorationType])

    # 新图层
    def new_surface(self, screen_size: tuple, map_size: tuple) -> None:
        self.__BACKGROUND_SURFACE = (
            IMG.resize(self.__BACKGROUND_IMAGE, screen_size)
            if self.__BACKGROUND_IMAGE is not None
            else new_surface(screen_size).convert()
        )
        if self.__MAP_SURFACE is not None:
            self.__MAP_SURFACE.fill(Color.TRANSPARENT)
        else:
            self.__MAP_SURFACE = new_transparent_surface(map_size)

    # 获取图层
    def get_surface(self) -> ImageSurface:
        return self.__MAP_SURFACE

    # 画出地图
    def display_background_surface(self, screen: ImageSurface, pos: tuple) -> None:
        screen.blits(((self.__BACKGROUND_SURFACE, (0, 0)), (self.__MAP_SURFACE, pos)))


# 地图场景图片管理
MAP_ENV_IMAGE: object = EnvImagesManagement()
