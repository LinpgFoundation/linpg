import math
from .video import *


class Sprite:

    # 加载Sprite图片合集
    @staticmethod
    def load(img_path: str) -> dict:
        # 加载Sprite图
        sprite_sheet: ImageSurface = RawImg.quickly_load(img_path)
        # 加载Sprite图的数据
        sprite_info: dict = Config.load_file(Config.resolve_path(img_path.removesuffix(".png")))
        # 将所有Sprite图上的图片以subsurface的形式append进字典中
        result: dict = {}
        for key, value in sprite_info.items():
            result[key] = sprite_sheet.subsurface((value["coordinate"], value["size"]))
        # 将结果以字典的形式返回
        return result

    # 制作新的Sprite图片合集
    @staticmethod
    def make(img_folder_path: str) -> None:
        # 储存数据的字典
        _data: dict = {}
        # 最大尺寸
        max_block_width: int = 0
        max_block_height: int = 0
        # 历遍目标文件夹中的图片
        for _path in glob(os.path.join(img_folder_path, "*.png")):
            _img: ImageSurface = RawImg.quickly_load(_path)
            # 获取图片的透明bounding
            _bounding: Rect = _img.get_bounding_rect()
            _data[os.path.basename(_path).removesuffix(".png")] = {"img": _img, "bounding": _bounding}
            # 确认最大尺寸
            if max_block_width < _bounding.width:
                max_block_width = _bounding.width
            if max_block_height < _bounding.height:
                max_block_height = _bounding.height
        # 列数
        columns: int = math.ceil(math.sqrt(len(_data)))
        # 行数
        rows: int = math.ceil(len(_data) / columns)
        # 最终sprite图
        sprite_surface: ImageSurface = Surface.transparent((columns * max_block_width, rows * max_block_height))
        # 当前图片index
        index: int = 0
        # 将图片刷到sprite图上
        for value in _data.values():
            _pos: tuple[int, int] = ((index % columns) * max_block_width, index // columns * max_block_height)
            sprite_surface.blit(value["img"].subsurface(value["bounding"]), _pos)
            # 图片的最终尺寸
            value["size"] = [value["bounding"].width, value["bounding"].height]
            # 记下图片在sprite图上的坐标
            value["coordinate"] = list(_pos)
            index += 1
            # 删除不必要的数据
            del value["img"], value["bounding"]
        # 保存sprite图
        RawImg.save(sprite_surface, img_folder_path + ".png")
        # 保存sprite图数据
        Config.save("{0}.{1}".format(img_folder_path, "json"), _data)
