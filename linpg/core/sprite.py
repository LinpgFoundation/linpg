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

    # 拆分一个未知格式的像素图，字典key为动作名称，value分别为xStart, yStart, width, height, frameCount
    @staticmethod
    def split_sprite_image(_image_path: str, output_directory: str, _data: dict[str, tuple[int, int, int, int, int]]) -> None:
        _sprite_image: ImageSurface = Images.load(_image_path)
        Files.delete_if_exist(output_directory)
        os.mkdir(output_directory)
        for key, value in _data.items():
            _out_path: str = os.path.join(output_directory, key)
            os.mkdir(_out_path)
            for i in range(value[4]):
                Images.save(_sprite_image.subsurface((value[0] + i * value[2], value[1], value[2], value[3])), os.path.join(_out_path, f"{key}_{i}.png"))

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
    def __put_and_document(_pos: tuple[int, int], minimize_pixels: bool, value: dict, sprite_surface: ImageSurface) -> list[int]:
        _rect: list[int]
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
    def generate(
        cls,
        img_folder_path: str,
        minimize_pixels: bool = False,
        actionOnSameRow: bool = False,
        universal_width: int | None = None,
        universal_height: int | None = None,
        additional_padding: int = 0,
        resultFileType: str = "png",
    ) -> None:
        # 储存数据的字典
        _cache: dict[str, Any] = {}
        _out: dict[str, Any] = {}
        # 最大尺寸
        max_block_size: list[int] = [0, 0]
        # 图片总数
        _count: int = 0
        # 最大动作数
        _max_action_count: int = 0
        # 历遍目标文件夹中的图片
        for _path in Files.natural_sort(glob(os.path.join(img_folder_path, "*"))):
            _name: str
            if os.path.isdir(_path):
                _name = os.path.basename(_path)
                _cache[_name] = [
                    cls.__process_image(_imgPath, max_block_size, minimize_pixels) for _imgPath in Files.natural_sort(glob(os.path.join(_path, "*")))
                ]
                _count += len(_cache[_name])
                _max_action_count = max(_max_action_count, len(_cache[_name]))
            elif _path.endswith(".png") or _path.endswith(".jpg"):
                _name = os.path.basename(_path)
                _name = _name[: _name.index(".")]
                _cache[_name] = cls.__process_image(_path, max_block_size, minimize_pixels)
                _count += 1
                _max_action_count = max(_max_action_count, 1)
        # 最终sprite图
        sprite_surface: ImageSurface = Surfaces.NULL
        # 如果设置了固定尺寸
        if universal_width is not None:
            max_block_size[0] = universal_width
        if universal_height is not None:
            max_block_size[1] = universal_height
        max_block_size[0] += additional_padding * 2
        max_block_size[1] += additional_padding * 2
        # 同一动作可以不同行，方便最小化图片
        if not actionOnSameRow:
            # 列数
            columns: int = math.ceil(math.sqrt(_count))
            # 行数
            rows: int = math.ceil(_count / columns)
            # 为最终sprite图获取内存空间
            sprite_surface = Surfaces.transparent((columns * max_block_size[0], rows * max_block_size[1]))
            # 当前图片index
            index: int = 0
            # 将图片刷到sprite图上
            for key, value in _cache.items():
                if isinstance(value, dict):
                    _out["animations"][key] = cls.__put_and_document(
                        ((index % columns) * max_block_size[0] + additional_padding, index // columns * max_block_size[1] + additional_padding),
                        minimize_pixels,
                        value,
                        sprite_surface,
                    )
                    index += 1
                else:
                    for i in range(len(value)):
                        _out["animations"][i] = cls.__put_and_document(
                            ((index % columns) * max_block_size[0] + additional_padding, index // columns * max_block_size[1] + additional_padding),
                            minimize_pixels,
                            value[i],
                            sprite_surface,
                        )
                        index += 1
        # 同一动作必须同行，方便读取管理
        else:
            # 为最终sprite图获取内存空间
            sprite_surface = Surfaces.transparent((_max_action_count * max_block_size[0], len(_cache) * max_block_size[1]))
            current_row: int = 0
            current_column: int = 0
            is_universal_size: bool = universal_width is not None and universal_height is not None
            if is_universal_size is True:
                _out["size"] = [max_block_size[0], max_block_size[1]]
            _out["animations"] = {}
            # 将图片刷到sprite图上
            for key in sorted(_cache, key=lambda k: len(_cache[k]) if isinstance(_cache[k], list) else 1):
                value = _cache[key]
                if isinstance(value, dict):
                    _out["animations"][key] = cls.__put_and_document(
                        (current_column * max_block_size[0] + additional_padding, current_row * max_block_size[1] + additional_padding),
                        minimize_pixels,
                        value,
                        sprite_surface,
                    )
                    if is_universal_size is True:
                        _out["animations"][key] = _out["animations"][key][:2]
                        _out["animations"][key][0] //= max_block_size[0]
                        _out["animations"][key][1] //= max_block_size[1]
                    _out["animations"][key].append(1)
                    current_column += 1
                    if current_column > _max_action_count:
                        current_column = 0
                        current_row += 1
                else:
                    if current_column + len(value) > _max_action_count:
                        current_column = 0
                        current_row += 1
                    _out["animations"][key] = cls.__put_and_document(
                        (current_column * max_block_size[0] + additional_padding, current_row * max_block_size[1] + additional_padding),
                        minimize_pixels,
                        value[0],
                        sprite_surface,
                    )
                    if is_universal_size is True:
                        _out["animations"][key] = _out["animations"][key][:2]
                        _out["animations"][key][0] //= max_block_size[0]
                        _out["animations"][key][1] //= max_block_size[1]
                    _out["animations"][key].append(len(value))
                    current_column += 1
                    for i in range(1, len(value)):
                        cls.__put_and_document(
                            (current_column * max_block_size[0] + additional_padding, current_row * max_block_size[1] + additional_padding),
                            minimize_pixels,
                            value[i],
                            sprite_surface,
                        )
                        current_column += 1
            sprite_surface = sprite_surface.subsurface((0, 0, sprite_surface.get_width(), (current_row + 1) * max_block_size[1]))
        # 保存sprite图
        target_file_name: str = f"{img_folder_path}.{resultFileType}"
        Images.save(sprite_surface, target_file_name)
        # 保存sprite图数据
        Config.save(target_file_name + ".linpg.meta", _out)
