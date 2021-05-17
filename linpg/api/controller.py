# cython: language_level=3
from .basic import *

#手柄控制组件
class SingleJoystick:
    def __init__(self):
        #如果pygame的手柄组件没有初始化，则初始化
        if not pygame.joystick.get_init(): pygame.joystick.init()
        self.inputController = None
        self.update_device()
    #更新设备
    def update_device(self) -> None:
        if self.inputController is None and pygame.joystick.get_count() > 0:
            self.inputController = pygame.joystick.Joystick(0)
            self.inputController.init()
            throw_exception("info","Joystick is detected and initialized successfully.")
        elif self.inputController is not None:
            if pygame.joystick.get_count() == 0:
                self.inputController = None
            elif self.inputController.get_id() != pygame.joystick.Joystick(0).get_id():
                self.inputController = pygame.joystick.Joystick(0)
                self.inputController.init()
                throw_exception("info","Joystick changed! New joystick is detected and initialized successfully.")
    #手柄是否初始化
    def get_init(self) -> bool:
        return self.inputController.get_init() if self.inputController is not None else False
    #获取该按钮的详情
    def get_button(self,buttonId) -> bool:
        return self.inputController.get_button(buttonId) if self.inputController is not None and self.inputController.get_init() else False
    def get_axis(self,buttonId) -> float:
        return self.inputController.get_axis(buttonId) if self.inputController is not None and self.inputController.get_init() else 0.0

#输入管理组件
class GameController:
    def __init__(self, mouse_icon_width:Union[int,float], speed:Union[int,float], custom:bool=False):
        self.joystick = SingleJoystick()
        if custom is True:
            pygame.mouse.set_visible(False)
            self.iconImg = load_img(os.path.join("Assets/image/UI","mouse_icon.png")),(int(mouse_icon_width),int(mouse_icon_width*1.3))
        else:
            self.iconImg = None
        #鼠标位置
        self.mouse_x:int = 0
        self.mouse_y:int = 0
        self.mouse_moving_speed:Union[int,float] = speed
        #输入事件
        self.__INPUT_EVENTS:list = pygame.event.get()
        """常见事件"""
        #是否有确认事件
        self.__confirm_event:int = 0
        #是否有返回事件
        self.__back_event:int = 0
    #更新输入事件
    def __update_input_events(self) -> None:
        self.joystick.update_device()
        self.__INPUT_EVENTS = pygame.event.get()
        #重设用于判断常见事件的参数
        self.__confirm_event = 0
        self.__back_event = 0
        for event in self.__INPUT_EVENTS:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 or \
                event.type == pygame.JOYBUTTONDOWN and self.joystick.get_button(0) is True:
                self.__confirm_event = 1
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.__back_event = 1
        #更新鼠标坐标
        self.mouse_x,self.mouse_y = pygame.mouse.get_pos()
    #获取输入事件
    @property
    def events(self): return self.__INPUT_EVENTS
    def get_events(self): return self.__INPUT_EVENTS
    #获取单个事件
    def get_event(self, event_type:str) -> bool:
        if event_type == "confirm":
            if self.__confirm_event == 1:
                return True
            elif self.__confirm_event == 0:
                return False
            else:
                throw_exception("error", "self.__confirm_event in GameController is set to invalid number!")
        elif event_type == "back":
            if self.__back_event == 1:
                return True
            elif self.__back_event == 0:
                return False
            else:
                throw_exception("error", "self.__back_event in GameController is set to invalid number!")
        else:
            throw_exception("error", 'The event type "{}" is not supported!'.format(event_type))
        return False
    #返回鼠标的坐标
    def get_mouse_pos(self) -> tuple: return self.mouse_x,self.mouse_y
    #是否鼠标按钮被点击
    def mouse_get_press(self, button_id:int) -> bool: return pygame.mouse.get_pressed()[button_id]
    #画出，实际上相当于更新
    def draw(self, screen:ImageSurface=None):
        #更新输入事件
        self.__update_input_events()
        if self.joystick.inputController is not None:
            if self.joystick.get_axis(0)>0.1 or self.joystick.get_axis(0)<-0.1:
                self.mouse_x += int(self.mouse_moving_speed*round(self.joystick.get_axis(0),1))
            if self.joystick.get_axis(1)>0.1 or self.joystick.get_axis(1)<-0.1:
                self.mouse_y += int(self.mouse_moving_speed*round(self.joystick.get_axis(1),1))
            pygame.mouse.set_pos((self.mouse_x,self.mouse_y))
        if self.iconImg is not None and screen is not None:
            screen.blit(self.iconImg,(self.mouse_x,self.mouse_y))

#控制器输入组件初始化
controller:GameController = GameController(get_setting("MouseIconWidth"),get_setting("MouseMoveSpeed"))

#画面更新控制器
class DisplayController:
    def __init__(self, fps:int):
        self.__fps:int = max(int(fps),1)
        self.__clock:object = pygame.time.Clock()
        self.__standard_fps:int = 60
        #默认尺寸
        self.__screen_scale:int = keep_in_range(int(get_setting("ScreenScale")),0,100)
        self.__standard_width:int = round(1920*self.__screen_scale/100)
        self.__standard_height:int = round(1080*self.__screen_scale/100)
    #帧数
    @property
    def fps(self) -> int: return self.__fps
    def get_fps(self) -> int: return self.__fps
    #标准帧数校准器
    @property
    def sfpsp(self) -> float: return self.__standard_fps/self.__fps
    #更新
    def flip(self) -> None:
        self.__clock.tick(self.fps)
        pygame.display.flip()
        controller.draw()
    #设置窗口标题
    def set_caption(self, title:any): pygame.display.set_caption(title)
    #设置窗口图标
    def set_icon(self, path:str): pygame.display.set_icon(pygame.image.load(os.path.join(path)))
    #窗口尺寸
    def get_width(self) -> int: return self.__standard_width
    def get_height(self) -> int: return self.__standard_height
    def get_size(self) -> tuple: return self.__standard_width,self.__standard_height
    #初始化屏幕
    def init_screen(self) -> any:
        flags = pygame.DOUBLEBUF | pygame.SCALED | pygame.FULLSCREEN if self.__screen_scale == 100 else pygame.SCALED
        return pygame.display.set_mode(self.get_size(), flags)
    def quit(self) -> None:
        from sys import exit
        #退出游戏
        exit()

#帧率控制器
display:DisplayController = DisplayController(get_setting("FPS"))
