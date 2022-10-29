from ..dialogue import *


# 地图图片参数管理模块
class MapImageParameters:

    # 方块尺寸
    __TILE_WIDTH: int = 0
    __TILE_HEIGHT: int = 0
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
    def set_tile_size(cls, _width: int, _height: int) -> None:
        cls.__TILE_WIDTH = _width
        cls.__TILE_HEIGHT = _height

    # 获取方块宽度
    @classmethod
    def get_tile_width(cls) -> int:
        return cls.__TILE_WIDTH

    # 获取方块高度
    @classmethod
    def get_tile_height(cls) -> int:
        return cls.__TILE_HEIGHT


# 装饰物的图片管理模块
class DecorationImagesModule:

    # 引擎自带的场景装饰物，默认为空的sheet
    DEFAULT_DECORATION_IMAGE_SPRITE_SHEET: SpriteImage = SpriteImage("<NULL>")
    # 引擎自带的场景装饰物是否被加载
    __IS_DEFAULT_DECORATION_IMAGE_SPRITE_SHEET_INITIALIZED: bool = False
    # 项目自带的场景装饰物，默认为空的sheet
    CUSTOM_DECORATION_IMAGE_SPRITE_SHEET: SpriteImage = SpriteImage("<NULL>")
    # 项目自带的场景装饰物是否被加载
    __IS_CUSTOM_DECORATION_IMAGE_SPRITE_SHEET_INITIALIZED: bool = False
    # 经过处理的场景装饰物
    __DECORATION_IMAGE_DICT: Final[dict[str, StaticImage | tuple[StaticImage, ...]]] = {}
    __DECORATION_IMAGE_DICT_DARK: Final[dict[str, StaticImage | tuple[StaticImage, ...]]] = {}

    # 确认sheet已经初始化
    @classmethod
    def init(cls) -> None:
        # 如果自带的SPRITE SHEET未被初始化，则初始化
        if not cls.__IS_DEFAULT_DECORATION_IMAGE_SPRITE_SHEET_INITIALIZED:
            if os.path.exists(Images.generate_path_according_to_prefix("<!env>decorations.png")):
                cls.DEFAULT_DECORATION_IMAGE_SPRITE_SHEET = SpriteImage("<!env>decorations.png")
            cls.__IS_DEFAULT_DECORATION_IMAGE_SPRITE_SHEET_INITIALIZED = True
        # 如果开发者自定义的SPRITE SHEET未被初始化，则初始化
        if not cls.__IS_CUSTOM_DECORATION_IMAGE_SPRITE_SHEET_INITIALIZED:
            if os.path.exists(Images.generate_path_according_to_prefix("<@env>decorations.png")):
                cls.CUSTOM_DECORATION_IMAGE_SPRITE_SHEET = SpriteImage("<@env>decorations.png")
            cls.__IS_CUSTOM_DECORATION_IMAGE_SPRITE_SHEET_INITIALIZED = True

    # 获取当前装饰物种类的数量
    @classmethod
    def count_variations(cls, _type: str) -> int:
        _ref: Optional[StaticImage | tuple[StaticImage, ...]] = cls.__DECORATION_IMAGE_DICT.get(_type)
        if _ref is None:
            EXCEPTION.fatal('Cannot find decoration image "{}"'.format(_type))
        return len(_ref) if isinstance(_ref, tuple) else 1

    # 加载场景装饰物图片
    @classmethod
    def add_image(cls, _type: str) -> None:
        # 确保初始化
        cls.init()
        # 查看图片是否在自带或自定义的SPRITE SHEET中存在，不存在则为None
        sheet_ref: Optional[SpriteImage] = (
            cls.DEFAULT_DECORATION_IMAGE_SPRITE_SHEET
            if cls.DEFAULT_DECORATION_IMAGE_SPRITE_SHEET.contain(_type)
            else cls.CUSTOM_DECORATION_IMAGE_SPRITE_SHEET
            if cls.CUSTOM_DECORATION_IMAGE_SPRITE_SHEET.contain(_type)
            else None
        )
        # 如果图片存在，则reference不为None
        if sheet_ref is not None:
            # 最后确认一下是不是需要加载
            if _type not in cls.__DECORATION_IMAGE_DICT:
                # 从sheet中读取装饰物图片
                _img: ImageSurface | tuple[ImageSurface, ...] = sheet_ref.get(_type)
                # 将图片转换成对应格式后存入字典中
                cls.__DECORATION_IMAGE_DICT[_type] = (
                    tuple(StaticImage(_imgRef, 0, 0) for _imgRef in _img) if isinstance(_img, tuple) else StaticImage(_img, 0, 0)
                )
            # 如果是夜战模式
            if MapImageParameters.get_darkness() > 0:
                _imgRefTemp: StaticImage | tuple[StaticImage, ...] = cls.__DECORATION_IMAGE_DICT[_type]
                if isinstance(_imgRefTemp, tuple):
                    _temp: list[StaticImage] = []
                    for _imgRef in _imgRefTemp:
                        _imgCopy = _imgRef.copy()
                        _imgCopy.add_darkness(MapImageParameters.get_darkness())
                        _temp.append(_imgCopy)
                    cls.__DECORATION_IMAGE_DICT_DARK[_type] = tuple(_temp)
                else:
                    _imgTemp: StaticImage = _imgRefTemp.copy()
                    _imgTemp.add_darkness(MapImageParameters.get_darkness())
                    cls.__DECORATION_IMAGE_DICT_DARK[_type] = _imgTemp
        else:
            EXCEPTION.fatal('Cannot find decoration image "{}"'.format(_type))

    # 获取图片
    @classmethod
    def get_image(cls, _id: str, darkMode: bool) -> StaticImage:
        # 获取参数
        _absId: list[str] = _id.split(":")
        # 尝试获取图片
        result: StaticImage | tuple[StaticImage, ...]
        possible_result: Optional[StaticImage | tuple[StaticImage, ...]] = (
            cls.__DECORATION_IMAGE_DICT_DARK.get(_absId[0]) if darkMode is True else cls.__DECORATION_IMAGE_DICT.get(_absId[0])
        )
        if possible_result is not None:
            result = possible_result
        else:
            if Debug.get_developer_mode():
                EXCEPTION.inform("Cannot find decoration image '{}', we will try to load it for you right now, but please by aware.".format(_id))
            cls.add_image(_absId[0])
            result = cls.__DECORATION_IMAGE_DICT_DARK[_absId[0]] if darkMode is True else cls.__DECORATION_IMAGE_DICT[_absId[0]]
        return result if not isinstance(result, tuple) else result[0 if len(_absId) <= 1 else int(_absId[1])]


# 地图贴图的管理模块
class TileMapImagesModule:

    # 引擎自带的地图贴图，默认为空的sheet
    DEFAULT_TILE_MAP_IMAGE_SPRITE_SHEET: SpriteImage = SpriteImage("<NULL>")
    # 引擎自带的地图贴图是否被加载
    __DEFAULT_TILE_MAP_IMAGE_SPRITE_SHEET_INITIALIZED: bool = False
    # 环境
    __ENV_IMAGE_DICT: Final[dict[str, StaticImage | tuple[StaticImage, ...]]] = {}
    __ENV_IMAGE_DICT_DARK: Final[dict[str, StaticImage | tuple[StaticImage, ...]]] = {}
    # 标准Tile尺寸
    TILE_TEMPLE_WIDTH: int = 0
    TILE_TEMPLE_HEIGHT: int = 0

    # 确认sheet已经初始化
    @classmethod
    def init(cls) -> None:
        # 如果SPRITE SHEET未被初始化，则初始化
        if not cls.__DEFAULT_TILE_MAP_IMAGE_SPRITE_SHEET_INITIALIZED:
            if os.path.exists(Images.generate_path_according_to_prefix("<!env>tiles.png")):
                cls.DEFAULT_TILE_MAP_IMAGE_SPRITE_SHEET = SpriteImage("<!env>tiles.png")
            cls.__DEFAULT_TILE_MAP_IMAGE_SPRITE_SHEET_INITIALIZED = True

    # 调整尺寸
    @classmethod
    def update_size(cls, _width: int, _height: int) -> None:
        # 更新尺寸
        MapImageParameters.set_tile_size(_width, _height)
        # 调整地图方块尺寸
        for _imgRef in cls.__ENV_IMAGE_DICT.values():
            if not isinstance(_imgRef, tuple):
                _imgRef.set_width_with_original_image_size_locked(MapImageParameters.get_tile_width())
            else:
                for _temp in _imgRef:
                    _temp.set_width_with_original_image_size_locked(MapImageParameters.get_tile_width())
        # 调整黑夜模式下的地图方块尺寸
        for _imgRef in cls.__ENV_IMAGE_DICT_DARK.values():
            if not isinstance(_imgRef, tuple):
                _imgRef.set_width_with_original_image_size_locked(MapImageParameters.get_tile_width())
            else:
                for _temp in _imgRef:
                    _temp.set_width_with_original_image_size_locked(MapImageParameters.get_tile_width())
        # 根据Template计算tile标准尺寸和offset
        cls.TILE_TEMPLE_WIDTH, cls.TILE_TEMPLE_HEIGHT = cls.get_image("template", False).get_bounding_rect().get_size()
        cls.TILE_TEMPLE_HEIGHT = cls.TILE_TEMPLE_HEIGHT * 2 // 5

    # 加载图片
    @classmethod
    def add_image(cls, _id: str) -> None:
        # 确保初始化
        cls.init()
        # 根据id决定如何处理图片加载
        _id = _id.split(":")[0]
        if cls.DEFAULT_TILE_MAP_IMAGE_SPRITE_SHEET.contain(_id):
            _temp: list[StaticImage]
            _imgTemp: StaticImage
            if _id not in cls.__ENV_IMAGE_DICT:
                _img: ImageSurface | tuple[ImageSurface, ...] = cls.DEFAULT_TILE_MAP_IMAGE_SPRITE_SHEET.get(_id)
                if isinstance(_img, tuple):
                    _temp = [StaticImage(_imgRef, 0, 0) for _imgRef in _img]
                    for _imgRef in _temp:
                        _imgRef.set_width_with_original_image_size_locked(MapImageParameters.get_tile_width())
                    cls.__ENV_IMAGE_DICT[_id] = tuple(_temp)
                else:
                    _imgTemp = StaticImage(_img, 0, 0)
                    _imgTemp.set_width_with_original_image_size_locked(MapImageParameters.get_tile_width())
                    cls.__ENV_IMAGE_DICT[_id] = _imgTemp
            # 如果是夜战模式
            if MapImageParameters.get_darkness() > 0:
                _imgRefTemp: StaticImage | tuple[StaticImage, ...] = cls.__ENV_IMAGE_DICT[_id]
                if isinstance(_imgRefTemp, tuple):
                    _temp = []
                    for _imgRef in _imgRefTemp:
                        _imgCopy = _imgRef.copy()
                        _imgCopy.add_darkness(MapImageParameters.get_darkness())
                        _temp.append(_imgCopy)
                    cls.__ENV_IMAGE_DICT_DARK[_id] = tuple(_temp)
                else:
                    _imgTemp = _imgRefTemp.copy()
                    _imgTemp.add_darkness(MapImageParameters.get_darkness())
                    cls.__ENV_IMAGE_DICT_DARK[_id] = _imgTemp
        else:
            EXCEPTION.fatal('Cannot find tile map image "{}"'.format(_id))

    # 获取图片
    @classmethod
    def get_image(cls, _id: str, darkMode: bool) -> StaticImage:
        # 获取参数
        _absId: list[str] = _id.split(":")
        # 尝试获取图片
        result: StaticImage | tuple[StaticImage, ...]
        possible_result: Optional[StaticImage | tuple[StaticImage, ...]] = (
            cls.__ENV_IMAGE_DICT_DARK.get(_absId[0]) if darkMode is True else cls.__ENV_IMAGE_DICT.get(_absId[0])
        )
        if possible_result is not None:
            result = possible_result
        else:
            if Debug.get_developer_mode():
                EXCEPTION.inform("Cannot find tile image '{}', we will try to load it for you right now, but please by aware.".format(_id))
            cls.add_image(_absId[0])
            result = cls.__ENV_IMAGE_DICT_DARK[_absId[0]] if darkMode is True else cls.__ENV_IMAGE_DICT[_absId[0]]
        return result if not isinstance(result, tuple) else result[0 if len(_absId) <= 1 else int(_absId[1])]


# 管理单个动作所有对应图片的模块
class _EntityImagesCollection:
    def __init__(self, imagesList: tuple[StaticImage, ...], crop_size: list[int], offset: list[int], original_img_size: list[int]) -> None:
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
    def draw_onto(self, _surface: ImageSurface, alpha: int, ifFlip: bool, pos: tuple, draw_outline: bool) -> None:
        self.__current_image_pointer.set_size(self.__width, self.__height)
        self.__current_image_pointer.set_alpha(alpha)  # 翻转图片
        self.__current_image_pointer.set_top(self.__offset_y * self.__height / self.__cropped_image_height + pos[1])
        if ifFlip:
            self.__current_image_pointer.flip_if_not()
            self.__current_image_pointer.set_left(self.__right_offset_x * self.__width / self.__cropped_image_width + pos[0])
        else:
            self.__current_image_pointer.flip_back_to_normal()
            self.__current_image_pointer.set_left(self.__left_offset_x * self.__width / self.__cropped_image_width + pos[0])
        self.__current_image_pointer.draw(_surface)
        if draw_outline is True:
            self.__current_image_pointer.draw_outline(_surface)


# 角色图片管理模块
class EntitySpriteImageManager:

    # 用于存放角色图片的字典
    __CHARACTERS_IMAGES: Final[dict[str, dict[str, _EntityImagesCollection]]] = {}
    # 角色图片文件夹路径
    SPRITES_PATH: Final[str] = Specification.get_directory("sprite")

    # 获取图片
    @classmethod
    def get_images(cls, characterType: str, action: str) -> _EntityImagesCollection:
        return cls.__CHARACTERS_IMAGES[characterType][action]

    # 尝试获取图片
    @classmethod
    def try_get_image_references(cls, faction: str, characterType: str, action: str) -> _EntityImagesCollection:
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
                        _bounding: PG_Rect = _image.get_bounding_rect()
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
                    imgTempList[0].save(os.path.join(folder_path, target_file_name), save_all=True, append_images=imgTempList[1:], duration=0, lossless=True)
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
        sprite_image_meta_data: dict = Config.load_file(os.path.join(cls.SPRITES_PATH, faction, characterType, characterType + ".linpg.meta"))
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
            tuple(StaticImage(surf, 0, 0) for surf in Images.load_animated(os.path.join(cls.SPRITES_PATH, faction, characterType, action + ".webp"))),
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
        _temp: ImageSurface | tuple = SpriteImage("<&env>" + weather + ".png").get(weather)
        if isinstance(_temp, tuple):
            self.__img_tuple = _temp
        else:
            EXCEPTION.fatal("The images for weather has to be in collection!")
        self.__items = tuple(
            [
                Snow(
                    imgId=Numbers.get_random_int(0, len(self.__img_tuple) - 1),
                    size=Numbers.get_random_int(5, 10),
                    speed=Numbers.get_random_int(1, 4),
                    x=Numbers.get_random_int(1, Display.get_width() * 3 // 2),
                    y=Numbers.get_random_int(1, Display.get_height()),
                )
                for _ in range(entityNum)
            ]
        )

    # 查看初始化状态
    def get_init(self) -> bool:
        return self.__initialized

    # 画出
    def draw(self, _surface: ImageSurface, perBlockWidth: number) -> None:
        if not self.__initialized:
            EXCEPTION.fatal("You need to initialize the weather system before using it.")
        self.__speed_unit = int(perBlockWidth / 15)
        for item in self.__items:
            if 0 <= item.x < _surface.get_width() and 0 <= item.y < _surface.get_height():
                _surface.blit(Images.resize(self.__img_tuple[item.imgId], (perBlockWidth / item.size, perBlockWidth / item.size)), item.pos)
            item.move(self.__speed_unit)
            if item.x <= 0 or item.y >= _surface.get_height():
                item.set_top(Numbers.get_random_int(-50, 0))
                item.set_left(Numbers.get_random_int(0, _surface.get_width() * 2))
