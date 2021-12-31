from .weather import *

# 战斗系统接口，请勿实例化
class AbstractBattleSystem(AbstractGameSystem):
    def __init__(self) -> None:
        super().__init__()
        # 用于判断是否移动屏幕的参数
        self.__mouse_move_temp_x: int = -1
        self.__mouse_move_temp_y: int = -1
        self._screen_to_move_x: int = None
        self._screen_to_move_y: int = None
        # 是否是死亡的那个
        self.the_dead_one: dict = {}
        # 用于检测是否有方向键被按到的字典
        self.__pressKeyToMove: dict = {"up": False, "down": False, "left": False, "right": False}
        # 角色数据
        self.alliances_data: dict = {}
        self.enemies_data: dict = {}
        # 地图数据
        self._MAP: MapObject = MapObject()
        # 方格标准尺寸
        self._standard_block_width: int = int(Display.get_width() / 10)
        self._standard_block_height: int = int(Display.get_height() / 10)
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
        return self.get_data_of_parent_game_system() | self._MAP.to_dict()

    # 初始化地图
    def _initialize_map(self, map_data: dict) -> None:
        self._MAP.update(map_data, self._standard_block_width, self._standard_block_height)

    # 计算光亮区域 并初始化地图
    def _calculate_darkness(self) -> None:
        self._MAP.calculate_darkness(self.alliances_data)

    # 展示地图
    def _display_map(self, screen: ImageSurface) -> None:
        self._check_if_move_screen()
        self._move_screen()
        self._screen_to_move_x, self._screen_to_move_y = self._MAP.display_map(
            screen, self._screen_to_move_x, self._screen_to_move_y
        )

    # 展示场景装饰物
    def _display_decoration(self, screen: ImageSurface) -> None:
        self._MAP.display_decoration(screen, self.alliances_data, self.enemies_data)

    # 初始化角色加载器并启动加载器线程
    def _start_loading_characters(self, alliancesData: dict, enemiesData: dict, mode: str = "default") -> None:
        self.__characterDataLoaderThread = CharacterDataLoader(alliancesData, enemiesData, mode)
        self.__characterDataLoaderThread.start()

    # 是否角色加载器还在运行
    def _is_characters_loader_alive(self) -> bool:
        if self.__characterDataLoaderThread.is_alive():
            return True
        else:
            self.alliances_data, self.enemies_data = self.__characterDataLoaderThread.getResult()
            del self.__characterDataLoaderThread
            return False

    @property
    def characters_loaded(self) -> int:
        return self.__characterDataLoaderThread.currentID

    @property
    def characters_total(self) -> int:
        return self.__characterDataLoaderThread.totalNum

    # 检测按下按键的事件
    def _check_key_down(self, event: pygame.event.Event) -> None:
        if event.key == Key.ARROW_UP:
            self.__pressKeyToMove["up"] = True
        elif event.key == Key.ARROW_DOWN:
            self.__pressKeyToMove["down"] = True
        elif event.key == Key.ARROW_LEFT:
            self.__pressKeyToMove["left"] = True
        elif event.key == Key.ARROW_RIGHT:
            self.__pressKeyToMove["right"] = True
        elif event.unicode == "p":
            self._MAP.dev_mode()

    # 检测按键回弹的事件
    def _check_key_up(self, event: pygame.event.Event) -> None:
        if event.key == Key.ARROW_UP:
            self.__pressKeyToMove["up"] = False
        elif event.key == Key.ARROW_DOWN:
            self.__pressKeyToMove["down"] = False
        elif event.key == Key.ARROW_LEFT:
            self.__pressKeyToMove["left"] = False
        elif event.key == Key.ARROW_RIGHT:
            self.__pressKeyToMove["right"] = False

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
            self.__pressKeyToMove["up"] = bool(round(Controller.joystick.get_axis(4)) == -1)
            self.__pressKeyToMove["down"] = bool(round(Controller.joystick.get_axis(4)) == 1)
            self.__pressKeyToMove["right"] = bool(round(Controller.joystick.get_axis(3)) == 1)
            self.__pressKeyToMove["left"] = bool(round(Controller.joystick.get_axis(3)) == -1)

    # 检测并处理屏幕移动事件
    def _check_if_move_screen(self) -> None:
        # 根据按键情况设定要移动的数值
        if self.__pressKeyToMove["up"] is True:
            if self._screen_to_move_y is None:
                self._screen_to_move_y = int(self._MAP.block_height / 4)
            else:
                self._screen_to_move_y += int(self._MAP.block_height / 4)
        if self.__pressKeyToMove["down"] is True:
            if self._screen_to_move_y is None:
                self._screen_to_move_y = int(-self._MAP.block_height / 4)
            else:
                self._screen_to_move_y -= int(self._MAP.block_height / 4)
        if self.__pressKeyToMove["left"] is True:
            if self._screen_to_move_x is None:
                self._screen_to_move_x = int(self._MAP.block_width / 4)
            else:
                self._screen_to_move_x += int(self._MAP.block_width / 4)
        if self.__pressKeyToMove["right"] is True:
            if self._screen_to_move_x is None:
                self._screen_to_move_x = int(-self._MAP.block_width / 4)
            else:
                self._screen_to_move_x -= int(self._MAP.block_width / 4)

    def _move_screen(self) -> None:
        # 如果需要移动屏幕
        if self._screen_to_move_x is not None and self._screen_to_move_x != 0:
            temp_value: int
            if (
                Display.get_width() - self._MAP.get_width()
                <= (temp_value := int(self._MAP.get_local_x() + self._screen_to_move_x * 0.2))
                <= 0
            ):
                self._MAP.set_local_x(temp_value)
                self._screen_to_move_x = int(self._screen_to_move_x * 0.8)
                if self._screen_to_move_x == 0:
                    self._screen_to_move_x = 0
            else:
                self._screen_to_move_x = 0
        if self._screen_to_move_y is not None and self._screen_to_move_y != 0:
            if (
                Display.get_height() - self._MAP.get_height()
                <= (temp_value := int(self._MAP.get_local_y() + self._screen_to_move_y * 0.2))
                <= 0
            ):
                self._MAP.set_local_y(temp_value)
                self._screen_to_move_y = int(self._screen_to_move_y * 0.8)
                if self._screen_to_move_y == 0:
                    self._screen_to_move_y = 0
            else:
                self._screen_to_move_y = 0
