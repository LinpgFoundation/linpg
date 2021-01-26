# cython: language_level=3
from .font import *

#手柄控制组件
class SingleJoystick:
    def __init__(self):
        if pygame.joystick.get_init() == False:
            pygame.joystick.init()
        self.inputController = None
        self.update_device()
    def update_device(self):
        if self.inputController == None and pygame.joystick.get_count() > 0:
            self.inputController = pygame.joystick.Joystick(0)
            self.inputController.init()
            print("LinpgEngine: Joystick is detected and initialized successfully.")
        elif self.inputController != None:
            if pygame.joystick.get_count() == 0:
                self.inputController = None
            elif self.inputController.get_id() != pygame.joystick.Joystick(0).get_id():
                self.inputController = pygame.joystick.Joystick(0)
                self.inputController.init()
                print("LinpgEngine: Joystick changed! New joystick is detected and initialized successfully.")
    def get_init(self):
        if self.inputController != None:
            return self.inputController.get_init()
        else:
            return False
    def get_button(self,buttonId):
        if self.inputController != None and self.inputController.get_init() == True:
            return self.inputController.get_button(buttonId)
        else:
            return None
    def get_axis(self,buttonId):
        if self.inputController != None and self.inputController.get_init() == True:
            return self.inputController.get_axis(buttonId)
        else:
            return 0

#输入管理组件
class GameController:
    def __init__(self,mouse_icon_width,speed,custom=False):
        self.joystick = SingleJoystick()
        if custom == True:
            pygame.mouse.set_visible(False)
            self.iconImg = pygame.transform.scale(pygame.image.load(os.path.join("Assets/image/UI/","mouse_icon.png")).convert_alpha(),(int(mouse_icon_width),int(mouse_icon_width*1.3)))
        else:
            self.iconImg = None
        self.mouse_x,self.mouse_y = pygame.mouse.get_pos()
        self.movingSpeed = speed
    def display(self,screen=None):
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
    def get_event(self,pygame_events=None):
        if pygame_events == None:
            pygame_events = pygame.event.get()
        for event in pygame_events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 or event.type == pygame.JOYBUTTONDOWN and self.joystick.get_button(0) == 1:
                return "comfirm"
        return None
    def get_pos(self):
        return self.mouse_x,self.mouse_y

#控制器输入组件初始化
controller = GameController(get_setting("MouseIconWidth"),get_setting("MouseMoveSpeed"))

#画面更新控制器
class DisplayController:
    def __init__(self,fps):
        self.fps = fps
        self.__clock = pygame.time.Clock()
    def flip(self,pump=False):
        self.__clock.tick(self.fps)
        controller.display()
        if pump == True:
            pygame.event.pump()
        pygame.display.flip()
    def update(self,rectangle=None,pump=False):
        self.__clock.tick(self.fps)
        controller.display()
        if pump == True:
            pygame.event.pump()
        if rectangle == None:
            pygame.display.flip()
        else:
            pygame.display.update(rectangle)
    def set_caption(self,title):
        pygame.display.set_caption(title)
    def set_icon(self,path):
        pygame.display.set_icon(pygame.image.load(os.path.join(path)))
    def get_width(self):
        return get_setting("Screen_size_x")
    def get_height(self):
        return get_setting("Screen_size_y")
    def get_size(self):
        return self.get_width(),self.get_height()
    #初始化屏幕
    def init_screen(self,flags:any) -> any:
        return pygame.display.set_mode(self.get_size(),flags)
    def quit(self):
        from sys import exit
        #退出游戏
        exit()

#帧率控制器
display = DisplayController(get_setting("FPS"))
