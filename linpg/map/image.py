from ..dialog import *

# 基础的图片管理模块
class AbstractMapImagesModule:

    # 方块尺寸
    __BLOCK_WIDTH: int = 0
    __BLOCK_HEIGHT: int = 0
    # 暗度（仅黑夜场景有效，为0时视为白天）
    __DARKNESS: int = 0

    @classmethod
    def get_darkness(cls) -> int:
        return cls.__DARKNESS

    @classmethod
    def set_darkness(cls, value: int) -> None:
        cls.__DARKNESS = value

    # 调整尺寸
    @classmethod
    def set_block_size(cls, newWidth: int, newHeight: int) -> None:
        cls.__BLOCK_WIDTH = newWidth
        cls.__BLOCK_HEIGHT = newHeight

    # 获取方块宽度
    @classmethod
    def get_block_width(cls) -> int:
        return cls.__BLOCK_WIDTH

    # 获取方块高度
    @classmethod
    def get_block_height(cls) -> int:
        return cls.__BLOCK_HEIGHT


# 装饰物的图片管理模块
class DecorationImagesModule(AbstractMapImagesModule):

    # 场景装饰物
    __DECORATION_IMAGE_DICT: dict = {}
    __DECORATION_IMAGE_DICT_DARK: dict = {}

    # 获取当前装饰物种类的数量
    @classmethod
    def get_image_num(cls, decorationType: str) -> int:
        return len(cls.__DECORATION_IMAGE_DICT[decorationType])

    # 加载场景装饰物图片
    @classmethod
    def add_image(cls, decorationType: str, fileName: str) -> None:
        # 如果是未被加载过的类型
        if decorationType not in cls.__DECORATION_IMAGE_DICT:
            cls.__DECORATION_IMAGE_DICT[decorationType] = {}
        imgPath: str
        # 常规装饰物
        if os.path.exists(
            (imgPath := os.path.join(ASSET.get_internal_environment_image_path("decoration"), "{}.png".format(fileName)))
        ):
            # 最后确认一下是不是需要加载
            if fileName not in cls.__DECORATION_IMAGE_DICT[decorationType]:
                # 生成图片
                cls.__DECORATION_IMAGE_DICT[decorationType][fileName] = StaticImage(imgPath, 0, 0)
            # 如果是夜战模式
            if cls.get_darkness() > 0:
                if decorationType not in cls.__DECORATION_IMAGE_DICT_DARK:
                    cls.__DECORATION_IMAGE_DICT_DARK[decorationType] = {}
                if fileName not in cls.__DECORATION_IMAGE_DICT_DARK[decorationType]:
                    cls.__DECORATION_IMAGE_DICT_DARK[decorationType][fileName] = cls.__DECORATION_IMAGE_DICT[decorationType][
                        fileName
                    ].copy()
                    cls.__DECORATION_IMAGE_DICT_DARK[decorationType][fileName].add_darkness(cls.get_darkness())
        # 类Gif形式，decorationType应该与fileName一致
        elif os.path.exists((imgPath := os.path.join(ASSET.get_internal_environment_image_path("decoration"), decorationType))):
            for img_path in glob(os.path.join(imgPath, "*.png")):
                cls.__DECORATION_IMAGE_DICT[decorationType][os.path.basename(img_path).removesuffix(".png")] = StaticImage(
                    img_path, 0, 0
                )
            if cls.get_darkness() > 0:
                cls.__DECORATION_IMAGE_DICT_DARK[decorationType] = {}
                for key in cls.__DECORATION_IMAGE_DICT[decorationType]:
                    cls.__DECORATION_IMAGE_DICT_DARK[decorationType][key] = cls.__DECORATION_IMAGE_DICT[decorationType][
                        key
                    ].copy()
                    cls.__DECORATION_IMAGE_DICT_DARK[decorationType][key].add_darkness(cls.get_darkness())
        else:
            EXCEPTION.fatal(
                'Cannot find image "{0}" in folder "{1}"'.format(
                    fileName, ASSET.get_internal_environment_image_path("decoration")
                )
            )

    # 获取图片
    @classmethod
    def get_image(cls, decorationType: str, key: str, darkMode: bool) -> Any:
        try:
            return (
                cls.__DECORATION_IMAGE_DICT_DARK[decorationType][key]
                if darkMode is True
                else cls.__DECORATION_IMAGE_DICT[decorationType][key]
            )
        # 如果图片没找到
        except Exception:
            EXCEPTION.inform(
                "Cannot find decoration image '{0}' in type '{1}', we will try to load it for you right now, but please by aware.".format(
                    key, decorationType
                )
            )
            cls.add_image(decorationType, key)
            return (
                cls.__DECORATION_IMAGE_DICT_DARK[decorationType][key]
                if darkMode is True
                else cls.__DECORATION_IMAGE_DICT[decorationType][key]
            )


# 地图贴图的管理模块
class TileMapImagesModule(AbstractMapImagesModule):

    # 环境
    __ENV_IMAGE_DICT: dict[str, StaticImage] = {}
    __ENV_IMAGE_DICT_DARK: dict[str, StaticImage] = {}

    # 调整尺寸
    @classmethod
    def update_size(cls) -> None:
        # 调整地图方块尺寸
        for key in cls.__ENV_IMAGE_DICT:
            cls.__ENV_IMAGE_DICT[key].set_width_with_original_image_size_locked(cls.get_block_width())
        # 调整黑夜模式下的地图方块尺寸
        for key in cls.__ENV_IMAGE_DICT_DARK:
            cls.__ENV_IMAGE_DICT_DARK[key].set_width_with_original_image_size_locked(cls.get_block_width())

    # 加载图片
    @classmethod
    def add_image(cls, fileName: str) -> None:
        imgPath: str = os.path.join(ASSET.get_internal_environment_image_path("block"), "{}.png".format(fileName))
        if os.path.exists(imgPath):
            if fileName not in cls.__ENV_IMAGE_DICT:
                cls.__ENV_IMAGE_DICT[fileName] = StaticImage(imgPath, 0, 0)
                cls.__ENV_IMAGE_DICT[fileName].set_width_with_original_image_size_locked(cls.get_block_width())
            # 如果是夜战模式
            if cls.get_darkness() > 0:
                cls.__ENV_IMAGE_DICT_DARK[fileName] = cls.__ENV_IMAGE_DICT[fileName].copy()
                cls.__ENV_IMAGE_DICT_DARK[fileName].add_darkness(cls.get_darkness())
        else:
            EXCEPTION.fatal(
                'Cannot find image "{0}" in folder "{1}"'.format(fileName, ASSET.get_internal_environment_image_path("block"))
            )

    # 获取图片
    @classmethod
    def get_image(cls, key: str, darkMode: bool) -> StaticImage:
        try:
            return cls.__ENV_IMAGE_DICT_DARK[key] if darkMode is True else cls.__ENV_IMAGE_DICT[key]
        except Exception:
            EXCEPTION.inform(
                "Cannot find block image '{}', we will try to load it for you right now, but please by aware.".format(key)
            )
            cls.add_image(key)
            return cls.__ENV_IMAGE_DICT_DARK[key] if darkMode is True else cls.__ENV_IMAGE_DICT[key]
