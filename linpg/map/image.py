from ..dialog import *

# 地图图片参数管理模块
class MapImageParameters:

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
    def set_block_size(cls, _width: int, _height: int) -> None:
        cls.__BLOCK_WIDTH = _width
        cls.__BLOCK_HEIGHT = _height

    # 获取方块宽度
    @classmethod
    def get_block_width(cls) -> int:
        return cls.__BLOCK_WIDTH

    # 获取方块高度
    @classmethod
    def get_block_height(cls) -> int:
        return cls.__BLOCK_HEIGHT


# 装饰物的图片管理模块
class DecorationImagesModule:

    # 引擎自带的场景装饰物
    DEFAULT_DECORATION_IMAGE_SPRITE_SHEET: Optional[SpriteImage] = None
    # 项目自带的场景装饰物
    CUSTOM_DECORATION_IMAGE_SPRITE_SHEET: Optional[SpriteImage] = None
    # 经过处理的场景装饰物
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
        # 如果SPRITE SHEET未被初始化，则初始化
        if cls.DEFAULT_DECORATION_IMAGE_SPRITE_SHEET is None:
            cls.DEFAULT_DECORATION_IMAGE_SPRITE_SHEET = SpriteImage(
                "<!env>decoration.png"
                if os.path.exists(Images.generate_path_according_to_prefix("<!env>decoration.png"))
                else "<NULL>"
            )
        if cls.CUSTOM_DECORATION_IMAGE_SPRITE_SHEET is None:
            # 确认自带的sheet存在; 如果不存在，则加载一个空的sheet
            cls.CUSTOM_DECORATION_IMAGE_SPRITE_SHEET = SpriteImage(
                "<@env>decoration.png"
                if os.path.exists(Images.generate_path_according_to_prefix("<@env>decoration.png"))
                else "<NULL>"
            )
        # 从sheet中读取装饰物图片
        _img: Union[ImageSurface, tuple]
        if cls.DEFAULT_DECORATION_IMAGE_SPRITE_SHEET.contain(fileName):
            _img = cls.DEFAULT_DECORATION_IMAGE_SPRITE_SHEET.get(fileName)
        elif cls.CUSTOM_DECORATION_IMAGE_SPRITE_SHEET.contain(fileName):
            _img = cls.CUSTOM_DECORATION_IMAGE_SPRITE_SHEET.get(fileName)
        else:
            EXCEPTION.fatal('Cannot find decoration image "{}"'.format(fileName))
        # 常规的独立图片
        if not isinstance(_img, tuple):
            # 最后确认一下是不是需要加载
            if fileName not in cls.__DECORATION_IMAGE_DICT[decorationType]:
                # 生成图片
                cls.__DECORATION_IMAGE_DICT[decorationType][fileName] = StaticImage(_img, 0, 0)
            # 如果是夜战模式
            if MapImageParameters.get_darkness() > 0:
                if decorationType not in cls.__DECORATION_IMAGE_DICT_DARK:
                    cls.__DECORATION_IMAGE_DICT_DARK[decorationType] = {}
                if fileName not in cls.__DECORATION_IMAGE_DICT_DARK[decorationType]:
                    cls.__DECORATION_IMAGE_DICT_DARK[decorationType][fileName] = cls.__DECORATION_IMAGE_DICT[decorationType][
                        fileName
                    ].copy()
                    cls.__DECORATION_IMAGE_DICT_DARK[decorationType][fileName].add_darkness(MapImageParameters.get_darkness())
        # 类Gif形式，decorationType应该与fileName一致
        else:
            cls.__DECORATION_IMAGE_DICT[decorationType] = [StaticImage(each_img, 0, 0) for each_img in _img]
            if MapImageParameters.get_darkness() > 0:
                cls.__DECORATION_IMAGE_DICT_DARK[decorationType] = []
                for key in cls.__DECORATION_IMAGE_DICT[decorationType]:
                    _img_clone = key.copy()
                    _img_clone.add_darkness(MapImageParameters.get_darkness())
                    cls.__DECORATION_IMAGE_DICT_DARK[decorationType].append(_img_clone)

    # 获取图片
    @classmethod
    def get_image(cls, decorationType: str, key: strint, darkMode: bool) -> Any:
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
            if isinstance(key, int):
                key = decorationType
            cls.add_image(decorationType, key)
            return (
                cls.__DECORATION_IMAGE_DICT_DARK[decorationType][key]
                if darkMode is True
                else cls.__DECORATION_IMAGE_DICT[decorationType][key]
            )


# 地图贴图的管理模块
class TileMapImagesModule:

    # 引擎自带的地图贴图
    DEFAULT_TILE_MAP_IMAGE_SPRITE_SHEET: Optional[SpriteImage] = None
    # 环境
    __ENV_IMAGE_DICT: dict[str, StaticImage] = {}
    __ENV_IMAGE_DICT_DARK: dict[str, StaticImage] = {}

    # 调整尺寸
    @classmethod
    def update_size(cls, _width: int, _height: int) -> None:
        # 更新尺寸
        MapImageParameters.set_block_size(_width, _height)
        # 调整地图方块尺寸
        for key in cls.__ENV_IMAGE_DICT:
            cls.__ENV_IMAGE_DICT[key].set_width_with_original_image_size_locked(MapImageParameters.get_block_width())
        # 调整黑夜模式下的地图方块尺寸
        for key in cls.__ENV_IMAGE_DICT_DARK:
            cls.__ENV_IMAGE_DICT_DARK[key].set_width_with_original_image_size_locked(MapImageParameters.get_block_width())

    # 加载图片
    @classmethod
    def add_image(cls, fileName: str) -> None:
        if cls.DEFAULT_TILE_MAP_IMAGE_SPRITE_SHEET is None:
            cls.DEFAULT_TILE_MAP_IMAGE_SPRITE_SHEET = SpriteImage(
                "<!env>block.png" if os.path.exists(Images.generate_path_according_to_prefix("<!env>block.png")) else "<NULL>"
            )
        if cls.DEFAULT_TILE_MAP_IMAGE_SPRITE_SHEET.contain(fileName):
            if fileName not in cls.__ENV_IMAGE_DICT:
                _img: Union[ImageSurface, tuple] = cls.DEFAULT_TILE_MAP_IMAGE_SPRITE_SHEET.get(fileName)
                if isinstance(_img, tuple):
                    EXCEPTION.fatal("Images for tile map cannot be groupped as a collection")
                cls.__ENV_IMAGE_DICT[fileName] = StaticImage(_img, 0, 0)
                cls.__ENV_IMAGE_DICT[fileName].set_width_with_original_image_size_locked(MapImageParameters.get_block_width())
            # 如果是夜战模式
            if MapImageParameters.get_darkness() > 0:
                cls.__ENV_IMAGE_DICT_DARK[fileName] = cls.__ENV_IMAGE_DICT[fileName].copy()
                cls.__ENV_IMAGE_DICT_DARK[fileName].add_darkness(MapImageParameters.get_darkness())
        else:
            EXCEPTION.fatal('Cannot find image "{}" in folder'.format(fileName))

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
