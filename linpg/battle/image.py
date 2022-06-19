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


# 管理单个动作所有对应图片的模块
class _EntityImagesCollection:
    def __init__(
        self, imagesList: tuple[StaticImage, ...], crop_size: list[int], offset: list[int], original_img_size: list[int]
    ) -> None:
        self.__images: tuple[StaticImage, ...] = imagesList
        self.__current_image_pointer: StaticImage = self.__images[0]
        self.__width: number = 0
        self.__height: number = 0
        self.__cropped_image_width: int = crop_size[0]
        self.__cropped_image_height: int = crop_size[1]
        self.__left_offset_x: int = offset[0]
        self.__offset_y: int = offset[1]
        self.__real_width: int = original_img_size[0]
        self.__real_height: int = original_img_size[1]
        self.__right_offset_x: int = self.__real_width - self.__cropped_image_width - self.__left_offset_x

    def __len__(self) -> int:
        return len(self.__images)

    # 获取指定index的图片
    def get_image(self, index: int) -> StaticImage:
        return self.__images[index]

    # 设置尺寸
    def set_size(self, width: number, height: number) -> None:
        self.__width = width * self.__cropped_image_width / self.__real_width
        self.__height = height * self.__cropped_image_height / self.__real_height

    # 设置要播放图片的index
    def set_index(self, index: int) -> None:
        self.__current_image_pointer = self.__images[index]

    # 反转所有列表内的图片
    def flip_all(self) -> None:
        for _image in self.__images:
            _image.flip_original_img()
        temp: int = self.__right_offset_x
        self.__right_offset_x = self.__left_offset_x
        self.__left_offset_x = temp

    # 获取当前图片的rect
    def get_rectangle(self) -> Rectangle:
        return self.__current_image_pointer.get_rectangle()

    # 展示
    def draw_onto(self, surface: ImageSurface, alpha: int, ifFlip: bool, pos: tuple, draw_outline: bool) -> None:
        self.__current_image_pointer.set_size(self.__width, self.__height)
        self.__current_image_pointer.set_alpha(alpha)  # 翻转图片
        self.__current_image_pointer.set_top(self.__offset_y * self.__height / self.__cropped_image_height + pos[1])
        if ifFlip:
            self.__current_image_pointer.flip_if_not()
            self.__current_image_pointer.set_left(self.__right_offset_x * self.__width / self.__cropped_image_width + pos[0])
        else:
            self.__current_image_pointer.flip_back_to_normal()
            self.__current_image_pointer.set_left(self.__left_offset_x * self.__width / self.__cropped_image_width + pos[0])
        self.__current_image_pointer.draw(surface)
        if draw_outline is True:
            self.__current_image_pointer.draw_outline(surface)


# 角色图片管理模块
class EntitySpriteImageManager:

    # 用于存放角色图片的字典
    __CHARACTERS_IMAGES: dict[str, dict[str, _EntityImagesCollection]] = {}
    # 角色图片文件夹路径
    SPRITES_PATH: str = Specification.get_directory("sprite")

    # 获取图片
    @classmethod
    def get_images(cls, characterType: str, action: str) -> _EntityImagesCollection:
        return cls.__CHARACTERS_IMAGES[characterType][action]

    # 尝试获取图片
    @classmethod
    def try_get_images(cls, faction: str, characterType: str, action: str) -> _EntityImagesCollection:
        if characterType not in cls.__CHARACTERS_IMAGES or action not in cls.__CHARACTERS_IMAGES[characterType]:
            cls.load(faction, characterType, "dev")
        return cls.get_images(characterType, action)

    # 是否图片存在
    @classmethod
    def does_action_exist(cls, characterType: str, action: str) -> bool:
        return action in cls.__CHARACTERS_IMAGES[characterType]

    # 生成webp动态图片
    @classmethod
    def generate(cls, entityFaction: str, entityType: str) -> None:
        # 储存数据的字典
        _data: dict = {}
        # 目录路径
        folder_path: str = os.path.join(cls.SPRITES_PATH, entityFaction, entityType)
        # 暂时存放图片的列表
        imgTempList: list = []
        # 历遍目标文件夹中的图片
        for _action_folder in os.listdir(folder_path):
            if os.path.isdir(_action_folder_path := os.path.join(folder_path, _action_folder)):
                # 单个sprite图切割点
                crop_rect: list[int] = []
                # 重置存放图片的列表
                imgTempList.clear()
                # 获取所有当前动作图片的目录
                img_list: list[str] = glob(os.path.join(_action_folder_path, "*.png"))
                if len(img_list) > 0:
                    img_list.sort(key=lambda f: int("".join(filter(str.isdigit, f))))
                    # 加载所有图片
                    for _path in img_list:
                        # 加载单个图片
                        _image: ImageSurface = Images.quickly_load(_path)
                        # 如果切割rect未被初始化
                        if len(crop_rect) <= 0:
                            crop_rect = [_image.get_width(), _image.get_height(), 0, 0]
                        # 获取图片的bounding，并和现有的bounding进行比较
                        _bounding: Rect = _image.get_bounding_rect()
                        if _bounding.x < crop_rect[0]:
                            crop_rect[0] = _bounding.x
                        if _bounding.y < crop_rect[1]:
                            crop_rect[1] = _bounding.y
                        if _bounding.right > crop_rect[2]:
                            crop_rect[2] = _bounding.right
                        if _bounding.bottom > crop_rect[3]:
                            crop_rect[3] = _bounding.bottom
                        # 放入图片
                        imgTempList.append(_image)
                    # 计算universal的尺寸
                    crop_rect[2] -= crop_rect[0]
                    crop_rect[3] -= crop_rect[1]
                    # 写入信息
                    _data[_action_folder] = {"count": len(imgTempList), "subrect": crop_rect, "size": list(_image.get_size())}
                    # 生成当前动作的webp图
                    for i in range(len(imgTempList)):
                        imgTempList[i] = PILImage.fromarray(Surfaces.to_array(imgTempList[i].subsurface(crop_rect)))
                    # 保存当前动作的webp图
                    target_file_name: str = _action_folder + ".webp"
                    imgTempList[0].save(
                        os.path.join(folder_path, target_file_name),
                        save_all=True,
                        append_images=imgTempList[1:],
                        duration=0,
                        lossless=True,
                    )
                    # 删除原先的文件夹
                    shutil.rmtree(os.path.join(folder_path, _action_folder))
        # 保存sprite图数据
        if len(_data) > 0:
            Config.save(os.path.join(folder_path, entityType + ".linpg.meta"), _data)

    # 为Sprite文件夹中的所有角色生成webp动态图片
    @classmethod
    def generate_all(cls) -> None:
        _path: str = cls.SPRITES_PATH
        for faction in os.listdir(_path):
            for key in os.listdir(os.path.join(_path, faction)):
                cls.generate(faction, key)

    # 加载sprite图片模块：接受一个友方角色名，返回对应的动图字典
    @classmethod
    def load(cls, faction: str, characterType: str, mode: str) -> dict:
        sprite_image_meta_data: dict = Config.load_file(
            os.path.join(cls.SPRITES_PATH, faction, characterType, characterType + ".linpg.meta")
        )
        imgId_dict: dict = {}
        # 默认模式下，加载所有动作
        if mode == "default":
            for key in sprite_image_meta_data:
                imgId_dict[key] = cls.__load_action(faction, characterType, key, sprite_image_meta_data[key])
        # 在开发模式下仅加载idle动作
        elif mode == "dev":
            imgId_dict["wait"] = cls.__load_action(faction, characterType, "wait", sprite_image_meta_data["wait"])
        else:
            EXCEPTION.fatal("Mode is not supported")
        return imgId_dict

    # 动图制作模块：接受一个友方角色名和动作,当前的方块标准长和高，返回对应角色动作list或者因为没图片而返回None
    # 810*810 position:405/567
    @classmethod
    def __load_action(cls, faction: str, characterType: str, action: str, action_meta_data: dict) -> dict:
        # 为尚未初始化的角色init一个字典
        if characterType not in cls.__CHARACTERS_IMAGES:
            cls.__CHARACTERS_IMAGES[characterType] = {}
        # 如果动作已被初始化，则返回对应字典
        elif action in cls.__CHARACTERS_IMAGES[characterType]:
            return {"imgId": 0, "alpha": 255}
        # 加载图片
        cls.__CHARACTERS_IMAGES[characterType][action] = _EntityImagesCollection(
            tuple(
                [
                    StaticImage(surf, 0, 0)
                    for surf in Images.load_animated(os.path.join(cls.SPRITES_PATH, faction, characterType, action + ".webp"))
                ]
            ),
            action_meta_data["subrect"][2:],
            action_meta_data["subrect"][:2],
            action_meta_data["size"],
        )
        # 如果是敌人模块，则flip所有图片
        if faction == "enemy":
            cls.__CHARACTERS_IMAGES[characterType][action].flip_all()
        # 返回数据
        return {"imgId": 0, "alpha": 255}


# 雪花片
class Snow(Coordinate):
    def __init__(self, imgId: int, size: int, speed: int, x: int, y: int):
        super().__init__(x, y)
        self.imgId: int = imgId
        self.size: int = size
        self.speed: int = speed

    def move(self, speed_unit: int) -> None:
        self.move_left(self.speed * speed_unit)
        self.move_downward(self.speed * speed_unit)


# 天气系统
class WeatherSystem:
    def __init__(self) -> None:
        self.__initialized: bool = False
        self.__items: tuple[Snow, ...] = tuple()
        self.__img_tuple: tuple = tuple()
        self.__speed_unit: int = 0

    # 初始化
    def init(self, weather: str, entityNum: int = 50) -> None:
        self.__initialized = True
        _temp: Union[ImageSurface, tuple] = SpriteImage("<&env>" + weather + ".png").get(weather)
        if isinstance(_temp, tuple):
            self.__img_tuple = _temp
        else:
            EXCEPTION.fatal("The images for weather has to be in collection!")
        self.__items = tuple(
            [
                Snow(
                    imgId=get_random_int(0, len(self.__img_tuple) - 1),
                    size=get_random_int(5, 10),
                    speed=get_random_int(1, 4),
                    x=get_random_int(1, Display.get_width() * 3 // 2),
                    y=get_random_int(1, Display.get_height()),
                )
                for i in range(entityNum)
            ]
        )

    # 查看初始化状态
    def get_init(self) -> bool:
        return self.__initialized

    # 画出
    def draw(self, surface: ImageSurface, perBlockWidth: number) -> None:
        if not self.__initialized:
            EXCEPTION.fatal("You need to initialize the weather system before using it.")
        self.__speed_unit = int(perBlockWidth / 15)
        for item in self.__items:
            if 0 <= item.x < surface.get_width() and 0 <= item.y < surface.get_height():
                surface.blit(
                    Images.resize(self.__img_tuple[item.imgId], (perBlockWidth / item.size, perBlockWidth / item.size)), item.pos
                )
            item.move(self.__speed_unit)
            if item.x <= 0 or item.y >= surface.get_height():
                item.set_top(get_random_int(-50, 0))
                item.set_left(get_random_int(0, surface.get_width() * 2))