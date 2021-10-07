from .img import *

# 手柄控制组件
class JoystickController:

    __input: object = None

    def __init__(self):
        # 如果pygame的手柄组件没有初始化，则初始化
        if not pygame.joystick.get_init():
            pygame.joystick.init()
        # 初始化
        self.update()

    # 手柄是否初始化
    def get_init(self) -> bool:
        return self.__input.get_init() if self.is_active() is True else False

    # 获取该按钮的详情
    def get_button(self, buttonId: int) -> bool:
        return self.__input.get_button(buttonId) if self.get_init() is True else False

    def get_axis(self, buttonId: int) -> float:
        return round(self.__input.get_axis(buttonId), 1) if self.get_init() is True else 0.0

    # 是否启动
    def is_active(self) -> bool:
        return self.__input is not None

    # 更新设备
    def update(self) -> None:
        # 有新的手柄连接了
        if self.__input is None:
            if pygame.joystick.get_count() > 0:
                self.__input = pygame.joystick.Joystick(0)
                self.__input.init()
                EXCEPTION.inform("A joystick is detected and initialized successfully.")
        # 当目前有手柄在连接
        else:
            # 失去与当前手柄的连接
            if pygame.joystick.get_count() == 0:
                self.__input = None
                EXCEPTION.inform("Lost connection with the joystick.")
            # 有新的手柄
            elif self.__input.get_id() != pygame.joystick.Joystick(0).get_id():
                self.__input = pygame.joystick.Joystick(0)
                self.__input.init()
                EXCEPTION.inform("Joystick changed! New joystick is detected and initialized successfully.")


# 鼠标控制
class MouseController:

    # 鼠标位置
    __x: int = 0
    __y: int = 0
    # 鼠标移动速度（使用手柄时）
    __moving_speed: int = int(max(Setting.get("MouseMoveSpeed"), 1))

    # 鼠标上次更新时被按下的详情
    __mouse_get_pressed_previously: tuple[bool] = (False, False, False, False, False)

    def __init__(self) -> None:
        custom: bool = False
        if not custom:
            self.__icon_img = None
        else:
            pygame.mouse.set_visible(False)
            self.__icon_img = IMG.load(
                "<!ui>mouse_icon.png", (int(Setting.get("MouseIconWidth")), int(Setting.get("MouseIconWidth") * 1.3))
            )
        self.update()

    # 灵敏度
    @property
    def moving_speed(self) -> int:
        return self.__moving_speed

    # 鼠标坐标
    @property
    def x(self) -> int:
        return self.__x

    @property
    def y(self) -> int:
        return self.__y

    @property
    def pos(self) -> tuple[int]:
        return self.__x, self.__y

    def get_pos(self) -> tuple[int]:
        return self.__x, self.__y

    # 设置坐标
    def set_pos(self, pos: Iterable) -> None:
        self.__x, self.__y = Pos.int(Pos.convert(pos))
        pygame.mouse.set_pos(self.get_pos())

    # 是否鼠标按钮被点击
    @staticmethod
    def get_pressed(button_id: int) -> bool:
        return pygame.mouse.get_pressed()[button_id]

    # 是否鼠标按钮在本次更新被点击
    def get_pressed_previously(self, button_id: int) -> bool:
        return self.__mouse_get_pressed_previously[button_id]

    # 更新设备
    def update(self) -> None:
        # 更新鼠标坐标
        self.__x, self.__y = pygame.mouse.get_pos()

    # 完成旧数据的存储
    def finish_up(self) -> None:
        self.__mouse_get_pressed_previously = pygame.mouse.get_pressed()

    # 画出自定义的鼠标图标
    def draw_custom_icon(self, surface: ImageSurface) -> None:
        if self.__icon_img is not None:
            surface.blit(self.__icon_img, self.pos)


# 输入管理组件
class GameController:

    # 模块
    __joystick: JoystickController = JoystickController()
    __mouse: MouseController = MouseController()
    # 输入事件
    __INPUT_EVENTS: list = []
    # 检测特定事件
    __SPECIFIC_EVENTS: dict = {
        # 是否有确认事件
        "confirm": False,
        # 是否有返回事件
        "back": False,
        # 鼠标滚轮
        "scroll_up": False,
        "scroll_down": False,
        "previous": False,
    }
    # 是否需要截图
    NEED_TO_TAKE_SCREENSHOT: bool = False

    # 手柄模块
    @property
    def joystick(self) -> JoystickController:
        return self.__joystick

    # 鼠标模块
    @property
    def mouse(self) -> MouseController:
        return self.__mouse

    # 输入事件
    @property
    def events(self):
        return self.__INPUT_EVENTS

    # 获取所有输入事件
    def get_events(self):
        return self.__INPUT_EVENTS

    # 获取单个事件
    def get_event(self, event_type: str) -> bool:
        try:
            return self.__SPECIFIC_EVENTS[event_type]
        except KeyError:
            EXCEPTION.fatal('The event type "{}" is not supported!'.format(event_type))

    # 完成这一帧的收尾工作
    def finish_up(self) -> None:
        self.__mouse.finish_up()

    # 更新输入
    def update(self) -> None:
        # 更新手柄输入事件
        self.__joystick.update()
        # 更新鼠标输入事件
        self.__mouse.update()
        # 根据手柄情况调整鼠标位置（如果手柄启动）
        if self.__joystick.is_active():
            x_axis_value: float = self.__joystick.get_axis(0)
            is_x_need_update: bool = not 0.5 > x_axis_value > -0.5
            y_axis_value: float = self.__joystick.get_axis(1)
            is_y_need_update: bool = not 0.5 > y_axis_value > -0.5
            if is_x_need_update is True and is_y_need_update is True:
                self.mouse.set_pos(
                    (
                        int(self.mouse.x + self.mouse.moving_speed * x_axis_value),
                        int(self.mouse.y + self.mouse.moving_speed * y_axis_value),
                    )
                )
            elif is_x_need_update is True:
                self.mouse.set_pos((int(self.mouse.x + self.mouse.moving_speed * x_axis_value), self.mouse.y))
            elif is_y_need_update is True:
                self.mouse.set_pos((self.mouse.x, int(self.mouse.y + self.mouse.moving_speed * y_axis_value)))
        # 更新综合输入事件
        self.__INPUT_EVENTS = pygame.event.get()
        # 重设用于判断常见事件的参数
        for key in self.__SPECIFIC_EVENTS:
            self.__SPECIFIC_EVENTS[key] = False
        for event in self.__INPUT_EVENTS:
            if event.type == MOUSE_BUTTON_DOWN:
                if event.button == 1:
                    self.__SPECIFIC_EVENTS["confirm"] = True
                elif event.button == 3:
                    self.__SPECIFIC_EVENTS["previous"] = True
                elif event.button == 4:
                    self.__SPECIFIC_EVENTS["scroll_up"] = True
                elif event.button == 5:
                    self.__SPECIFIC_EVENTS["scroll_down"] = True
            elif event.type == JOYSTICK_BUTTON_DOWN:
                if self.__joystick.get_button(0) is True:
                    self.__SPECIFIC_EVENTS["confirm"] = True
                elif self.__joystick.get_button(1) is True:
                    self.__SPECIFIC_EVENTS["previous"] = True
            elif event.type == Key.DOWN:
                if event.key == Key.ESCAPE:
                    self.__SPECIFIC_EVENTS["back"] = True
                elif event.key == Key.F3:
                    self.NEED_TO_TAKE_SCREENSHOT = True


# 控制器输入组件初始化
Controller: GameController = GameController()
