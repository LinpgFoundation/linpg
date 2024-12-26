from ..dialogue import *


class SpriteImage:
    def __init__(self, metadata_path: str) -> None:
        # path of meta metadata
        self.__METADATA_PATH: Final[str] = metadata_path
        # metadata
        self.__METADATA: Final[dict[str, str | int]] = Configurations.load_file(self.__METADATA_PATH)
        # load tile sheet
        self.__SHEET: Final[ImageSurface] = Images.quickly_load(
            os.path.join(os.path.dirname(self.__METADATA_PATH), str(self.__METADATA["image"]))
        )
        # get columns
        self.__COLUMN: Final[int] = int(self.__METADATA["columns"])
        # tile height
        self.__TILE_HEIGHT: Final[int] = int(self.__METADATA["tileheight"])
        # tile width
        self.__TILE_WIDTH: Final[int] = int(self.__METADATA["tilewidth"])

    @property
    def tile_width(self) -> int:
        return self.__TILE_WIDTH

    @property
    def tile_height(self) -> int:
        return self.__TILE_HEIGHT

    def get(self, index: int) -> ImageSurface:
        return self.__SHEET.subsurface(
            index % self.__COLUMN * self.__TILE_WIDTH,
            index // self.__COLUMN * self.__TILE_HEIGHT,
            self.__TILE_WIDTH,
            self.__TILE_HEIGHT,
        )
