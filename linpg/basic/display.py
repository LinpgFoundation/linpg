from datetime import datetime

from .controller import *


# 画面更新控制器
class Display:
    # 帧率控制器
    __CLOCK: Final[pygame.time.Clock] = pygame.time.Clock()
    # 帧率
    __MAX_FPS: int = min(max(int(Setting.get("MaxFps")), 30), 1000)
    # 窗口比例
    __SCALE: int = Numbers.keep_int_in_range(int(Setting.get("Resolution", "scale")), 0, 100)
    # 主要的窗口
    __SCREEN_WINDOW: ImageSurface = Surfaces.NULL
    # 窗口尺寸
    __STANDARD_WIDTH: int = max(int(Setting.get("Resolution", "width")), 1) * __SCALE // 100
    __STANDARD_HEIGHT: int = max(int(Setting.get("Resolution", "height")), 1) * __SCALE // 100
    # 信息渲染使用的文字模块
    __FONT: Final[pygame.font.Font] = pygame.font.SysFont("arial", __STANDARD_HEIGHT // 40)
    # 时间增量
    __TICKS: int = 0
    __DELTA_TIME: int = 1

    # 帧数
    @classmethod
    def get_current_fps(cls) -> float:
        return cls.__CLOCK.get_fps()

    @classmethod
    def get_max_fps(cls) -> int:
        return cls.__MAX_FPS

    # 时间增量(ms)
    @classmethod
    def get_delta_time(cls) -> int:
        return cls.__DELTA_TIME

    # 更新屏幕
    @classmethod
    def flip(cls) -> None:
        Controller.finish_up()
        # 展示帧率信息
        if Debug.get_show_fps():
            _text: ImageSurface = cls.__FONT.render(
                f"fps: {round(cls.get_current_fps(), 2)} delta time (ms): {cls.__DELTA_TIME}", Setting.get_antialias(), Colors.WHITE
            )
            cls.__SCREEN_WINDOW.blit(_text, (cls.__STANDARD_WIDTH - cls.__FONT.get_height() - _text.get_width(), cls.__FONT.get_height()))
        # 使用clock进行tick
        cls.__CLOCK.tick(cls.__MAX_FPS)
        pygame.display.flip()
        # 如果需要截图
        if Controller.NEED_TO_TAKE_SCREENSHOT is True:
            Controller.NEED_TO_TAKE_SCREENSHOT = False
            if not os.path.exists(Specification.get_directory("screenshots")):
                os.mkdir(Specification.get_directory("screenshots"))
            pygame.image.save(cls.__SCREEN_WINDOW, Specification.get_directory("screenshots", f"{datetime.now().strftime('%Y%m%d%H%M%S')}.png"))
        # 更新控制器
        Controller.update()
        Controller.mouse.draw_custom_icon(cls.__SCREEN_WINDOW)
        # 计算新的时间增量
        new_ticks: int = pygame.time.get_ticks()
        cls.__DELTA_TIME = max(new_ticks - cls.__TICKS, 1)
        cls.__TICKS = new_ticks

    # 设置窗口标题
    @staticmethod
    def set_caption(title: str) -> None:
        pygame.display.set_caption(title)

    # 设置窗口图标
    @staticmethod
    def set_icon(path: str) -> None:
        pygame.display.set_icon(Images.quickly_load(path, False))

    # 窗口宽度
    @classmethod
    def get_width(cls) -> int:
        return cls.__STANDARD_WIDTH

    # 窗口高度
    @classmethod
    def get_height(cls) -> int:
        return cls.__STANDARD_HEIGHT

    # 窗口尺寸
    @classmethod
    def get_size(cls) -> tuple[int, int]:
        return cls.__STANDARD_WIDTH, cls.__STANDARD_HEIGHT

    # 初始化屏幕
    @classmethod
    def init(cls, flags: int = 0) -> ImageSurface:
        monitorId: int = int(Setting.get("MonitorToDisplay"))
        # 如果是全屏模式
        if cls.__SCALE >= 100:
            if flags <= 0:
                flags = pygame.FULLSCREEN | pygame.SCALED
            if Setting.get("EnableOpenGL") is True:
                flags |= pygame.OPENGL
            # 如果分辨率与设置中的参数不符，则更新设置中的分辨率参数
            theSelectedScreenSize: tuple[int, int] = pygame.display.get_desktop_sizes()[monitorId]
            if cls.__STANDARD_WIDTH != theSelectedScreenSize[0] or cls.__STANDARD_HEIGHT != theSelectedScreenSize[1]:
                cls.__STANDARD_WIDTH = theSelectedScreenSize[0]
                cls.__STANDARD_HEIGHT = theSelectedScreenSize[1]
                Setting.set("Resolution", "width", value=cls.__STANDARD_WIDTH)
                Setting.set("Resolution", "height", value=cls.__STANDARD_HEIGHT)
                Setting.save()
        # 生成screen
        cls.__SCREEN_WINDOW = pygame.display.set_mode(cls.get_size(), flags, display=monitorId, vsync=1 if Setting.get("EnableVerticalSync") is True else 0)
        cls.__SCREEN_WINDOW.set_alpha(None)
        cls.__SCREEN_WINDOW.fill(Colors.BLACK)
        return cls.__SCREEN_WINDOW

    # 获取屏幕
    @classmethod
    def get_window(cls) -> ImageSurface:
        return cls.__SCREEN_WINDOW

    # 直接画到屏幕上
    @classmethod
    def blit(cls, surface_to_draw: ImageSurface, pos: Sequence) -> None:
        cls.__SCREEN_WINDOW.blit(surface_to_draw, Coordinates.convert(pos))
