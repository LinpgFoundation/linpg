from .tilemap import *


class Level:
    __MAX_SCALE: Final[int] = 1000
    __MIN_SCALE: Final[int] = 10

    def __init__(self, path: str, tw: int, th: int = 0):
        self.__movement: DynamicMovementController = DynamicMovementController()
        self.__map: TileMap = TileMap(path, tw, th if th > 0 else tw)
        # prev mouse hover location if pressed
        self.__prev_mouse_hover_x: int | None = None
        self.__prev_mouse_hover_y: int | None = None

    # check key down events
    def _check_key_down(self, event: Event) -> None:
        if event.key == Keys.ARROW_UP:
            self.__movement.move(Directions.UP, True)
        elif event.key == Keys.ARROW_DOWN:
            self.__movement.move(Directions.DOWN, True)
        elif event.key == Keys.ARROW_LEFT:
            self.__movement.move(Directions.LEFT, True)
        elif event.key == Keys.ARROW_RIGHT:
            self.__movement.move(Directions.RIGHT, True)

    # check key up events
    def _check_key_up(self, event: Event) -> None:
        if event.key == Keys.ARROW_UP:
            self.__movement.move(Directions.UP, False)
        elif event.key == Keys.ARROW_DOWN:
            self.__movement.move(Directions.DOWN, False)
        elif event.key == Keys.ARROW_LEFT:
            self.__movement.move(Directions.LEFT, False)
        elif event.key == Keys.ARROW_RIGHT:
            self.__movement.move(Directions.RIGHT, False)

    @property
    def map(self) -> TileMap:
        return self.__map

    def print(self, surface: ImageSurface) -> None:
        # using scroll to scale map
        if Controller.get_event("scroll_up"):
            self.__map.scale = min(self.__map.scale + 10, self.__MAX_SCALE)
        elif Controller.get_event("scroll_down"):
            self.__map.scale = max(self.__map.scale - 10, self.__MIN_SCALE)
        # handel events
        for event in Controller.get_events():
            if event.type == Events.KEY_DOWN:
                self._check_key_down(event)
            elif event.type == Events.KEY_UP:
                self._check_key_up(event)
        # update map movement
        self.__movement.tick()
        # if player choose to move map using mouse
        if Controller.mouse.get_pressed(2):
            if self.__prev_mouse_hover_x is None or self.__prev_mouse_hover_y is None:
                self.__prev_mouse_hover_x = Controller.mouse.x
                self.__prev_mouse_hover_y = Controller.mouse.y
            elif self.__prev_mouse_hover_x != Controller.mouse.x or self.__prev_mouse_hover_y != Controller.mouse.y:
                if self.__prev_mouse_hover_x != Controller.mouse.x:
                    self.__map.move_left(self.__prev_mouse_hover_x - Controller.mouse.x)
                if self.__prev_mouse_hover_y != Controller.mouse.y:
                    self.__map.move_upward(self.__prev_mouse_hover_y - Controller.mouse.y)
                self.__prev_mouse_hover_x = Controller.mouse.x
                self.__prev_mouse_hover_y = Controller.mouse.y
        else:
            self.__prev_mouse_hover_x = None
            self.__prev_mouse_hover_y = None
        # update map location
        self.__map.move_right(self.__movement.current_horizontal_speed)
        self.__map.move_downward(self.__movement.current_vertical_speed)
        # render map
        self.__map.print(surface)
