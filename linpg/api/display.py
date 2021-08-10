from .controller import *

# 画面更新控制器
class DisplayController:
    def __init__(self):
        self.__fps: int = max(int(Setting.get("FPS")), 1)
        self.__clock: object = pygame.time.Clock()
        self.__standard_fps: int = 60
        # 窗口比例
        self.__screen_scale: int = int(keep_in_range(Setting.get("ScreenScale"), 0, 100))
        # 窗口尺寸
        self.__standard_width: int = round(1920 * self.__screen_scale / 100)
        self.__standard_height: int = round(1080 * self.__screen_scale / 100)
        # 主要的窗口
        self.__SCREEN_WINDOW: object = None

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

    # 更新屏幕
    def flip(self) -> None:
        self.__clock.tick(self.fps)
        pygame.display.flip()
        # 更新控制器
        Controller.update()
        Controller.mouse.draw_custom_icon(self.__SCREEN_WINDOW)

    # 设置窗口标题
    def set_caption(self, title: str) -> None:
        if is_using_pygame():
            pygame.display.set_caption(title)
        else:
            self.__SCREEN_WINDOW.set_caption(title)

    # 设置窗口图标
    def set_icon(self, path: str) -> None:
        if is_using_pygame():
            pygame.display.set_icon(IMG.quickly_load(path, False))
        else:
            self.__SCREEN_WINDOW.set_icon(IMG.quickly_load(path, False))

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
    def size(self) -> tuple:
        return self.__standard_width, self.__standard_height

    def get_size(self) -> tuple:
        return self.__standard_width, self.__standard_height

    # 分辨率 - str
    @property
    def resolution(self) -> str:
        return "{0}x{1}".format(self.__standard_width, self.__standard_height)

    # 初始化屏幕
    def init(self, flags=None) -> object:
        if is_using_pygame() is True:
            if flags is None:
                if self.__screen_scale >= 100:
                    flags = pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.SCALED
                else:
                    flags = pygame.SCALED
            self.__SCREEN_WINDOW = pygame.display.set_mode(
                self.get_size(),
                flags,
                vsync=1 if Setting.get("VerticalSync") is True else 0,
            )
            self.__SCREEN_WINDOW.set_alpha(None)
        else:
            self.__SCREEN_WINDOW = pyglet.window.Window(self.get_width(), self.get_height())
        return self.__SCREEN_WINDOW

    # 获取屏幕
    @property
    def window(self) -> object:
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
def draw_on_screen(surface_to_draw: ImageSurface, pos: Iterable) -> None:
    Display.window.blit(surface_to_draw, Pos.convert(pos))
