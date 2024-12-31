from collections import deque

from .layer import *


class TileMap(Coordinate):
    def __init__(self, path: str, tw: int, th: int) -> None:
        super().__init__(0, 0)
        _data: dict = Configurations.load_file(path)
        self.__PATH: str = path
        # load tile sets assets information
        dirname: str = os.path.dirname(os.path.abspath(self.__PATH))
        self.__tile_sets: tuple[TileSet, ...] = tuple(self.__new_tile_set(dirname, t) for t in reversed(_data["tilesets"]))
        # pre-allocated space for map
        self.__layers: tuple[Layer, ...] = tuple(Layer(l, self.__tile_sets) for l in _data["layers"])
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
        # entities list
        self.__entities: deque[Entity] = deque()
        # entities layer id
        self.__entities_layer_id: int = self.__layers[-1].id

    @property
    def layers(self) -> tuple[Layer, ...]:
        return self.__layers

    # set the id of the layer that represents entities layer
    def set_entities_layer(self, layer_id: int) -> None:
        self.__entities_layer_id = layer_id

    @staticmethod
    def __new_tile_set(dirname: str, data: dict[str, str | int]) -> TileSet:
        tile_source: str = str(data["source"])
        is_system: bool = tile_source.startswith(":")
        return TileSet(int(data["firstgid"]), is_system, tile_source if is_system else os.path.join(dirname, tile_source))

    @property
    def tile_width(self) -> int:
        return self.__tile_width

    @property
    def tile_height(self) -> int:
        return self.__tile_height

    # add an entity to map
    def add_entity(self, e: Entity) -> None:
        self.__entities.append(e)

    # the local so given x, y will be in the middle of the screen
    def set_focus(self, surface: ImageSurface, x: number, y: number) -> None:
        self.set_pos(
            round((-x - 1) * self.scale * self.__tile_width / 100 + surface.width / 2),
            round((-y - 1) * self.scale * self.__tile_height / 100 + surface.height / 2),
        )

    # print map to surface
    def print(self, surface: ImageSurface) -> None:
        # update tile size
        self.__current_tile_width = self.scale * self.__tile_width // 100
        self.__current_tile_height = self.scale * self.__tile_height // 100
        # render map layers
        for l in self.__layers:
            l.set_tile_size(self.__current_tile_width, self.__current_tile_height)
            l.render(surface, self.get_pos())
            if l.id != self.__entities_layer_id:
                continue
            # render entities
            for e in self.__entities:
                e.set_tile_size(self.__current_tile_width, self.__current_tile_height)
                e.render(surface, self.get_pos())
