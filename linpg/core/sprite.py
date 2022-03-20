import math
from .video import *


class SpriteImage:
    def __init__(self, img_path: str) -> None:
        # 路径
        self.__PATH: str = img_path
        # 加载Sprite图
        self.__SHEET: ImageSurface = RawImg.quickly_load(self.__PATH)
        # 加载Sprite图的数据
        self.__DICTIONARY: dict = {}
        if self.__PATH != "<!null>":
            self.__DICTIONARY.update(Config.load_file(self.__PATH + ".linpg.meta"))

    # 获取一个图片
    def get(self, key: str) -> Union[ImageSurface, tuple]:
        return (
            self.__SHEET.subsurface(self.__DICTIONARY[key])
            if not isinstance(self.__DICTIONARY[key][0], list)
            else tuple([self.__SHEET.subsurface(_data) for _data in self.__DICTIONARY[key]])
        )

    # 是否存在key
    def contain(self, key: str) -> bool:
        return key in self.__DICTIONARY

    # 将所有图片以dict的形式返回
    def to_dict(self) -> dict:
        # 将所有Sprite图上的图片以subsurface的形式append进字典中
        result: dict = {}
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

    # 制作新的Sprite图片合集
    @staticmethod
    def generate(img_folder_path: str, minimize_pixels: bool = False, resultFileType: str = "png") -> None:
        # 储存数据的字典
        _data: dict = {}
        # 最大尺寸
        max_block_width: int = 0
        max_block_height: int = 0
        # 历遍目标文件夹中的图片
        for _path in glob(os.path.join(img_folder_path, "*.png")):
            _img: ImageSurface = RawImg.quickly_load(_path)
            _name: str = os.path.basename(_path).removesuffix(".png")
            _data[_name] = {}
            if not minimize_pixels:
                # 确认最大尺寸
                if max_block_width < _img.get_width():
                    max_block_width = _img.get_width()
                if max_block_height < _img.get_height():
                    max_block_height = _img.get_height()
            else:
                # 获取图片的透明bounding
                _bounding: Rect = _img.get_bounding_rect()
                # 确认最大尺寸
                if max_block_width < _bounding.width:
                    max_block_width = _bounding.width
                if max_block_height < _bounding.height:
                    max_block_height = _bounding.height
                # 写入bounding尺寸
                _data[_name]["bounding"] = _bounding
            # 放入图片
            _data[_name]["img"] = _img
        # 列数
        columns: int = math.ceil(math.sqrt(len(_data)))
        # 行数
        rows: int = math.ceil(len(_data) / columns)
        # 最终sprite图
        sprite_surface: ImageSurface = Surface.transparent((columns * max_block_width, rows * max_block_height))
        # 当前图片index
        index: int = 0
        # 将图片刷到sprite图上
        for key in _data:
            _pos: tuple[int, int] = ((index % columns) * max_block_width, index // columns * max_block_height)
            if not minimize_pixels:
                sprite_surface.blit(_data[key]["img"], _pos)
                # 记录下图片的最终尺寸和图片在sprite图上的坐标
                _data[key] = [_pos[0], _pos[1], _data[key]["img"].get_width(), _data[key]["img"].get_height()]
            else:
                _bounding = _data[key]["bounding"]
                sprite_surface.blit(_data[key]["img"].subsurface(_bounding), _pos)
                # 记录下图片的最终尺寸和图片在sprite图上的坐标
                _data[key] = [_pos[0], _pos[1], _bounding.width, _bounding.height]
            index += 1
        # 保存sprite图
        target_file_name: str = "{0}.{1}".format(img_folder_path, resultFileType)
        RawImg.save(sprite_surface, target_file_name)
        # 保存sprite图数据
        Config.save(target_file_name + ".linpg.meta", _data)
