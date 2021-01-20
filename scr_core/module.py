# cython: language_level=3
import threading
from .controller import *

#游戏对象接口
class GameObject:
    def __init__(self, x:float, y:float) -> None:
        self.x = x
        self.y = y
    def __lt__(self,other) -> bool: return self.y+self.x < other.y+other.x
    #获取坐标
    def get_pos(self) -> tuple: return self.x,self.y
    #设置坐标
    def set_pos(self, x:float, y:float) -> None:
        self.x = round(x)
        self.y = round(y)
    #检测是否在给定的位置上
    def on_pos(self,pos) -> bool: return is_same_pos(self.get_pos(),pos)

#系统模块接口
class SystemObject:
    def __init__(self) -> None:
        #输入事件
        self.__events = None
    #更新输入事件
    def _update_event(self) -> None: self.__events = pygame.event.get()
    #获取输入事件
    @property
    def events(self): return self.__events

#环境系统
class WeatherSystem:
    def  __init__(self,weather,window_x,window_y,entityNum=50):
        self.name = 0
        self.img_list = [loadImg(imgPath) for imgPath in glob.glob("Assets/image/environment/"+weather+"/*.png")]
        self.ImgObject = []
        for i in range(entityNum):
            imgId = randomInt(0,len(self.img_list)-1)
            img_size = randomInt(5,10)
            img_speed = randomInt(1,4)
            img_x = randomInt(1,window_x*1.5)
            img_y = randomInt(1,window_y)
            self.ImgObject.append(Snow(imgId,img_size,img_speed,img_x,img_y))
    def display(self,screen,perBlockWidth):
        speed_unit = perBlockWidth/15
        for i in range(len(self.ImgObject)):
            if 0 <= self.ImgObject[i].x <= screen.get_width() and 0 <= self.ImgObject[i].y <= screen.get_height():
                imgTemp = resizeImg(self.img_list[self.ImgObject[i].imgId],(perBlockWidth/self.ImgObject[i].size,perBlockWidth/self.ImgObject[i].size))
                screen.blit(imgTemp,(self.ImgObject[i].x,self.ImgObject[i].y))
            self.ImgObject[i].move(speed_unit)
            if self.ImgObject[i].x <= 0 or self.ImgObject[i].y >= screen.get_height():
                self.ImgObject[i].y = randomInt(-50,0)
                self.ImgObject[i].x = randomInt(0,screen.get_width()*2)

#雪花片
class Snow(GameObject):
    def  __init__(self,imgId,size,speed,x,y) -> None:
        GameObject.__init__(self,x,y)
        self.imgId = imgId
        self.size = size
        self.speed = speed
    def move(self,speed_unit) -> None:
        self.x -= self.speed*speed_unit
        self.y += self.speed*speed_unit

#设置UI
class SettingContoller:
    def __init__(self):
        self.isDisplaying = False
    def init(self,size):
        self.baseImgWidth = round(size[0]/3)
        self.baseImgHeight = round(size[0]/3)
        self.baseImg = loadImg("Assets/image/UI/setting_baseImg.png",(self.baseImgWidth,self.baseImgHeight))
        self.baseImg.set_alpha(200)
        self.baseImgX = int((size[0]-self.baseImgWidth)/2)
        self.baseImgY = int((size[1]-self.baseImgHeight)/2)
        self.bar_height = round(size[0]/60)
        self.bar_width = round(size[0]/5)
        self.button = loadImg("Assets/image/UI/setting_bar_circle.png",(self.bar_height,self.bar_height*2))
        self.bar_empty = loadImg("Assets/image/UI/setting_bar_empty.png",(self.bar_width,self.bar_height))
        self.bar_full = loadImg("Assets/image/UI/setting_bar_full.png",(self.bar_width,self.bar_height))
        self.bar_x = int(self.baseImgX+(self.baseImgWidth-self.bar_empty.get_width())/2)
        self.bar_y0 = self.baseImgY + self.baseImgHeight*0.2
        self.bar_y1 = self.baseImgY + self.baseImgHeight*0.4
        self.bar_y2 = self.baseImgY + self.baseImgHeight*0.6
        self.bar_y3 = self.baseImgY + self.baseImgHeight*0.8
        #音量数值
        self.soundVolume_background_music = get_setting("Sound","background_music")
        self.soundVolume_sound_effects = get_setting("Sound","sound_effects")
        self.soundVolume_sound_environment = get_setting("Sound","sound_environment")
        #设置UI中的文字
        self.FONTSIZE = round(size[0]/50)
        self.fontSizeBig = round(size[0]/50*1.5)
        self.normalFont = createFont(self.FONTSIZE)
        self.bigFont = createFont(self.fontSizeBig)
        langTxt = get_lang("SettingUI")
        self.settingTitleTxt = self.bigFont.render(langTxt["setting"],True,(255, 255, 255))
        self.settingTitleTxt_x = int(self.baseImgX+(self.baseImgWidth-self.settingTitleTxt.get_width())/2)
        self.settingTitleTxt_y = self.baseImgY+self.baseImgHeight*0.05
        #语言
        self.languageTxt = self.normalFont.render(langTxt["language"]+": "+langTxt["currentLang"],True,(255, 255, 255))
        #背景音乐
        self.backgroundMusicTxt = langTxt["background_music"]
        #音效
        self.soundEffectsTxt = langTxt["sound_effects"]
        #环境声效
        self.soundEnvironmentTxt = langTxt["sound_environment"]
        #确认
        self.confirmTxt_n = self.normalFont.render(langTxt["confirm"],True,(255, 255, 255))
        self.confirmTxt_b = self.bigFont.render(langTxt["confirm"],True,(255, 255, 255))
        #取消
        self.cancelTxt_n = self.normalFont.render(langTxt["cancel"],True,(255, 255, 255))
        self.cancelTxt_b = self.bigFont.render(langTxt["cancel"],True,(255, 255, 255))
        #确认和取消按钮的位置
        self.buttons_y = self.baseImgY + self.baseImgHeight*0.88
        self.buttons_x1 = self.baseImgX + self.baseImgWidth*0.2
        self.buttons_x2 = self.buttons_x1 + self.cancelTxt_n.get_width()*1.7
    def display(self,screen,pygame_events=pygame.event.get()):
        if self.isDisplaying:
            #底部图
            screen.blit(self.baseImg,(self.baseImgX,self.baseImgY))
            screen.blit(self.settingTitleTxt,(self.settingTitleTxt_x,self.settingTitleTxt_y))
            #语言
            screen.blit(self.languageTxt,(self.bar_x,self.bar_y0))
            #背景音乐
            screen.blit(self.normalFont.render(self.backgroundMusicTxt+": "+str(self.soundVolume_background_music),True,(255, 255, 255)),(self.bar_x,self.bar_y1-self.FONTSIZE*1.4))
            screen.blit(self.bar_empty,(self.bar_x,self.bar_y1))
            barImgWidth = round(self.bar_full.get_width()*self.soundVolume_background_music/100)
            screen.blit(resizeImg(self.bar_full,(barImgWidth,self.bar_height)),(self.bar_x,self.bar_y1))
            screen.blit(self.button,(self.bar_x+barImgWidth-self.button.get_width()/2,self.bar_y1-self.bar_height/2))
            #音效
            screen.blit(self.normalFont.render(self.soundEffectsTxt+": "+str(self.soundVolume_sound_effects),True,(255, 255, 255)),(self.bar_x,self.bar_y2-self.FONTSIZE*1.4))
            screen.blit(self.bar_empty,(self.bar_x,self.bar_y2))
            barImgWidth = round(self.bar_full.get_width()*self.soundVolume_sound_effects/100)
            screen.blit(resizeImg(self.bar_full,(barImgWidth,self.bar_height)),(self.bar_x,self.bar_y2))
            screen.blit(self.button,(self.bar_x+barImgWidth-self.button.get_width()/2,self.bar_y2-self.bar_height/2))
            #环境声
            screen.blit(self.normalFont.render(self.soundEnvironmentTxt+": "+str(self.soundVolume_sound_environment),True,(255, 255, 255)),(self.bar_x,self.bar_y3-self.FONTSIZE*1.4))
            screen.blit(self.bar_empty,(self.bar_x,self.bar_y3))
            barImgWidth = round(self.bar_full.get_width()*self.soundVolume_sound_environment/100)
            screen.blit(resizeImg(self.bar_full,(barImgWidth,self.bar_height)),(self.bar_x,self.bar_y3))
            screen.blit(self.button,(self.bar_x+barImgWidth-self.button.get_width()/2,self.bar_y3-self.bar_height/2))
            #获取鼠标坐标
            mouse_x,mouse_y=pygame.mouse.get_pos()
            #取消按钮
            if self.buttons_x1<mouse_x<self.buttons_x1+self.cancelTxt_n.get_width() and self.buttons_y<mouse_y<self.buttons_y+self.cancelTxt_n.get_height():
                screen.blit(self.cancelTxt_b,(self.buttons_x1,self.buttons_y))
                if controller.get_event(pygame_events) == "comfirm":
                    self.soundVolume_background_music = get_setting("Sound","background_music")
                    self.soundVolume_sound_effects = get_setting("Sound","sound_effects")
                    self.soundVolume_sound_environment = get_setting("Sound","sound_environment")
                    self.isDisplaying = False
            else:
                screen.blit(self.cancelTxt_n,(self.buttons_x1,self.buttons_y))
            #确认按钮
            if self.buttons_x2<mouse_x<self.buttons_x2+self.confirmTxt_n.get_width() and self.buttons_y<mouse_y<self.buttons_y+self.confirmTxt_n.get_height():
                screen.blit(self.confirmTxt_b,(self.buttons_x2,self.buttons_y))
                if controller.get_event(pygame_events) == "comfirm":
                    set_setting("Sound","background_music",self.soundVolume_background_music)
                    set_setting("Sound","sound_effects",self.soundVolume_sound_effects)
                    set_setting("Sound","sound_environment",self.soundVolume_sound_environment)
                    save_setting()
                    pygame.mixer.music.set_volume(self.soundVolume_background_music/100.0)
                    self.isDisplaying = False
                    return True
            else:
                screen.blit(self.confirmTxt_n,(self.buttons_x2,self.buttons_y))
            #其他按键的判定按钮
            if controller.get_event(pygame_events) == "comfirm":
                if self.bar_x<=mouse_x<=self.bar_x+self.bar_width:
                    #如果碰到背景音乐的音量条
                    if self.bar_y1-self.bar_height/2<mouse_y<self.bar_y1+self.bar_height*1.5:
                        self.soundVolume_background_music = round(100*(mouse_x-self.bar_x)/self.bar_width)
                    #如果碰到音效的音量条
                    elif self.bar_y2-self.bar_height/2<mouse_y<self.bar_y2+self.bar_height*1.5:
                        self.soundVolume_sound_effects = round(100*(mouse_x-self.bar_x)/self.bar_width)
                    #如果碰到环境声的音量条
                    elif self.bar_y3-self.bar_height/2<mouse_y<self.bar_y3+self.bar_height*1.5:
                        self.soundVolume_sound_environment = round(100*(mouse_x-self.bar_x)/self.bar_width)
        return False

setting = SettingContoller()

#行动点数管理器（塔防模式）
class ApSystem:
    def __init__(self,fontSize):
        self.point = 0
        self.coolDown = 0
        self.FONT = createFont(fontSize)
    def display(self,screen,x,y):
        screen.blit(self.FONT.render(self.point,self.MODE,(255, 255, 255)),(x,y))
        if self.coolDown == 100:
            self.point += 1
            self.coolDown = 0
        else:
            self.coolDown += 1

#音效管理模块
class SoundManagement:
    def __init__(self,channel_id):
        self.channel_id = channel_id
        self.sound_id = 0
        self.__sounds_list = []
    def add(self,path):
        self.__sounds_list.append(pygame.mixer.Sound(path))
    def play(self,sound_id=None):
        if len(self.__sounds_list)>0 and not pygame.mixer.Channel(self.channel_id).get_busy():
            if sound_id == None:
                self.sound_id = randomInt(0,len(self.__sounds_list)-1)
            else:
                self.sound_id = sound_id
            pygame.mixer.Channel(self.channel_id).play(self.__sounds_list[self.sound_id])
    def stop(self):
        pygame.mixer.Channel(self.channel_id).stop()
    def set_volume(self,volume):
        for i in range(len(self.__sounds_list)):
            self.__sounds_list[i].set_volume(volume)

#使用多线程保存数据
class SaveDataThread(threading.Thread):
    def __init__(self,config_file_path,data):
        threading.Thread.__init__(self)
        self.config_file_path = config_file_path
        self.data = data
    def run(self):
        saveConfig(self.config_file_path,self.data)
        del self.data,self.config_file_path
