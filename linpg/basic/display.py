from .controller import *
from datetime import datetime

# 画面更新控制器
class DisplayController:

    __fps: int = max(int(Setting.get("FPS")), 1)
    __clock: pygame.time.Clock = pygame.time.Clock()
    __standard_fps: int = 60
    # 窗口比例
    __screen_scale: int = keep_int_in_range(int(Setting.get("ScreenScale")), 0, 100)
    # 主要的窗口
    __SCREEN_WINDOW: ImageSurface = Surface.NULL
    # 窗口尺寸
    __standard_width: int = round(1920 * __screen_scale / 100)
    __standard_height: int = round(1080 * __screen_scale / 100)

    # 帧数
    @property
    def fps(self) -> int:
        return self.__fps

    def get_fps(self) -> int:
        return self.__fps

    # 标准帧数校准器
    @property
    def sfpsp(self) -> float:
        return self.__standard_fps / self.__fps

    # 时间增量
    @property
    def delta_time(self) -> float:
        return pygame.time.get_ticks() / self.__fps

    # 获取 pixel per second
    def get_pps(self, distcane: float) -> int:
        return int(pygame.time.get_ticks() * distcane / self.__fps)

    # 更新屏幕
    def flip(self) -> None:
        Controller.finish_up()
        self.__clock.tick(self.fps)
        pygame.display.flip()
        # 如果需要截图
        if Controller.NEED_TO_TAKE_SCREENSHOT is True:
            Controller.NEED_TO_TAKE_SCREENSHOT = False
            if not os.path.exists("screenshots"):
                os.mkdir("screenshots")
            pygame.image.save(
                self.__SCREEN_WINDOW, os.path.join("screenshots", "{}.png".format(datetime.now().strftime("%Y%m%d%H%M%S")))
            )
        # 更新控制器
        Controller.update()
        Controller.mouse.draw_custom_icon(self.__SCREEN_WINDOW)

    # 设置窗口标题
    @staticmethod
    def set_caption(title: str) -> None:
        pygame.display.set_caption(title)

    # 设置窗口图标
    @staticmethod
    def set_icon(path: str) -> None:
        pygame.display.set_icon(RawImg.quickly_load(path, False))

    # 窗口尺寸
    @property
    def width(self) -> int:
        return self.__standard_width

    def get_width(self) -> int:
        return self.__standard_width

    @property
    def height(self) -> int:
        return self.__standard_height

    def get_height(self) -> int:
        return self.__standard_height

    @property
    def size(self) -> tuple[int, int]:
        return self.__standard_width, self.__standard_height

    def get_size(self) -> tuple[int, int]:
        return self.__standard_width, self.__standard_height

    # 分辨率 - str
    @property
    def resolution(self) -> str:
        return "{0}x{1}".format(self.__standard_width, self.__standard_height)

    # 初始化屏幕
    def init(self, flags: int = -1) -> ImageSurface:
        if flags < 0:
            flags = pygame.FULLSCREEN if self.__screen_scale >= 100 else 0
            if Setting.get("EnableOpenGL") is True:
                flags |= pygame.OPENGL
        self.__SCREEN_WINDOW = pygame.display.set_mode(
            self.get_size(), flags, vsync=1 if Setting.get("EnableVerticalSync") is True else 0
        )
        self.__SCREEN_WINDOW.set_alpha(None)
        return self.__SCREEN_WINDOW

    # 获取屏幕
    @property
    def window(self) -> ImageSurface:
        return self.__SCREEN_WINDOW

    # 退出
    @staticmethod
    def quit() -> None:
        from sys import exit as CLOSE

        # 退出游戏
        CLOSE()


# 帧率控制器
Display: DisplayController = DisplayController()

# 直接画到屏幕上
def draw_on_screen(surface_to_draw: ImageSurface, pos: Sequence) -> None:
    Display.window.blit(surface_to_draw, Coordinates.convert(pos))
