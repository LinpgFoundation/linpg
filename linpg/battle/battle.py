from .weather import *

# 战斗系统接口，请勿实例化
class AbstractBattleSystem(AbstractGameSystem):
    def __init__(self) -> None:
        super().__init__()
        # 用于判断是否移动屏幕的参数
        self.__mouse_move_temp_x: int = -1
        self.__mouse_move_temp_y: int = -1
        self._screen_to_move_x: Optional[int] = None
        self._screen_to_move_y: Optional[int] = None
        # 用于检测是否有方向键被按到的字典
        self.__moving_screen_in_direction: dict[str, bool] = {"up": False, "down": False, "left": False, "right": False}
        # 角色数据
        self._alliances_data: dict[str, Entity] = {}
        self._enemies_data: dict[str, Entity] = {}
        # 地图数据
        self._MAP: MapObject = MapObject()
        # 方格标准尺寸
        self._standard_block_width: int = Display.get_width() // 10
        self._standard_block_height: int = Display.get_height() // 10
        # 天气系统
        self._weather_system: WeatherSystem = WeatherSystem()

    # 获取对话文件所在的具体路径
    def get_map_file_location(self) -> str:
        return (
            os.path.join("Data", self._chapter_type, "chapter{0}_map.{1}".format(self._chapter_id, Config.get_file_type()))
            if self._project_name is None
            else os.path.join(
                "Data",
                self._chapter_type,
                self._project_name,
                "chapter{0}_map.{1}".format(self._chapter_id, Config.get_file_type()),
            )
        )

    # 返回需要保存数据
    def _get_data_need_to_save(self) -> dict:
        _data: dict = {"alliances": {}, "enemies": {}}
        for key in self._alliances_data:
            _data["alliances"][key] = self._alliances_data[key].to_dict()
        for key in self._enemies_data:
            _data["enemies"][key] = self._enemies_data[key].to_dict()
        _data.update(self.get_data_of_parent_game_system())
        _data.update(self._MAP.to_dict())
        return _data

    # 初始化地图
    def _initialize_map(self, map_data: dict) -> None:
        self._MAP.update(map_data, self._standard_block_width, self._standard_block_height)

    # 计算光亮区域 并初始化地图
    def _calculate_darkness(self) -> None:
        self._MAP.calculate_darkness(self._alliances_data)

    # 展示地图
    def _display_map(self, screen: ImageSurface) -> None:
        self._check_if_move_screen()
        self._move_screen()
        _x: int = self._screen_to_move_x if self._screen_to_move_x is not None else 0
        _y: int = self._screen_to_move_y if self._screen_to_move_y is not None else 0
        self._screen_to_move_x, self._screen_to_move_y = self._MAP.display_map(screen, _x, _y)

    # 展示场景装饰物
    def _display_decoration(self, screen: ImageSurface) -> None:
        self._MAP.display_decoration(screen, self._alliances_data, self._enemies_data)

    # 检测按下按键的事件
    def _check_key_down(self, event: PG_Event) -> None:
        if event.key == Key.ARROW_UP:
            self.__moving_screen_in_direction["up"] = True
        elif event.key == Key.ARROW_DOWN:
            self.__moving_screen_in_direction["down"] = True
        elif event.key == Key.ARROW_LEFT:
            self.__moving_screen_in_direction["left"] = True
        elif event.key == Key.ARROW_RIGHT:
            self.__moving_screen_in_direction["right"] = True
        elif event.unicode == "p":
            self._MAP.dev_mode()

    # 检测按键回弹的事件
    def _check_key_up(self, event: PG_Event) -> None:
        if event.key == Key.ARROW_UP:
            self.__moving_screen_in_direction["up"] = False
        elif event.key == Key.ARROW_DOWN:
            self.__moving_screen_in_direction["down"] = False
        elif event.key == Key.ARROW_LEFT:
            self.__moving_screen_in_direction["left"] = False
        elif event.key == Key.ARROW_RIGHT:
            self.__moving_screen_in_direction["right"] = False

    # 根据鼠标移动屏幕
    def _check_right_click_move(self) -> None:
        if Controller.mouse.get_pressed(2):
            if self.__mouse_move_temp_x == -1 and self.__mouse_move_temp_y == -1:
                self.__mouse_move_temp_x = Controller.mouse.x
                self.__mouse_move_temp_y = Controller.mouse.y
            else:
                if self.__mouse_move_temp_x != Controller.mouse.x or self.__mouse_move_temp_y != Controller.mouse.y:
                    if self.__mouse_move_temp_x != Controller.mouse.x:
                        self._MAP.add_local_x(self.__mouse_move_temp_x - Controller.mouse.x)
                    if self.__mouse_move_temp_y != Controller.mouse.y:
                        self._MAP.add_local_y(self.__mouse_move_temp_y - Controller.mouse.y)
                    self.__mouse_move_temp_x = Controller.mouse.x
                    self.__mouse_move_temp_y = Controller.mouse.y
        else:
            self.__mouse_move_temp_x = -1
            self.__mouse_move_temp_y = -1

    # 检测手柄事件
    def _check_jostick_events(self) -> None:
        if Controller.joystick.get_init():
            self.__moving_screen_in_direction["up"] = bool(round(Controller.joystick.get_axis(4)) == -1)
            self.__moving_screen_in_direction["down"] = bool(round(Controller.joystick.get_axis(4)) == 1)
            self.__moving_screen_in_direction["right"] = bool(round(Controller.joystick.get_axis(3)) == 1)
            self.__moving_screen_in_direction["left"] = bool(round(Controller.joystick.get_axis(3)) == -1)

    # 检测并处理屏幕移动事件
    def _check_if_move_screen(self) -> None:
        # 根据按键情况设定要移动的数值
        if self.__moving_screen_in_direction["up"] is True:
            if self._screen_to_move_y is None:
                self._screen_to_move_y = self._MAP.block_height // 4
            else:
                self._screen_to_move_y += self._MAP.block_height // 4
        if self.__moving_screen_in_direction["down"] is True:
            if self._screen_to_move_y is None:
                self._screen_to_move_y = -self._MAP.block_height // 4
            else:
                self._screen_to_move_y -= self._MAP.block_height // 4
        if self.__moving_screen_in_direction["left"] is True:
            if self._screen_to_move_x is None:
                self._screen_to_move_x = self._MAP.block_width // 4
            else:
                self._screen_to_move_x += self._MAP.block_width // 4
        if self.__moving_screen_in_direction["right"] is True:
            if self._screen_to_move_x is None:
                self._screen_to_move_x = -self._MAP.block_width // 4
            else:
                self._screen_to_move_x -= self._MAP.block_width // 4

    def _move_screen(self) -> None:
        # 如果需要移动屏幕
        temp_value: int = 0
        if self._screen_to_move_x is not None and self._screen_to_move_x != 0:
            temp_value = self._MAP.get_local_x() + self._screen_to_move_x // 5
            if Display.get_width() - self._MAP.get_width() <= temp_value <= 0:
                self._MAP.set_local_x(temp_value)
                self._screen_to_move_x = self._screen_to_move_x * 4 // 5
                if self._screen_to_move_x == 0:
                    self._screen_to_move_x = 0
            else:
                self._screen_to_move_x = 0
        if self._screen_to_move_y is not None and self._screen_to_move_y != 0:
            temp_value = self._MAP.get_local_y() + self._screen_to_move_y // 5
            if Display.get_height() - self._MAP.get_height() <= temp_value <= 0:
                self._MAP.set_local_y(temp_value)
                self._screen_to_move_y = self._screen_to_move_y * 4 // 5
                if self._screen_to_move_y == 0:
                    self._screen_to_move_y = 0
            else:
                self._screen_to_move_y = 0
