from .map import *

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
        self.__moving_screen_in_direction_up: bool = False
        self.__moving_screen_in_direction_down: bool = False
        self.__moving_screen_in_direction_left: bool = False
        self.__moving_screen_in_direction_right: bool = False
        # 角色数据
        self._entities_data: dict[str, dict[str, Entity]] = {}
        # 地图数据
        self._MAP: MapObject = MapObject()
        # 方格标准尺寸
        self._standard_block_width: int = Display.get_width() // 10
        self._standard_block_height: int = Display.get_height() // 10
        # 天气系统
        self._weather_system: WeatherSystem = WeatherSystem()
        # 当前鼠标位置上的tile块
        self._block_is_hovering: Optional[tuple[int, int]] = None

    # 渲染出所有的entity - 子类需实现
    def _display_entities(self, screen: ImageSurface) -> None:
        EXCEPTION.fatal("_display_entities()", 1)

    # 加载角色的数据 - 子类需实现
    def _load_entities(self, _entities: dict) -> None:
        EXCEPTION.fatal("_load_entities()", 1)

    # 加载地图数据
    def _load_map(self, _data: dict) -> None:
        self._MAP.update(_data, self._standard_block_width, self._standard_block_height)

    # 处理数据
    def _process_data(self, _data: dict) -> None:
        # 初始化角色信息
        self._load_entities(_data.get("entities", {}))
        # 初始化地图
        self._load_map(_data)

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
        _data: dict = {"entities": {}}
        for faction, entitiesDict in self._entities_data.items():
            _data["entities"][faction] = {}
            for key in entitiesDict:
                _data["entities"][faction][key] = entitiesDict[key].to_dict()
        _data.update(self.get_data_of_parent_game_system())
        _data.update(self._MAP.to_dict())
        return _data

    # 检测按下按键的事件
    def _check_key_down(self, event: PG_Event) -> None:
        if event.key == Key.ARROW_UP:
            self.__moving_screen_in_direction_up = True
        elif event.key == Key.ARROW_DOWN:
            self.__moving_screen_in_direction_down = True
        elif event.key == Key.ARROW_LEFT:
            self.__moving_screen_in_direction_left = True
        elif event.key == Key.ARROW_RIGHT:
            self.__moving_screen_in_direction_right = True
        elif event.unicode == "p":
            self._MAP.dev_mode()

    # 检测按键回弹的事件
    def _check_key_up(self, event: PG_Event) -> None:
        if event.key == Key.ARROW_UP:
            self.__moving_screen_in_direction_up = False
        elif event.key == Key.ARROW_DOWN:
            self.__moving_screen_in_direction_down = False
        elif event.key == Key.ARROW_LEFT:
            self.__moving_screen_in_direction_left = False
        elif event.key == Key.ARROW_RIGHT:
            self.__moving_screen_in_direction_right = False

    # 检测手柄事件
    def _check_jostick_events(self) -> None:
        self.__moving_screen_in_direction_up = round(Controller.joystick.get_axis(4)) == -1
        self.__moving_screen_in_direction_down = round(Controller.joystick.get_axis(4)) == 1
        self.__moving_screen_in_direction_right = round(Controller.joystick.get_axis(3)) == 1
        self.__moving_screen_in_direction_left = round(Controller.joystick.get_axis(3)) == -1

    # 展示地图
    def _display_map(self, screen: ImageSurface) -> None:
        # 处理鼠标事件
        for event in Controller.events:
            if event.type == Key.DOWN:
                self._check_key_down(event)
            elif event.type == Key.UP:
                self._check_key_up(event)
        # 处理手柄事件
        if Controller.joystick.get_init():
            self._check_jostick_events()
        # 检测是否使用了鼠标移动了地图的本地坐标
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
        # 根据按键情况设定要移动的数值
        if self.__moving_screen_in_direction_up is True:
            if self._screen_to_move_y is None:
                self._screen_to_move_y = self._MAP.block_height // 4
            else:
                self._screen_to_move_y += self._MAP.block_height // 4
        if self.__moving_screen_in_direction_down is True:
            if self._screen_to_move_y is None:
                self._screen_to_move_y = -self._MAP.block_height // 4
            else:
                self._screen_to_move_y -= self._MAP.block_height // 4
        if self.__moving_screen_in_direction_left is True:
            if self._screen_to_move_x is None:
                self._screen_to_move_x = self._MAP.block_width // 4
            else:
                self._screen_to_move_x += self._MAP.block_width // 4
        if self.__moving_screen_in_direction_right is True:
            if self._screen_to_move_x is None:
                self._screen_to_move_x = -self._MAP.block_width // 4
            else:
                self._screen_to_move_x -= self._MAP.block_width // 4
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
        # 展示地图
        self._screen_to_move_x, self._screen_to_move_y = self._MAP.display_map(
            screen,
            self._screen_to_move_x if self._screen_to_move_x is not None else 0,
            self._screen_to_move_y if self._screen_to_move_y is not None else 0,
        )
        # 获取位于鼠标位置的tile块
        self._block_is_hovering = self._MAP.calculate_coordinate()
        # 展示角色动画
        self._display_entities(screen)
        # 检测角色所占据的装饰物（即需要透明化，方便玩家看到角色）
        charactersPos: list = []
        for value in self._entities_data.values():
            for dataDict in value.values():
                charactersPos.append((round(dataDict.x), round(dataDict.y)))
                charactersPos.append((round(dataDict.x) + 1, round(dataDict.y) + 1))
        # 展示场景装饰物
        self._MAP.display_decoration(screen, tuple(charactersPos))
