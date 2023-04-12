from .map import *


# 战斗系统接口，请勿实例化
class AbstractBattleSystem(AbstractGameSystem, metaclass=ABCMeta):
    def __init__(self) -> None:
        super().__init__()
        # 用于判断是否移动屏幕的参数
        self.__mouse_move_temp_x: int = -1
        self.__mouse_move_temp_y: int = -1
        self._screen_to_move_speed_x: Optional[int] = None
        self._screen_to_move_speed_y: Optional[int] = None
        # 用于检测是否有方向键被按到的字典
        self.__moving_screen_in_direction_up: bool = False
        self.__moving_screen_in_direction_down: bool = False
        self.__moving_screen_in_direction_left: bool = False
        self.__moving_screen_in_direction_right: bool = False
        # 角色数据
        self._entities_data: dict[str, dict[str, Entity]] = {}
        # 地图数据
        self.__map: Optional[AbstractTileMap] = None
        # 方格标准尺寸
        self._standard_tile_size: int = Display.get_width() // 10
        # 天气系统
        self._weather_system: WeatherSystem = WeatherSystem()
        # 当前鼠标位置上的tile块
        self._tile_is_hovering: Optional[tuple[int, int]] = None

    # 渲染出所有的entity - 子类需实现
    @abstractmethod
    def _display_entities(self, _surface: ImageSurface) -> None:
        EXCEPTION.fatal("_display_entities()", 1)

    # 加载角色的数据 - 子类需实现
    @abstractmethod
    def _load_entities(self, _entities: dict, _mode: str) -> None:
        EXCEPTION.fatal("_load_entities()", 1)

    # 初始化并加载新场景 - 子类需实现
    @abstractmethod
    def new(self, chapterType: str, chapterId: int, projectName: Optional[str] = None) -> None:
        EXCEPTION.fatal("new()", 1)

    # 获取地图
    def get_map(self) -> AbstractTileMap:
        if self.__map is not None:
            return self.__map
        else:
            EXCEPTION.fatal("Map has not been initialized!")

    # 获取地图
    def set_map(self, _map: AbstractTileMap) -> None:
        self.__map = _map

    # 加载地图数据
    def _load_map(self, _data: dict) -> None:
        self.get_map().update(_data, self._standard_tile_size)

    # 处理数据
    def _process_data(self, _data: dict) -> None:
        # 初始化角色信息
        self._load_entities(_data.get("entities", {}), _data.get("_mode", "default"))
        # 初始化地图
        self._load_map(_data)

    # 获取地图文件所在的具体路径
    def get_data_file_path(self) -> str:
        return (
            os.path.join("Data", self._chapter_type, f"chapter{self._chapter_id}_map.{Config.get_file_type()}")
            if self._project_name is None
            else os.path.join("Data", self._chapter_type, self._project_name, f"chapter{self._chapter_id}_map.{Config.get_file_type()}")
        )

    # 返回需要保存数据
    def _get_data_need_to_save(self) -> dict:
        _data: dict = {"entities": {}}
        for faction, entitiesDict in self._entities_data.items():
            _data["entities"][faction] = {}
            for key in entitiesDict:
                _data["entities"][faction][key] = entitiesDict[key].to_dict()
        _data.update(self.get_data_of_parent_game_system())
        _data.update(self.get_map().to_dict())
        return _data

    # 检测按下按键的事件
    def _check_key_down(self, event: PG_Event) -> None:
        match event.key:
            case Keys.ARROW_UP:
                self.__moving_screen_in_direction_up = True
            case Keys.ARROW_DOWN:
                self.__moving_screen_in_direction_down = True
            case Keys.ARROW_LEFT:
                self.__moving_screen_in_direction_left = True
            case Keys.ARROW_RIGHT:
                self.__moving_screen_in_direction_right = True

    # 检测按键回弹的事件
    def _check_key_up(self, event: PG_Event) -> None:
        match event.key:
            case Keys.ARROW_UP:
                self.__moving_screen_in_direction_up = False
            case Keys.ARROW_DOWN:
                self.__moving_screen_in_direction_down = False
            case Keys.ARROW_LEFT:
                self.__moving_screen_in_direction_left = False
            case Keys.ARROW_RIGHT:
                self.__moving_screen_in_direction_right = False

    # 检测手柄事件
    def _check_joystick_events(self) -> None:
        self.__moving_screen_in_direction_up = round(Controller.joystick.get_axis(4)) == -1
        self.__moving_screen_in_direction_down = round(Controller.joystick.get_axis(4)) == 1
        self.__moving_screen_in_direction_right = round(Controller.joystick.get_axis(3)) == 1
        self.__moving_screen_in_direction_left = round(Controller.joystick.get_axis(3)) == -1

    # 展示地图
    def _display_map(self, _surface: ImageSurface) -> None:
        # 处理鼠标事件
        for event in Controller.get_events():
            match event.type:
                case Events.KEY_DOWN:
                    self._check_key_down(event)
                case Events.KEY_UP:
                    self._check_key_up(event)
        # 处理手柄事件
        if Controller.joystick.get_init():
            self._check_joystick_events()
        # 检测是否使用了鼠标移动了地图的本地坐标
        if Controller.mouse.get_pressed(2):
            if self.__mouse_move_temp_x == -1 and self.__mouse_move_temp_y == -1:
                self.__mouse_move_temp_x = Controller.mouse.x
                self.__mouse_move_temp_y = Controller.mouse.y
            else:
                if self.__mouse_move_temp_x != Controller.mouse.x or self.__mouse_move_temp_y != Controller.mouse.y:
                    if self.__mouse_move_temp_x != Controller.mouse.x:
                        self.get_map().add_local_x(self.__mouse_move_temp_x - Controller.mouse.x)
                    if self.__mouse_move_temp_y != Controller.mouse.y:
                        self.get_map().add_local_y(self.__mouse_move_temp_y - Controller.mouse.y)
                    self.__mouse_move_temp_x = Controller.mouse.x
                    self.__mouse_move_temp_y = Controller.mouse.y
        else:
            self.__mouse_move_temp_x = -1
            self.__mouse_move_temp_y = -1
        # 根据按键情况设定要移动的数值
        if self.__moving_screen_in_direction_up is True:
            if self._screen_to_move_speed_y is None:
                self._screen_to_move_speed_y = self.get_map().tile_height // 4
            else:
                self._screen_to_move_speed_y += self.get_map().tile_height // 4
        if self.__moving_screen_in_direction_down is True:
            if self._screen_to_move_speed_y is None:
                self._screen_to_move_speed_y = -self.get_map().tile_height // 4
            else:
                self._screen_to_move_speed_y -= self.get_map().tile_height // 4
        if self.__moving_screen_in_direction_left is True:
            if self._screen_to_move_speed_x is None:
                self._screen_to_move_speed_x = self.get_map().tile_width // 4
            else:
                self._screen_to_move_speed_x += self.get_map().tile_width // 4
        if self.__moving_screen_in_direction_right is True:
            if self._screen_to_move_speed_x is None:
                self._screen_to_move_speed_x = -self.get_map().tile_width // 4
            else:
                self._screen_to_move_speed_x -= self.get_map().tile_width // 4
        # 如果需要移动屏幕
        # 注意，因为self._screen_to_move_speed可能是复数，所以//会可能导致问题
        temp_value: int
        if self._screen_to_move_speed_x is not None:
            temp_value = self.get_map().get_local_x() + int(self._screen_to_move_speed_x / 5)
            if Display.get_width() - self.get_map().get_width() <= temp_value <= 0:
                self.get_map().set_local_x(temp_value)
                self._screen_to_move_speed_x = int(self._screen_to_move_speed_x * 4 / 5)
                if self._screen_to_move_speed_x == 0:
                    self._screen_to_move_speed_x = None
            else:
                self._screen_to_move_speed_x = None
        if self._screen_to_move_speed_y is not None:
            temp_value = self.get_map().get_local_y() + int(self._screen_to_move_speed_y / 5)
            if Display.get_height() - self.get_map().get_height() <= temp_value <= 0:
                self.get_map().set_local_y(temp_value)
                self._screen_to_move_speed_y = int(self._screen_to_move_speed_y * 4 / 5)
                if self._screen_to_move_speed_y == 0:
                    self._screen_to_move_speed_y = None
            else:
                self._screen_to_move_speed_y = None
        # 展示地图
        self._screen_to_move_speed_x, self._screen_to_move_speed_y = self.get_map().render(
            _surface,
            self._screen_to_move_speed_x if self._screen_to_move_speed_x is not None else 0,
            self._screen_to_move_speed_y if self._screen_to_move_speed_y is not None else 0,
        )
        # 获取位于鼠标位置的tile块
        self._tile_is_hovering = self.get_map().calculate_coordinate()
        # 展示角色动画
        self._display_entities(_surface)
        # 检测角色所占据的装饰物（即需要透明化，方便玩家看到角色）
        charactersPos: list = []
        for value in self._entities_data.values():
            for dataDict in value.values():
                charactersPos.append((round(dataDict.x), round(dataDict.y)))
                charactersPos.append((round(dataDict.x) + 1, round(dataDict.y) + 1))
        # 展示场景装饰物
        self.get_map().display_decoration(_surface, tuple(charactersPos))
