import math
from .video import *


class Sprite:

    # 加载Sprite图片合集
    @staticmethod
    def load(img_path: str) -> dict:
        sprite_sheet: ImageSurface = RawImg.quickly_load(img_path)
        sprite_info: dict = Config.load_file(Config.resolve_path(img_path.removesuffix(".png")))
        result: dict = {}
        for key, value in sprite_info.items():
            result[key] = sprite_sheet.subsurface((value["coordinate"], value["size"]))
        return result

    # 制作新的Sprite图片合集
    @staticmethod
    def make(img_folder_path: str) -> None:
        _data: dict = {}
        for _path in glob(os.path.join(img_folder_path, "*.png")):
            _data[os.path.basename(_path).removesuffix(".png")] = {"img": RawImg.quickly_load(_path)}

        crop_rect: Rectangle = Rectangle.new((0, 0), (0, 0))
        for key in _data:
            bounding = _data[key]["img"].get_bounding_rect()
            _data[key]["bounding"] = bounding
            if crop_rect.get_left() > bounding.x:
                crop_rect.set_left(bounding.x)
            if crop_rect.get_top() > bounding.y:
                crop_rect.set_top(bounding.y)
            if crop_rect.get_right() < bounding.right:
                crop_rect.set_width(bounding.right - crop_rect.left)
            if crop_rect.get_bottom() < bounding.bottom:
                crop_rect.set_height(bounding.bottom - crop_rect.top)

        columns: int = math.ceil(math.sqrt(len(_data)))
        rows: int = math.ceil(len(_data) / columns)
        sprite_surface: ImageSurface = new_transparent_surface((columns * crop_rect.width, rows * crop_rect.height))

        index: int = 0
        for value in _data.values():
            _pos: tuple[int, int] = ((index % columns) * crop_rect.width, int(index / rows) * crop_rect.height)
            sprite_surface.blit(value["img"].subsurface(value["bounding"]), _pos)
            value["size"] = [value["bounding"].width, value["bounding"].height]
            value["coordinate"] = list(_pos)
            del value["img"], value["bounding"]
            index += 1

        RawImg.save(sprite_surface, img_folder_path + ".png")
        # Config.get_file_type()
        Config.save("{0}.{1}".format(img_folder_path, "json"), _data)
