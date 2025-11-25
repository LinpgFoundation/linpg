from .entity import *


class TileSet(NamedTuple):
    first_gid: int
    is_system: bool
    source: str


class Chunk(Rectangle):
    def __init__(self, data: dict[str, Any], tile_sets: tuple[TileSet, ...]) -> None:
        super().__init__(data["x"], data["y"], data["width"], data["height"])
        self.__data: numpy.ndarray = numpy.array(data["data"], dtype=numpy.uint).reshape(self.height, self.width)
        self.__surface: StaticImage | None = None
        self.__tile_sets: tuple[TileSet, ...] = tile_sets
        self.__tile_size: tuple[int, int] = (0, 0)

    def get_tile(self, x: int, y: int) -> int:
        return int(self.__data[y - self.y, x - self.x])

    def set_tile_size(self, w: int, h: int) -> None:
        if w != self.__tile_size[0] or h != self.__tile_size[1]:
            self.__tile_size = (w, h)
            self.__surface = None

    # given tile id, draw the tile to position
    def __draw_tile(self, surface: ImageSurface, x: int, y: int) -> None:
        for tile_set in self.__tile_sets:
            # calculate the relevant id for current tile set
            absId: int = int(self.__data[y, x]) - tile_set.first_gid
            # a negative id means we are not there yet
            if absId < 0:
                continue
            # no need to render sources that start with colon
            if tile_set.source.startswith(":"):
                break
            # get the sheet
            sprit_sheet: SpriteImage = AssetsManager.get_sprite(tile_set.source)
            sprit_sheet.set_size(self.__tile_size[0], self.__tile_size[1])
            # and render it
            surface.blit(sprit_sheet.get(absId), Coordinates.multiply((x, y), self.__tile_size))
            break

    def render(self, surface: ImageSurface, pos: tuple[int, int]) -> None:
        # if surface is None, then a new one needs to be generated
        if self.__surface is None:
            new_surface = Surfaces.transparent(Coordinates.multiply(self.__tile_size, self.size))
            # Iterate through the non-zero elements
            for y, x in numpy.argwhere(self.__data):
                self.__draw_tile(new_surface, int(x), int(y))
            self.__surface = StaticImage(new_surface, enable_cropping=True, is_pixelated=SpriteImage.IS_PIXELATED)
        # render the chuck image
        self.__surface.set_pos(pos[0], pos[1])
        self.__surface.display(surface, Coordinates.multiply(self.pos, self.__tile_size))


class Layer(Hidable):
    def __init__(self, data: dict[str, Any], tile_sets: tuple[TileSet, ...]) -> None:
        super().__init__(data["visible"])
        self.__name: Final[str] = data["name"]
        self.__id: Final[int] = data["id"]
        self.__tile_width: int = 0
        self.__tile_height: int = 0
        self.__chunks: tuple[Chunk, ...] = tuple(Chunk(d, tile_sets) for d in reversed(data["chunks"]))

    @property
    def name(self) -> str:
        return self.__name

    @property
    def id(self) -> int:
        return self.__id

    def get_tile(self, x: int, y: int) -> int:
        the_chuck: Chunk | None = next((c for c in self.__chunks if x >= c.x and y >= c.y), None)
        return 0 if the_chuck is None else the_chuck.get_tile(x, y)

    def set_tile_size(self, w: int, h: int) -> None:
        self.__tile_width = w
        self.__tile_height = h

    def render(self, surface: ImageSurface, pos: tuple[int, int]) -> None:
        # no need to render layer if it has been hidden
        if self.is_hidden():
            return
        # render all the chucks in this layer
        for c in self.__chunks:
            c.set_tile_size(self.__tile_width, self.__tile_height)
            c.render(surface, pos)
