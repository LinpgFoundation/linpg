import math

from .video import *


class SpriteImage:
    def __init__(self, img_path: str) -> None:
        # 路径
        self.__PATH: str = img_path
        # 加载Sprite图
        self.__SHEET: ImageSurface = Images.quickly_load(self.__PATH)
        # 加载Sprite图的数据
        self.__DICTIONARY: dict = {}
        if not self.__PATH.startswith("<"):
            self.__DICTIONARY.update(Config.load_file(self.__PATH + ".linpg.meta"))
        elif self.__PATH != "<NULL>":
            self.__DICTIONARY.update(Config.load_file(Images.generate_path_according_to_prefix(self.__PATH).removesuffix(".zip") + ".linpg.meta"))

    # 获取一个图片
    def get(self, key: str) -> ImageSurface | tuple[ImageSurface, ...]:
        return (
            self.__SHEET.subsurface(self.__DICTIONARY[key])
            if not isinstance(self.__DICTIONARY[key][0], list)
            else tuple(self.__SHEET.subsurface(_data) for _data in self.__DICTIONARY[key])
        )

    # 是否存在key
    def contain(self, key: str) -> bool:
        return key in self.__DICTIONARY

    # 将所有图片以dict的形式返回
    def to_dict(self) -> dict[str, ImageSurface | tuple[ImageSurface, ...]]:
        # 将所有Sprite图上的图片以subsurface的形式append进字典中
        result: dict[str, ImageSurface | tuple[ImageSurface, ...]] = {}
        for key in self.__DICTIONARY:
            result[key] = self.get(key)
        # 将结果以字典的形式返回
        return result

    # 将所有图片以tuple的形式返回
    def to_tuple(self) -> tuple:
        return tuple(self.to_dict().values())

    # 返回一个复制品
    def copy(self) -> "SpriteImage":
        return SpriteImage(self.__PATH)

    # 获取Sprite图（这是很危险的操作，强烈不建议在引擎外使用）
    def get_SHEET(self) -> ImageSurface:
        return self.__SHEET

    # 设置Sprite图（这是很危险的操作，强烈不建议在引擎外使用）
    def set_SHEET(self, SHEET: ImageSurface) -> None:
        self.__SHEET = SHEET

    # 处理图片并返回对应的数据
    @staticmethod
    def __process_image(_path: str, max_block_size: list[int], minimize_pixels: bool) -> dict:
        _image_data: dict = {}
        _img: ImageSurface = Images.quickly_load(_path)
        if not minimize_pixels:
            # 确认最大尺寸
            if max_block_size[0] < _img.get_width():
                max_block_size[0] = _img.get_width()
            if max_block_size[1] < _img.get_height():
                max_block_size[1] = _img.get_height()
        else:
            # 获取图片的透明bounding
            _bounding: PG_Rect = _img.get_bounding_rect()
            # 确认最大尺寸
            if max_block_size[0] < _bounding.width:
                max_block_size[0] = _bounding.width
            if max_block_size[1] < _bounding.height:
                max_block_size[1] = _bounding.height
            # 写入bounding尺寸
            _image_data["bounding"] = _bounding
        # 放入图片
        _image_data["img"] = _img
        return _image_data

    # 将图片渲染到sheet上等待保存，并生产rect的信息
    @staticmethod
    def __put_and_document(index: int, columns: int, max_block_size: list[int], minimize_pixels: bool, value: dict, sprite_surface: ImageSurface) -> list[int]:
        _rect: list[int]
        _pos: tuple[int, int] = ((index % columns) * max_block_size[0], index // columns * max_block_size[1])
        if not minimize_pixels:
            sprite_surface.blit(value["img"], _pos)
            # 记录下图片的最终尺寸和图片在sprite图上的坐标
            _rect = [_pos[0], _pos[1], value["img"].get_width(), value["img"].get_height()]
        else:
            _bounding = value["bounding"]
            sprite_surface.blit(value["img"].subsurface(_bounding), _pos)
            # 记录下图片的最终尺寸和图片在sprite图上的坐标
            _rect = [_pos[0], _pos[1], _bounding.width, _bounding.height]
        return _rect

    # 制作新的Sprite图片合集
    @classmethod
    def generate(cls, img_folder_path: str, minimize_pixels: bool = False, resultFileType: str = "png") -> None:
        # 储存数据的字典
        _data: dict = {}
        # 最大尺寸
        max_block_size: list[int] = [0, 0]
        # 图片总数
        _count: int = 0
        # 历遍目标文件夹中的图片
        for _path in Organizer.natural_sort(glob(os.path.join(img_folder_path, "*"))):
            _name: str
            if os.path.isdir(_path):
                _name = os.path.basename(_path)
                _data[_name] = [
                    cls.__process_image(_imgPath, max_block_size, minimize_pixels) for _imgPath in Organizer.natural_sort(glob(os.path.join(_path, "*")))
                ]
                _count += len(_data[_name])
            elif _path.endswith(".png") or _path.endswith(".jpg"):
                _name = os.path.basename(_path)
                _name = _name[: _name.index(".")]
                _data[_name] = cls.__process_image(_path, max_block_size, minimize_pixels)
                _count += 1
        # 列数
        columns: int = math.ceil(math.sqrt(_count))
        # 行数
        rows: int = math.ceil(_count / columns)
        # 最终sprite图
        sprite_surface: ImageSurface = Surfaces.transparent((columns * max_block_size[0], rows * max_block_size[1]))
        # 当前图片index
        index: int = 0
        # 将图片刷到sprite图上
        for key, value in _data.items():
            if isinstance(value, dict):
                _data[key] = cls.__put_and_document(index, columns, max_block_size, minimize_pixels, value, sprite_surface)
                index += 1
            else:
                for i in range(len(value)):
                    _data[key][i] = cls.__put_and_document(index, columns, max_block_size, minimize_pixels, value[i], sprite_surface)
                    index += 1
        # 保存sprite图
        target_file_name: str = "{0}.{1}".format(img_folder_path, resultFileType)
        Images.save(sprite_surface, target_file_name)
        # 保存sprite图数据
        Config.save(target_file_name + ".linpg.meta", _data)
