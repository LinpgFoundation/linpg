# cython: language_level=3
from .font import *

#手柄控制组件
class SingleJoystick:
    def __init__(self):
        #如果pygame的手柄组件没有初始化，则初始化
        if not pygame.joystick.get_init(): pygame.joystick.init()
        self.inputController = None
        self.update_device()
    #更新设备
    def update_device(self) -> None:
        if self.inputController == None and pygame.joystick.get_count() > 0:
            self.inputController = pygame.joystick.Joystick(0)
            self.inputController.init()
            throwException("info","Joystick is detected and initialized successfully.")
        elif self.inputController != None:
            if pygame.joystick.get_count() == 0:
                self.inputController = None
            elif self.inputController.get_id() != pygame.joystick.Joystick(0).get_id():
                self.inputController = pygame.joystick.Joystick(0)
                self.inputController.init()
                throwException("info","Joystick changed! New joystick is detected and initialized successfully.")
    #手柄是否初始化
    def get_init(self) -> bool:
        return self.inputController.get_init() if self.inputController != None else False
    #获取该按钮的详情
    def get_button(self,buttonId) -> bool:
        return self.inputController.get_button(buttonId) if self.inputController != None and self.inputController.get_init() else False
    def get_axis(self,buttonId) -> float:
        return self.inputController.get_axis(buttonId) if self.inputController != None and self.inputController.get_init() else 0.0

#输入管理组件
class GameController:
    def __init__(self, mouse_icon_width:Union[int,float], speed:Union[int,float], custom:bool=False):
        self.joystick = SingleJoystick()
        if custom:
            pygame.mouse.set_visible(False)
            self.iconImg = pygame.transform.scale(pygame.image.load(os.path.join("Assets/image/UI/","mouse_icon.png")).convert_alpha(),(int(mouse_icon_width),int(mouse_icon_width*1.3)))
        else:
            self.iconImg = None
        self.mouse_x,self.mouse_y = pygame.mouse.get_pos()
        self.movingSpeed = speed
    def display(self, screen=None):
        self.joystick.update_device()
        self.mouse_x,self.mouse_y = pygame.mouse.get_pos()
        if self.joystick.inputController != None:
            if self.joystick.get_axis(0)>0.1 or self.joystick.get_axis(0)<-0.1:
                self.mouse_x += int(self.movingSpeed*round(self.joystick.get_axis(0),1))
            if self.joystick.get_axis(1)>0.1 or self.joystick.get_axis(1)<-0.1:
                self.mouse_y += int(self.movingSpeed*round(self.joystick.get_axis(1),1))
            pygame.mouse.set_pos((self.mouse_x,self.mouse_y))
        if self.iconImg != None and screen != None:
            screen.blit(self.iconImg,(self.mouse_x,self.mouse_y))
    def get_event(self, pygame_events=pygame.event.get()):
        for event in pygame_events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 or\
                event.type == pygame.JOYBUTTONDOWN and self.joystick.get_button(0) == True: return "comfirm"
        return None
    #返回鼠标的坐标
    def get_pos(self): return self.mouse_x,self.mouse_y

#控制器输入组件初始化
controller:GameController = GameController(get_setting("MouseIconWidth"),get_setting("MouseMoveSpeed"))

#画面更新控制器
class DisplayController:
    def __init__(self, fps:int):
        self.fps = fps
        self.__clock = pygame.time.Clock()
    def flip(self, pump:bool=False) -> None:
        self.__clock.tick(self.fps)
        controller.display()
        if pump: pygame.event.pump()
        pygame.display.flip()
    def update(self, rectangle=None, pump:bool=False):
        self.__clock.tick(self.fps)
        controller.display()
        if pump == True: pygame.event.pump()
        if rectangle == None:
            pygame.display.flip()
        else:
            pygame.display.update(rectangle)
    #设置窗口标题
    def set_caption(self, title:any): pygame.display.set_caption(title)
    #设置窗口图标
    def set_icon(self, path:str): pygame.display.set_icon(pygame.image.load(os.path.join(path)))
    def get_width(self) -> int: return get_setting("Screen_size")*16
    def get_height(self) -> int: return get_setting("Screen_size")*9
    def get_size(self) -> tuple: return self.get_width(),self.get_height()
    #初始化屏幕
    def init_screen(self, flags:any) -> any:
        return pygame.display.set_mode(self.get_size(),flags)
    def quit(self) -> None:
        from sys import exit
        #退出游戏
        exit()

#帧率控制器
display:DisplayController = DisplayController(get_setting("FPS"))
