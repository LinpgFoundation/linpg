import math
from collections import deque

from .entity import *


class _TileSet:
    def __init__(self, dirname: str, data: dict[str, str | int]):
        self.first_gid: Final[int] = int(data["firstgid"])
        tile_source: str = str(data["source"])
        self.is_system: Final[bool] = tile_source.startswith(":")
        self.source: Final[str] = tile_source if self.is_system else os.path.join(dirname, tile_source)


class TileMap(SurfaceWithLocalPos):

    __SHEETS: dict[str, SpriteImage] = {}

    def __init__(self, _path: str, tw: int, th: int) -> None:
        super().__init__()
        _data: dict = Configurations.load_file(_path)
        self.__PATH: str = _path
        self.__row = 0
        self.__column = 0
        self.__minX = 0
        self.__minY = 0
        dirname: str = os.path.dirname(os.path.abspath(self.__PATH))
        self.__tile_sets: tuple[_TileSet, ...] = tuple(_TileSet(dirname, t) for t in reversed(_data["tilesets"]))
        layers: list[dict] = _data["layers"]
        for _layer in layers:
            self.__row = max(self.__row, _layer["height"])
            self.__column = max(self.__column, _layer["width"])
            self.__minX = min(self.__minX, _layer["startx"]) if _layer["startx"] is not None else min(self.__minX, _layer["x"])
            self.__minY = min(self.__minY, _layer["starty"]) if _layer["starty"] is not None else min(self.__minX, _layer["y"])
        # pre-allocated space for map
        self.__MAP = numpy.zeros((self.__row, self.__column, len(layers)), numpy.int32)
        for i in range(len(layers)):
            _layer = layers[i]
            if _layer["chunks"] is not None:
                for c in _layer["chunks"]:
                    self.__process_chunk(c, i)
            else:
                self.__process_chunk(_layer, i)
        # the default tile width
        self.__tile_width: int = tw
        # the default tile height, using default tile width by default
        self.__tile_height: int = th
        # the current tile width
        self.__current_tile_width: int = self.__tile_width
        # the current tile height
        self.__current_tile_height: int = self.__tile_height
        # scale value in percentage
        self.scale: int = 100
        # using as temp coordinates for calculating abs coordinates
        self.__left: int = 0
        self.__top: int = 0
        # entities list
        self.__entities: deque[Entity] = deque()

    def get_left(self) -> int:
        return self.__left

    def get_top(self) -> int:
        return self.__top

    @property
    def tile_width(self) -> int:
        return self.__tile_width

    @property
    def tile_height(self) -> int:
        return self.__tile_height

    def __process_chunk(self, _chunk: dict, index: int) -> None:
        chunk_width = int(_chunk["width"])
        for i in range(len(_chunk["data"])):
            x = _chunk["x"] - self.__minX + i % chunk_width
            y = _chunk["y"] - self.__minY + math.floor(i / chunk_width)
            self.__MAP[y, x][index] = _chunk["data"][i]

    def __draw_sprit(self, surface: ImageSurface, sprit_sheet: SpriteImage, x: number, y: number, index: int) -> None:
        sprit_sheet.set_size(self.__current_tile_width, self.__current_tile_height)
        self.__left = int(x * self.__current_tile_width)
        self.__top = int(y * self.__current_tile_height)
        surface.blit(sprit_sheet.get(index), self.get_abs_pos())

    def __get_sheet(self, p: str) -> SpriteImage:
        if p not in self.__SHEETS:
            self.__SHEETS[p] = SpriteImage(p)
        return self.__SHEETS[p]

    def __draw_tile(self, surface: ImageSurface, _id: int, x: int, y: int) -> None:
        for tile_set in self.__tile_sets:
            absId: int = _id - tile_set.first_gid
            if absId < 0:
                continue
            tile_source: str = tile_set.source
            if tile_source.startswith(":"):
                break
            self.__draw_sprit(surface, self.__get_sheet(tile_source), x, y, absId)
            break

    def add_entity(self, e: Entity) -> None:
        self.__entities.append(e)

    def print(self, surface: ImageSurface) -> None:
        xStart = 0
        yStart = 0
        xEndExclude = self.__column
        yEndExclude = self.__row
        self.__current_tile_width = self.scale * self.__tile_width // 100
        self.__current_tile_height = self.scale * self.__tile_height // 100
        for y in range(yStart, yEndExclude):
            for x in range(xStart, xEndExclude):
                currentTile = self.__MAP[y, x]
                for l in currentTile:
                    self.__draw_tile(surface, l, x, y)
        for e in self.__entities:
            _sheet: SpriteImage = self.__get_sheet(e.src)
            self.__draw_sprit(surface, _sheet, e.x, e.y, e.get_current_frame_id(_sheet))
