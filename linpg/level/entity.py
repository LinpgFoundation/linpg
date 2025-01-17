from .assets import *


# basic entity object
class Entity(Position):
    def __init__(self, src: str, x: number, y: number) -> None:
        super().__init__(x, y)
        self.__source: str = src
        self.__animator: SpriteTileAnimator = SpriteTileAnimator()
        self.__movement: DynamicMovementController = DynamicMovementController()
        self.__current_animation: str | None = None
        self.__current_frame: None | ImageSurface = None
        self._tile_width: int = 0
        self._tile_height: int = 0

    # child get movement controller
    @property
    def _movement(self) -> DynamicMovementController:
        return self.__movement

    # is entity moving
    def is_moving(self) -> bool:
        return self.__movement.is_moving()

    def set_tile_size(self, w: int, h: int) -> None:
        self._tile_width = w
        self._tile_height = h

    def _set_animation(self, new_animation: str) -> None:
        if self.__current_animation == new_animation:
            return
        self.__current_animation = new_animation
        self.__animator.reset()

    # obtain the current frame
    def _get_current_frame(self) -> ImageSurface:
        # obtain the sheet
        sheet: SpriteImage = AssetsManager.get_sprite(self.__source)
        # update sheet size
        sheet.set_size(self._tile_width, self._tile_height)
        # get the frame id that represent the frame of current animation
        current_frame_id: int = 0
        if self.__current_animation is not None:
            _animation: SpriteTileAnimation = sheet.get_animation(self.__current_animation)
            self.__animator.tick(_animation)
            current_frame_id = self.__animator.get_frame_id(_animation)
        return sheet.get(current_frame_id)

    # get the current frame image surface
    @property
    def current_frame(self) -> ImageSurface:
        # if the current frame has not been generated yet, then do it
        if self.__current_frame is None:
            self.__current_frame = self._get_current_frame()
        # return the frame image
        return self.__current_frame

    def render(self, surface: ImageSurface, pos: tuple[int, int]) -> None:
        # blit the frame to surface
        surface.blit(
            self.current_frame,
            Coordinates.add((int((self.x - 0.5) * self._tile_width), int((self.y - 1) * self._tile_height)), pos),
        )
        # reset current frame
        self.__current_frame = None


# creature, basically entity with health
class Creature(Entity):
    def __init__(self, src: str, x: number, y: number) -> None:
        super().__init__(src, x, y)
        # creature's max health
        self.__max_health: int = 1
        # creature's current health
        self.__current_health: int = 1
        # whether the creature is invincible, which means it will not take any damage
        self.__is_invincible: bool = False

    # is creature still alive
    def is_alive(self) -> bool:
        return self.__current_health > 0

    # creature's current hp
    @property
    def current_health(self) -> int:
        return self.__current_health

    # creature's max hp
    @property
    def max_health(self) -> int:
        return self.__max_health

    # creature's hp percentage
    @property
    def health_percentage(self) -> float:
        return round(self.__current_health / self.__max_health, 5)

    # increase health (child can rewrite)
    def _heal(self, health: int) -> None:
        self.__current_health += health

    # heal creature (should not be rewritten)
    def heal(self, health: int) -> None:
        if health < 0:
            Exceptions.fatal("You cannot heal a negative value")
        self._heal(health)

    # decrease health (child can rewrite)
    def _injure(self, damage: int) -> None:
        self.__current_health -= damage

    # deal damage to creature (should not be rewritten)
    def injure(self, damage: int) -> None:
        # if the damage taken are 0 or the entity is invincible
        if damage == 0 or self.__is_invincible:
            return
        # throw error if the damage is negative
        if damage < 0:
            Exceptions.fatal("A negative damage is not allowed!")
        # taking damage
        self._injure(damage)
