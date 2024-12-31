from .assets import *


class Entity(Position):
    def __init__(self, src: str, x: number, y: number) -> None:
        super().__init__(x, y)
        self.__source: str = src
        self.__animator: SpriteTileAnimator = SpriteTileAnimator()
        self.__current_animation: str | None = None
        self.__tile_width: int = 0
        self.__tile_height: int = 0

    def set_tile_size(self, w: int, h: int) -> None:
        self.__tile_width = w
        self.__tile_height = h

    def _set_animation(self, new_animation: str) -> None:
        if self.__current_animation == new_animation:
            return
        self.__current_animation = new_animation
        self.__animator.reset()

    def render(self, surface: ImageSurface, pos: tuple[int, int]) -> None:
        # obtain the sheet
        sheet: SpriteImage = AssetsManager.get_sprite(self.__source)
        # update sheet size
        sheet.set_size(self.__tile_width, self.__tile_height)
        # get the frame id that represent the frame of current animation
        current_frame_id: int = 0
        if self.__current_animation is not None:
            _animation: SpriteTileAnimation = sheet.get_animation(self.__current_animation)
            self.__animator.tick(_animation)
            current_frame_id = self.__animator.get_frame_id(_animation)
        # blit the frame to surface
        surface.blit(
            sheet.get(current_frame_id),
            Coordinates.add((int((self.x - 0.5) * self.__tile_width), int((self.y - 1) * self.__tile_height)), pos),
        )
