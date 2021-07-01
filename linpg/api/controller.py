# cython: language_level=3
from .img import *

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
            EXCEPTION.inform("Joystick is detected and initialized successfully.")
        elif self.inputController is not None:
            if pygame.joystick.get_count() == 0:
                self.inputController = None
            elif self.inputController.get_id() != pygame.joystick.Joystick(0).get_id():
                self.inputController = pygame.joystick.Joystick(0)
                self.inputController.init()
                EXCEPTION.inform("Joystick changed! New joystick is detected and initialized successfully.")
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
        self.__INPUT_EVENTS:list = []
        #检测特定事件
        self.__specific_events = {
            #是否有确认事件
            "confirm": False,
            #是否有返回事件
            "back": False,
            #鼠标滚轮
            "scroll_up": False,
            "scroll_down": False,
            "previous": False
        }
    #更新输入事件
    def __update_input_events(self) -> None:
        self.joystick.update_device()
        self.__INPUT_EVENTS = pygame.event.get()
        #重设用于判断常见事件的参数
        for key in self.__specific_events:
            self.__specific_events[key] = False
        for event in self.__INPUT_EVENTS:
            if event.type == MOUSE_BUTTON_DOWN:
                if event.button == 1:
                    self.__specific_events["confirm"] = True
                elif event.button == 3:
                    self.__specific_events["previous"] = True
                elif event.button == 4:
                    self.__specific_events["scroll_up"] = True
                elif event.button == 5:
                    self.__specific_events["scroll_down"] = True
            elif event.type == JOYSTICK_BUTTON_DOWN:
                if self.joystick.get_button(0) is True:
                    self.__specific_events["confirm"] = True
                elif self.joystick.get_button(1) is True:
                    self.__specific_events["previous"] = True
            elif event.type == Key.DOWN and event.key == Key.ESCAPE:
                self.__specific_events["back"] = True
        #更新鼠标坐标
        self.mouse_x,self.mouse_y = pygame.mouse.get_pos()
    #获取输入事件
    @property
    def events(self): return self.__INPUT_EVENTS
    def get_events(self): return self.__INPUT_EVENTS
    #获取单个事件
    def get_event(self, event_type:str) -> bool:
        try:
            return self.__specific_events[event_type]
        except KeyError:
            EXCEPTION.throw("error", 'The event type "{}" is not supported!'.format(event_type))
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
controller:GameController = GameController(Setting.get("MouseIconWidth"),Setting.get("MouseMoveSpeed"))
