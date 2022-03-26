from .controller import *
from datetime import datetime

# 画面更新控制器
class Display:

    # 帧率控制器
    __CLOCK: pygame.time.Clock = pygame.time.Clock()
    # 帧率
    __FPS: int = max(int(Setting.get("FPS")), 1)
    __STANDARD_FPS: int = 60
    # 窗口比例
    __SCALE: int = keep_int_in_range(int(Setting.get("Resolution", "scale")), 0, 100)
    # 主要的窗口
    __SCREEN_WINDOW: ImageSurface = Surface.NULL
    # 窗口尺寸
    __STANDARD_WIDTH: int = max(int(Setting.get("Resolution", "width")), 0) * __SCALE // 100
    __STANDARD_HEIGHT: int = max(int(Setting.get("Resolution", "height")), 0) * __SCALE // 100
    # 信息渲染使用的文字模块
    __FONT: pygame.font.Font = pygame.font.SysFont("arial", __STANDARD_HEIGHT // 40)

    # 帧数
    @classmethod
    def get_fps(cls) -> int:
        return cls.__FPS

    # 时间增量
    @classmethod
    def get_delta_time(cls) -> float:
        return max(cls.__CLOCK.get_fps() / cls.__STANDARD_FPS, 0.5)

    # 更新屏幕
    @classmethod
    def flip(cls) -> None:
        Controller.finish_up()
        # 展示帧率信息
        if Debug.get_show_fps():
            _text: ImageSurface = cls.__FONT.render(str(round(cls.__CLOCK.get_fps())), Setting.antialias, Colors.WHITE)
            cls.__SCREEN_WINDOW.blit(
                _text, (cls.__STANDARD_WIDTH - cls.__FONT.get_height() - _text.get_width(), cls.__FONT.get_height())
            )
        # 使用clock进行tick
        cls.__CLOCK.tick(cls.__FPS)
        pygame.display.flip()
        # 如果需要截图
        if Controller.NEED_TO_TAKE_SCREENSHOT is True:
            Controller.NEED_TO_TAKE_SCREENSHOT = False
            if not os.path.exists("screenshots"):
                os.mkdir("screenshots")
            pygame.image.save(
                cls.__SCREEN_WINDOW, os.path.join("screenshots", "{}.png".format(datetime.now().strftime("%Y%m%d%H%M%S")))
            )
        # 更新控制器
        Controller.update()
        Controller.mouse.draw_custom_icon(cls.__SCREEN_WINDOW)

    # 设置窗口标题
    @staticmethod
    def set_caption(title: str) -> None:
        pygame.display.set_caption(title)

    # 设置窗口图标
    @staticmethod
    def set_icon(path: str) -> None:
        pygame.display.set_icon(RawImg.quickly_load(path, False))

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
    def init(cls, flags: int = -1) -> ImageSurface:
        # 如果是全屏模式
        if cls.__SCALE >= 100:
            if flags < 0:
                flags = pygame.FULLSCREEN | pygame.SCALED
            if Setting.get("EnableOpenGL") is True:
                flags |= pygame.OPENGL
            # 如果分辨率与设置中的参数不符，则更新设置中的分辨率参数
            _info = pygame.display.Info()
            if cls.__STANDARD_WIDTH != _info.current_w or cls.__STANDARD_HEIGHT != _info.current_h:
                cls.__STANDARD_WIDTH = _info.current_w
                cls.__STANDARD_HEIGHT = _info.current_h
                Setting.set("Resolution", "width", value=cls.__STANDARD_WIDTH)
                Setting.set("Resolution", "height", value=cls.__STANDARD_HEIGHT)
                Setting.save()
        # 生成screen
        cls.__SCREEN_WINDOW = pygame.display.set_mode(
            cls.get_size(), flags, vsync=1 if Setting.get("EnableVerticalSync") is True else 0
        )
        cls.__SCREEN_WINDOW.set_alpha(None)
        return cls.__SCREEN_WINDOW

    # 获取屏幕
    @classmethod
    def get_window(cls) -> ImageSurface:
        return cls.__SCREEN_WINDOW

    # 退出
    @staticmethod
    def quit() -> None:
        from sys import exit as CLOSE

        # 退出游戏
        CLOSE()


# 直接画到屏幕上
def draw_on_screen(surface_to_draw: ImageSurface, pos: Sequence) -> None:
    Display.get_window().blit(surface_to_draw, Coordinates.convert(pos))
