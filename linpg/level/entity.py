from .sprite import *


class Entity(Position):
    def __init__(self, src: str, x: number, y: number) -> None:
        super().__init__(x, y)
        self.src: str = src
        self.__animator: SpriteTileAnimator = SpriteTileAnimator()
        self.__current_animation: str | None = None

    def _set_animation(self, new_animation: str) -> None:
        if self.__current_animation == new_animation:
            return
        self.__current_animation = new_animation
        self.__animator.reset()

    def get_current_frame_id(self, sheet: SpriteImage) -> int:
        if self.__current_animation is None:
            return 0
        _animation: SpriteTileAnimation = sheet.get_animation(self.__current_animation)
        self.__animator.tick(_animation)
        return self.__animator.get_frame_id(_animation)
