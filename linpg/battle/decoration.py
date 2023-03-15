from .image import *


# 管理场景装饰物的类
class DecorationObject(GameObject2d):
    def __init__(self, x: int, y: int, _type: str, _variation: int, status: dict = {}):
        super().__init__(x, y)
        self.__type: Final[str] = _type
        self._variation: int = _variation
        self.__status: Final[dict] = status
        self.__alpha: int = 255
        self.__is_dark_mode: bool = False

    # 确保图片已经被存档
    def ensure_image_cached(self) -> None:
        DecorationImagesModule.add_image(self.__type)

    @property
    def id(self) -> str:
        return self.__type if self._variation <= 0 else self.__type + ":" + str(self._variation)

    @property
    def type(self) -> str:
        return self.__type

    @property
    def variation(self) -> int:
        return self._variation

    def get_alpha(self) -> int:
        return self.__alpha

    def set_alpha(self, value: int) -> None:
        self.__alpha = value

    def set_dark_mode(self, value: bool) -> None:
        self.__is_dark_mode = value

    def to_dict(self) -> dict:
        data_t: dict = {"x": self.x, "y": self.y, "id": self.id}
        if len(self.__status) > 0:
            data_t["status"] = copy.deepcopy(self.__status)
        return data_t

    @staticmethod
    def from_dict(_data: dict) -> "DecorationObject":
        index_args: list[str] = str(_data["id"]).split(":")
        if not isinstance(_data.get("status"), dict):
            _data["status"] = {}
        theDecoration: DecorationObject = DecorationObject(
            _data["x"], _data["y"], index_args[0], int(index_args[1]) if len(index_args) > 1 else 0, _data["status"]
        )
        return theDecoration

    def is_on_pos(self, pos: object) -> bool:
        return Coordinates.is_same(self.get_pos(), pos)

    def _has_status(self, key: str) -> bool:
        return key in self.__status

    def get_status(self, key: str) -> object:
        return self.__status[key]

    def set_status(self, key: str, value: object) -> None:
        self.__status[key] = value

    def remove_status(self, key: str) -> None:
        if key in self.__status:
            del self.__status[key]
        else:
            EXCEPTION.fatal('Cannot remove status "{}" because it does not exist'.format(key))

    def display(self, _surface: ImageSurface, offSet: tuple[int, int] = ORIGIN) -> None:
        abs_pos: Final[tuple[int, int]] = Coordinates.add(self.get_pos(), offSet)
        imgToBlit = DecorationImagesModule.get_image(self.id, self.__is_dark_mode)
        imgToBlit.set_width_with_original_image_size_locked(TileMapImagesModule.TILE_TEMPLE_WIDTH // 2)
        imgToBlit.set_alpha(self.__alpha)
        imgToBlit.set_left(abs_pos[0] + TileMapImagesModule.TILE_TEMPLE_WIDTH // 4)
        imgToBlit.set_bottom(abs_pos[1] + TileMapImagesModule.TILE_TEMPLE_HEIGHT * 0.85)
        imgToBlit.draw(_surface)

    def get_width(self) -> int:
        return 0

    def get_height(self) -> int:
        return 0
