from .images import *

# 如果pygame的手柄组件没有初始化，则初始化
if not pygame.joystick.get_init():
    pygame.joystick.init()

# 输入管理组件
class Controller:

    # 手柄控制组件
    class __JoystickController:

        __input: Optional[pygame.joystick.JoystickType] = None

        # 手柄是否初始化
        @classmethod
        def get_init(cls) -> bool:
            return cls.__input.get_init() if cls.is_active() is True else False  # type: ignore

        # 获取该按钮的详情
        @classmethod
        def get_button(cls, buttonId: int) -> bool:
            return cls.__input.get_button(buttonId) if cls.get_init() is True else False  # type: ignore

        @classmethod
        def get_axis(cls, buttonId: int) -> float:
            return round(cls.__input.get_axis(buttonId), 1) if cls.get_init() is True else 0.0  # type: ignore

        # 是否启动
        @classmethod
        def is_active(cls) -> bool:
            return cls.__input is not None

        # 更新设备
        @classmethod
        def update(cls) -> None:
            # 有新的手柄连接了
            if cls.__input is None:
                if pygame.joystick.get_count() > 0:
                    cls.__input = pygame.joystick.Joystick(0)
                    cls.__input.init()
                    EXCEPTION.inform("A joystick is detected and initialized successfully.")
            # 当目前有手柄在连接
            else:
                # 失去与当前手柄的连接
                if pygame.joystick.get_count() == 0:
                    cls.__input = None
                    EXCEPTION.inform("Lost connection with the joystick.")
                # 有新的手柄
                elif cls.__input.get_id() != pygame.joystick.Joystick(0).get_id():
                    cls.__input = pygame.joystick.Joystick(0)
                    cls.__input.init()
                    EXCEPTION.inform("Joystick changed! New joystick is detected and initialized successfully.")

    # 鼠标控制
    class __MouseController:

        # 当前鼠标坐标
        x: int = 0
        y: int = 0
        # 之前的鼠标坐标
        __last_x: int = 0
        __last_y: int = 0
        # 鼠标移动速度（使用手柄时）
        __moving_speed: int = max(int(Setting.get("MouseMoveSpeed")), 1)
        # 鼠标上次更新时被按下的详情
        __mouse_get_pressed_previously: tuple[bool, ...] = (False, False, False, False, False)
        # 鼠标图标
        __icon_img: Optional[ImageSurface] = None

        @classmethod
        def set_custom_icon(cls, path: str = "<&ui>mouse_icon.png") -> None:
            cls.__icon_img = Images.load(path, (int(Setting.get("MouseIconWidth")), int(Setting.get("MouseIconWidth") * 1.3)))

        # 灵敏度
        @classmethod
        def get_moving_speed(cls) -> int:
            return cls.__moving_speed

        # 鼠标坐标
        @classmethod
        def get_x_moved(cls) -> int:
            return cls.__last_x - cls.x

        @classmethod
        def get_y_moved(cls) -> int:
            return cls.__last_y - cls.y

        @classmethod
        def get_pos(cls) -> tuple[int, int]:
            return cls.x, cls.y

        # 设置坐标
        @classmethod
        def set_pos(cls, pos: tuple) -> None:
            # 更新前鼠标坐标
            cls.__last_x = cls.x
            cls.__last_y = cls.y
            # 更新当前鼠标坐标
            cls.x, cls.y = Coordinates.convert(pos)
            pygame.mouse.set_pos(cls.get_pos())

        # 是否鼠标按钮被点击
        @staticmethod
        def get_pressed(button_id: int) -> bool:
            return pygame.mouse.get_pressed()[button_id]

        # 是否鼠标按钮在上一帧被点击
        @classmethod
        def get_pressed_previously(cls, button_id: int) -> bool:
            return cls.__mouse_get_pressed_previously[button_id]

        # 是否鼠标按钮在上一帧和当前帧被点击
        @classmethod
        def get_pressed_since(cls, button_id: int) -> bool:
            return cls.__mouse_get_pressed_previously[button_id] and pygame.mouse.get_pressed()[button_id]

        # 是否鼠标指针在指定的方形范围内
        @classmethod
        def is_in_rect(cls, _x: int, _y: int, _width: int, _height: int) -> bool:
            return 0 < cls.x - _x < _width and 0 < cls.y - _y < _height

        # 更新鼠标数据
        @classmethod
        def update(cls) -> None:
            # 更新前鼠标坐标
            cls.__last_x = cls.x
            cls.__last_y = cls.y
            # 更新当前鼠标坐标
            cls.x, cls.y = pygame.mouse.get_pos()

        # 完成旧数据的存储
        @classmethod
        def finish_up(cls) -> None:
            cls.__mouse_get_pressed_previously = pygame.mouse.get_pressed()

        # 画出自定义的鼠标图标
        @classmethod
        def draw_custom_icon(cls, _surface: ImageSurface) -> None:
            if cls.__icon_img is not None:
                _surface.blit(cls.__icon_img, (cls.x, cls.y))

    # 手柄模块
    joystick = __JoystickController
    # 鼠标模块
    mouse = __MouseController
    # 输入事件
    __INPUT_EVENTS: tuple = tuple()
    # 检测特定事件
    __SPECIFIC_EVENTS: Final[dict[str, bool]] = {
        # 是否有确认事件
        "confirm": False,
        # 是否有返回事件
        "back": False,
        # 鼠标滚轮
        "scroll_up": False,
        "scroll_down": False,
        "previous": False,
        # 删除
        "delete": False,
    }
    # 是否需要截图
    NEED_TO_TAKE_SCREENSHOT: bool = False

    # 获取所有输入事件
    @classmethod
    def get_events(cls) -> tuple:
        return cls.__INPUT_EVENTS

    # 获取单个事件
    @classmethod
    def get_event(cls, event_type: str) -> bool:
        _result: Optional[bool] = cls.__SPECIFIC_EVENTS.get(event_type)
        if _result is not None:
            return _result
        else:
            EXCEPTION.fatal('The event type "{}" is not supported!'.format(event_type))

    # 完成这一帧的收尾工作
    @classmethod
    def finish_up(cls) -> None:
        cls.mouse.finish_up()

    # 更新输入
    @classmethod
    def update(cls) -> None:
        # 更新手柄输入事件
        cls.joystick.update()
        # 更新鼠标输入事件
        cls.mouse.update()
        # 根据手柄情况调整鼠标位置（如果手柄启动）
        if cls.joystick.is_active():
            x_axis_value: float = cls.joystick.get_axis(0)
            is_x_need_update: bool = not 0.5 > x_axis_value > -0.5
            y_axis_value: float = cls.joystick.get_axis(1)
            is_y_need_update: bool = not 0.5 > y_axis_value > -0.5
            if is_x_need_update is True and is_y_need_update is True:
                cls.mouse.set_pos(
                    (
                        int(cls.mouse.x + cls.mouse.get_moving_speed() * x_axis_value),
                        int(cls.mouse.y + cls.mouse.get_moving_speed() * y_axis_value),
                    )
                )
            elif is_x_need_update is True:
                cls.mouse.set_pos((int(cls.mouse.x + cls.mouse.get_moving_speed() * x_axis_value), cls.mouse.y))
            elif is_y_need_update is True:
                cls.mouse.set_pos((cls.mouse.x, int(cls.mouse.y + cls.mouse.get_moving_speed() * y_axis_value)))
        # 更新综合输入事件
        cls.__INPUT_EVENTS = tuple(pygame.event.get())
        # 重设用于判断常见事件的参数
        for key in cls.__SPECIFIC_EVENTS:
            cls.__SPECIFIC_EVENTS[key] = False
        for event in cls.__INPUT_EVENTS:
            if event.type == MOUSE_BUTTON_DOWN:
                if event.button == 1:
                    cls.__SPECIFIC_EVENTS["confirm"] = True
                elif event.button == 3:
                    cls.__SPECIFIC_EVENTS["previous"] = True
                elif event.button == 4:
                    cls.__SPECIFIC_EVENTS["scroll_up"] = True
                elif event.button == 5:
                    cls.__SPECIFIC_EVENTS["scroll_down"] = True
            elif event.type == JOYSTICK_BUTTON_DOWN:
                if cls.joystick.get_button(0) is True:
                    cls.__SPECIFIC_EVENTS["confirm"] = True
                elif cls.joystick.get_button(1) is True:
                    cls.__SPECIFIC_EVENTS["previous"] = True
            elif event.type == Keys.DOWN:
                if event.key == Keys.ESCAPE:
                    cls.__SPECIFIC_EVENTS["back"] = True
                elif event.key == Keys.F3:
                    cls.NEED_TO_TAKE_SCREENSHOT = True
                elif event.key == Keys.DELETE:
                    cls.__SPECIFIC_EVENTS["delete"] = True


# 控制器输入组件初始化
Controller.update()
