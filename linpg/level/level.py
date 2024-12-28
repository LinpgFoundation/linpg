from .tilemap import *


class Level:
    __MAX_SCALE: Final[int] = 1000
    __MIN_SCALE: Final[int] = 10

    def __init__(self, path: str, tw: int, th: int = 0):
        self.__map = TileMap(path, tw, th if th > 0 else tw)
        # speed for moving map
        self.__vertical_speed: int = 0
        self.__horizontal_speed: int = 0
        # whether to move screen to a certain direction
        self.__moving_screen_in_direction_up: bool = False
        self.__moving_screen_in_direction_down: bool = False
        self.__moving_screen_in_direction_left: bool = False
        self.__moving_screen_in_direction_right: bool = False
        # prev mouse hover location if pressed
        self.__prev_mouse_hover_x: int | None = None
        self.__prev_mouse_hover_y: int | None = None

    # check key down events
    def _check_key_down(self, event: Event) -> None:
        if event.key == Keys.ARROW_UP:
            self.__moving_screen_in_direction_up = True
        elif event.key == Keys.ARROW_DOWN:
            self.__moving_screen_in_direction_down = True
        elif event.key == Keys.ARROW_LEFT:
            self.__moving_screen_in_direction_left = True
        elif event.key == Keys.ARROW_RIGHT:
            self.__moving_screen_in_direction_right = True

    # check key up events
    def _check_key_up(self, event: Event) -> None:
        if event.key == Keys.ARROW_UP:
            self.__moving_screen_in_direction_up = False
        elif event.key == Keys.ARROW_DOWN:
            self.__moving_screen_in_direction_down = False
        elif event.key == Keys.ARROW_LEFT:
            self.__moving_screen_in_direction_left = False
        elif event.key == Keys.ARROW_RIGHT:
            self.__moving_screen_in_direction_right = False

    # move screen location according to speed
    def __update_map_movements(self)-> None:
        # move speed closer to 0
        if self.__horizontal_speed > 0:
            self.__horizontal_speed -= 1
        elif self.__horizontal_speed < 0:
            self.__horizontal_speed += 1
        if self.__vertical_speed > 0:
            self.__vertical_speed -= 1
        elif self.__vertical_speed < 0:
            self.__vertical_speed += 1
        # restore speed if continue to move
        if self.__moving_screen_in_direction_up:
            self.__vertical_speed = 10
        if self.__moving_screen_in_direction_down:
            self.__vertical_speed = -10
        if self.__moving_screen_in_direction_left:
            self.__horizontal_speed = 10
        if self.__moving_screen_in_direction_right:
            self.__horizontal_speed = -10

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
        self.__update_map_movements()
        # if player choose to move map using mouse
        if Controller.mouse.get_pressed(2):
            if self.__prev_mouse_hover_x is None and self.__prev_mouse_hover_y is None:
                self.__prev_mouse_hover_x = Controller.mouse.x
                self.__prev_mouse_hover_y = Controller.mouse.y
            elif self.__prev_mouse_hover_x != Controller.mouse.x or self.__prev_mouse_hover_y != Controller.mouse.y:
                if self.__prev_mouse_hover_x != Controller.mouse.x:
                    self.__map.add_local_x(self.__prev_mouse_hover_x - Controller.mouse.x)
                if self.__prev_mouse_hover_y != Controller.mouse.y:
                    self.__map.add_local_y(self.__prev_mouse_hover_y - Controller.mouse.y)
                self.__prev_mouse_hover_x = Controller.mouse.x
                self.__prev_mouse_hover_y = Controller.mouse.y
        else:
            self.__prev_mouse_hover_x = None
            self.__prev_mouse_hover_y = None
        # update map location
        self.__map.add_local_pos(self.__horizontal_speed, self.__vertical_speed)
        # render map
        self.__map.print(surface)
