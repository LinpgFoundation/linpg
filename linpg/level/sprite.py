from ..dialogue import *


class SpriteImage:
    IS_PIXEL: bool = True

    def __init__(self, metadata_path: str) -> None:
        # path of meta metadata
        self.__METADATA_PATH: Final[str] = metadata_path
        # metadata
        self.__METADATA: Final[dict[str, str | int]] = Configurations.load_file(self.__METADATA_PATH)
        # load tile sheet
        self.__SHEET_ORIGINAL: Final[ImageSurface] = Images.quickly_load(
            os.path.join(os.path.dirname(self.__METADATA_PATH), str(self.__METADATA["image"]))
        )
        self.__sheet: ImageSurface = self.__SHEET_ORIGINAL
        # get tile count
        self.__tile_count: Final[int] = int(self.__METADATA["tilecount"])
        # get columns
        self.__COLUMN: Final[int] = int(self.__METADATA["columns"])
        # get rows
        self.__ROW: Final[int] = self.__tile_count // self.__COLUMN
        # tile width
        self.__tile_width: int = int(self.__METADATA["tilewidth"])
        # tile height
        self.__tile_height: int = int(self.__METADATA["tileheight"])

    def set_size(self, w: int, h: int) -> None:
        if self.__tile_width == w and self.__tile_height == h:
            return
        self.__tile_width = w
        self.__tile_height = h
        self.__sheet = (
            Images.resize(self.__SHEET_ORIGINAL, (self.__tile_width * self.__COLUMN, self.__tile_height * self.__ROW))
            if self.IS_PIXEL
            else Images.smoothly_resize(
                self.__SHEET_ORIGINAL, (self.__tile_width * self.__COLUMN, self.__tile_height * self.__ROW)
            )
        )

    @property
    def tile_width(self) -> int:
        return self.__tile_width

    @property
    def tile_height(self) -> int:
        return self.__tile_height

    def get(self, index: int) -> ImageSurface:
        return self.__sheet.subsurface(
            index % self.__COLUMN * self.__tile_width,
            index // self.__COLUMN * self.__tile_height,
            self.__tile_width,
            self.__tile_height,
        )
