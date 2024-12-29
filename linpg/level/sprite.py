from ..dialogue import *


@dataclass(frozen=True)
class SpriteTileAnimationFrame:
    duration: int
    tile_id: int


class SpriteTileAnimation:
    def __init__(self, data: dict[str, Any]):
        self.__frames: Final[tuple[SpriteTileAnimationFrame, ...]] = tuple(
            SpriteTileAnimationFrame(d["duration"], d["tileid"]) for d in data["animation"]
        )
        self.__start_id: Final[int] = int(data["id"])
        self.__start_index: Final[int] = next(
            (i for i in range(len(self.__frames)) if self.__frames[i].tile_id == self.__start_id), -1
        )
        self.__type: Final[str] = str(data["type"])

    @property
    def type(self) -> str:
        return self.__type

    @property
    def start_index(self) -> int:
        return self.__start_index

    @property
    def frames(self) -> tuple[SpriteTileAnimationFrame, ...]:
        return self.__frames


class SpriteTileAnimator:
    def __init__(self) -> None:
        self.__frame_index: int = 0
        self.__frame_time_ms: int = 0

    def reset(self) -> None:
        self.__frame_index = 0
        self.__frame_time_ms = 0

    def tick(self, animation: SpriteTileAnimation) -> None:
        self.__frame_time_ms += Display.get_delta_time()
        the_duration: int = animation.frames[self.__frame_index].duration
        if self.__frame_time_ms > the_duration:
            self.__frame_time_ms -= the_duration
            self.__frame_index += 1
            if self.__frame_index >= len(animation.frames):
                self.__frame_index = animation.start_index

    def get_frame_id(self, animation: SpriteTileAnimation) -> int:
        return animation.frames[self.__frame_index].tile_id


class SpriteImage:
    IS_PIXEL: bool = True

    def __init__(self, metadata_path: str) -> None:
        # path of meta metadata
        self.__METADATA_PATH: Final[str] = metadata_path
        # metadata
        self.__METADATA: Final[dict[str, Any]] = Configurations.load_file(self.__METADATA_PATH)
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
        # animations
        self.__animations: dict[str, SpriteTileAnimation] = {}
        for d in self.__METADATA.get("tiles", tuple()):
            _animation: SpriteTileAnimation = SpriteTileAnimation(d)
            self.__animations[_animation.type] = _animation

    def get_animation(self, name: str) -> SpriteTileAnimation:
        return self.__animations[name]

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
