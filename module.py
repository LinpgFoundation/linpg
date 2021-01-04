# cython: language_level=3
import glob
import random
from .controller import *
import time
from tkinter import Tk

#游戏对象接口
class GameObject:
    def __init__(self,x,y):
        self.x = x
        self.y = y
    def __lt__(self,other):
        return self.y+self.x < other.y+other.x
    def get_pos(self):
        return self.x,self.y

#图形接口
class ImageInterface(GameObject):
    def __init__(self,img,x,y,width,height):
        GameObject.__init__(self,x,y)
        self.img = img
        self.width = width
        self.height = height
    def set_alpha(self,value):
        self.img.set_alpha(value)
    def get_alpha(self):
        return self.img.get_alpha()
    def get_width(self):
        return self.width
    def get_height(self):
        return self.height

#高级图形类
class ImageSurface(ImageInterface):
    def __init__(self,img,x,y,width=None,height=None,description="Default"):
        ImageInterface.__init__(self,img,x,y,width,height)
        self.xTogo = x
        self.yTogo = y
        self.items = []
        self.description = description
        if self.width == None and self.height == None:
            self.width,self.height = self.img.get_size()
        elif self.width == None and self.height != None:
            self.width = self.height/self.img.get_height()*self.img.get_width()
        elif self.width != None and self.height == None:
            self.height = self.width/self.img.get_width()*self.img.get_height()
    def draw(self,screen):
        screen.blit(pygame.transform.scale(self.img,(round(self.width),round(self.height))),(self.x,self.y))
    def display(self,screen,local_x=0,local_y=0):
        screen.blit(pygame.transform.scale(self.img, (round(self.width),round(self.height))),(self.x+local_x,self.y+local_y))
    def rotate(self,angle):
        self.img = pygame.transform.rotate(self.img,angle)
    def flip(self,vertical=False,horizontal=False):
        self.img = pygame.transform.flip(self.img,vertical,horizontal)
    def ifHover(self,mouse_x,mouse_y):
        if 0<mouse_x-self.x<self.width and 0<mouse_y-self.y<self.height:
            return True
        else:
            return False

#需要移动的动态图片
class DynamicImageSurface(ImageSurface):
    def __init__(self,img,x,y,target_x,target_y,moveSpeed_x,moveSpeed_y,width=None,height=None,description="Default"):
        ImageSurface.__init__(self,img,x,y,width,height,description)
        self.default_x = x
        self.default_y = y
        self.target_x = target_x
        self.target_y = target_y
        self.moveSpeed_x = moveSpeed_x
        self.moveSpeed_y = moveSpeed_y
        self.__towardTargetPos = False
    def display(self,screen,local_x=0,local_y=0):
        super().display(screen,local_x,local_y)
        if self.__towardTargetPos == True:
            if self.default_x < self.target_x and self.x < self.target_x:
                self.x += self.moveSpeed_x
            elif self.default_x > self.target_x and self.x > self.target_x:
                self.x -= self.moveSpeed_x
            if self.default_y < self.target_y and self.y < self.target_y:
                self.y += self.moveSpeed_y
            elif self.default_y > self.target_y and self.y > self.target_y:
                self.y -= self.moveSpeed_y
        else:
            if self.default_x < self.target_x and self.x > self.default_x:
                self.x -= self.moveSpeed_x
            elif self.default_x > self.target_x and self.x < self.default_x:
                self.x += self.moveSpeed_x
            if self.default_y < self.target_y and self.y > self.default_y:
                self.y -= self.moveSpeed_y
            elif self.default_y > self.target_y and self.y < self.default_y:
                self.y += self.moveSpeed_y
    def draw(self,screen):
        self.display(screen)
    def switch(self):
        self.__towardTargetPos = not self.__towardTargetPos
    def ifToward(self):
        return self.__towardTargetPos

#进度条
class ProgressBar(ImageInterface):
    def __init__(self,x,y,max_width,height,color):
        ImageInterface.__init__(self,None,x,y,max_width,height)
        self.percentage = 0
        self.color = findColorRGBA(color)
    def draw(self,screen):
        pygame.draw.rect(screen,self.color,(self.x,self.y,self.width*self.percentage,self.height))

#环境系统
class WeatherSystem:
    def  __init__(self,weather,window_x,window_y,entityNum=50):
        self.name = 0
        self.img_list = [pygame.image.load(os.path.join(imgPath)).convert_alpha() for imgPath in glob.glob("Assets/image/environment/"+weather+"/*.png")]
        self.ImgObject = []
        for i in range(entityNum):
            imgId = random.randint(0,len(self.img_list)-1)
            img_size = random.randint(5,10)
            img_speed = random.randint(1,4)
            img_x = random.randint(1,window_x*1.5)
            img_y = random.randint(1,window_y)
            self.ImgObject.append(Snow(imgId,img_size,img_speed,img_x,img_y))
    def display(self,screen,perBlockWidth):
        speed_unit = perBlockWidth/15
        for i in range(len(self.ImgObject)):
            if 0 <= self.ImgObject[i].x <= screen.get_width() and 0 <= self.ImgObject[i].y <= screen.get_height():
                imgTemp = pygame.transform.scale(self.img_list[self.ImgObject[i].imgId], (round(perBlockWidth/self.ImgObject[i].size), round(perBlockWidth/self.ImgObject[i].size)))
                screen.blit(imgTemp,(self.ImgObject[i].x,self.ImgObject[i].y))
            self.ImgObject[i].move(speed_unit)
            if self.ImgObject[i].x <= 0 or self.ImgObject[i].y >= screen.get_height():
                self.ImgObject[i].y = random.randint(-50,0)
                self.ImgObject[i].x = random.randint(0,screen.get_width()*2)

#雪花片
class Snow:
    def  __init__(self,imgId,size,speed,x,y):
        self.imgId = imgId
        self.size = size
        self.speed = speed
        self.x = x
        self.y = y
    def move(self,speed_unit):
        self.x -= self.speed*speed_unit
        self.y += self.speed*speed_unit

#设置UI
class SettingContoller:
    def __init__(self,window_x,window_y,langTxt):
        self.ifDisplay = False
        self.baseImgWidth = round(window_x/3)
        self.baseImgHeight = round(window_x/3)
        self.baseImg = pygame.transform.scale(pygame.image.load(os.path.join("Assets/image/UI/setting_baseImg.png")).convert_alpha(),(self.baseImgWidth,self.baseImgHeight))
        self.baseImg.set_alpha(200)
        self.baseImgX = int((window_x-self.baseImgWidth)/2)
        self.baseImgY = int((window_y-self.baseImgHeight)/2)
        self.bar_height = round(window_x/60)
        self.bar_width = round(window_x/5)
        self.button = pygame.transform.scale(pygame.image.load(os.path.join("Assets/image/UI/setting_bar_circle.png")).convert_alpha(),(self.bar_height,self.bar_height*2))
        self.bar_empty = pygame.transform.scale(pygame.image.load(os.path.join("Assets/image/UI/setting_bar_empty.png")).convert_alpha(),(self.bar_width,self.bar_height))
        self.bar_full = pygame.transform.scale(pygame.image.load(os.path.join("Assets/image/UI/setting_bar_full.png")).convert_alpha(),(self.bar_width,self.bar_height))
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
        self.FONTSIZE = round(window_x/50)
        self.fontSizeBig = round(window_x/50*1.5)
        self.normalFont = createFont(self.FONTSIZE)
        self.bigFont = createFont(self.fontSizeBig)
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
    def display(self,screen):
        if self.ifDisplay == True:
            #底部图
            screen.blit(self.baseImg,(self.baseImgX,self.baseImgY))
            screen.blit(self.settingTitleTxt,(self.settingTitleTxt_x,self.settingTitleTxt_y))
            #语言
            screen.blit(self.languageTxt,(self.bar_x,self.bar_y0))
            #背景音乐
            screen.blit(self.normalFont.render(self.backgroundMusicTxt+": "+str(self.soundVolume_background_music),True,(255, 255, 255)),(self.bar_x,self.bar_y1-self.FONTSIZE*1.4))
            screen.blit(self.bar_empty,(self.bar_x,self.bar_y1))
            barImgWidth = round(self.bar_full.get_width()*self.soundVolume_background_music/100)
            screen.blit(pygame.transform.scale(self.bar_full,(barImgWidth,self.bar_height)),(self.bar_x,self.bar_y1))
            screen.blit(self.button,(self.bar_x+barImgWidth-self.button.get_width()/2,self.bar_y1-self.bar_height/2))
            #音效
            screen.blit(self.normalFont.render(self.soundEffectsTxt+": "+str(self.soundVolume_sound_effects),True,(255, 255, 255)),(self.bar_x,self.bar_y2-self.FONTSIZE*1.4))
            screen.blit(self.bar_empty,(self.bar_x,self.bar_y2))
            barImgWidth = round(self.bar_full.get_width()*self.soundVolume_sound_effects/100)
            screen.blit(pygame.transform.scale(self.bar_full,(barImgWidth,self.bar_height)),(self.bar_x,self.bar_y2))
            screen.blit(self.button,(self.bar_x+barImgWidth-self.button.get_width()/2,self.bar_y2-self.bar_height/2))
            #环境声
            screen.blit(self.normalFont.render(self.soundEnvironmentTxt+": "+str(self.soundVolume_sound_environment),True,(255, 255, 255)),(self.bar_x,self.bar_y3-self.FONTSIZE*1.4))
            screen.blit(self.bar_empty,(self.bar_x,self.bar_y3))
            barImgWidth = round(self.bar_full.get_width()*self.soundVolume_sound_environment/100)
            screen.blit(pygame.transform.scale(self.bar_full,(barImgWidth,self.bar_height)),(self.bar_x,self.bar_y3))
            screen.blit(self.button,(self.bar_x+barImgWidth-self.button.get_width()/2,self.bar_y3-self.bar_height/2))
            #获取鼠标坐标
            mouse_x,mouse_y=pygame.mouse.get_pos()
            #取消按钮
            if self.buttons_x1<mouse_x<self.buttons_x1+self.cancelTxt_n.get_width() and self.buttons_y<mouse_y<self.buttons_y+self.cancelTxt_n.get_height():
                screen.blit(self.cancelTxt_b,(self.buttons_x1,self.buttons_y))
                if controller.get_event() == "comfirm":
                    self.soundVolume_background_music = get_setting("Sound","background_music")
                    self.soundVolume_sound_effects = get_setting("Sound","sound_effects")
                    self.soundVolume_sound_environment = get_setting("Sound","sound_environment")
                    self.ifDisplay = False
            else:
                screen.blit(self.cancelTxt_n,(self.buttons_x1,self.buttons_y))
            #确认按钮
            if self.buttons_x2<mouse_x<self.buttons_x2+self.confirmTxt_n.get_width() and self.buttons_y<mouse_y<self.buttons_y+self.confirmTxt_n.get_height():
                screen.blit(self.confirmTxt_b,(self.buttons_x2,self.buttons_y))
                if controller.get_event() == "comfirm":
                    set_setting("Sound","background_music",self.soundVolume_background_music)
                    set_setting("Sound","sound_effects",self.soundVolume_sound_effects)
                    set_setting("Sound","sound_environment",self.soundVolume_sound_environment)
                    save_setting()
                    pygame.mixer.music.set_volume(self.soundVolume_background_music/100.0)
                    self.ifDisplay = False
                    return True
            else:
                screen.blit(self.confirmTxt_n,(self.buttons_x2,self.buttons_y))
            #其他按键的判定按钮
            if controller.get_event() == "comfirm":
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

#按钮
class Button(GameObject):
    def __init__(self,path,x,y):
        GameObject.__init__(self,x,y)
        self.img = pygame.image.load(os.path.join(path)).convert_alpha() if isinstance(path,str) else path
        self.img2 = None
        self.hoverEventTriggered = False
    def setHoverImg(self,img):
        self.img2 = img
    def display(self,screen,local_x=0,local_y=0):
        screen.blit(self.img,(self.x+local_x,self.y+local_y))
    def hoverEventOn(self):
        if self.img2 != None and self.hoverEventTriggered == False:
            tempSurface = self.img
            self.img = self.img2
            self.img2 = tempSurface
            self.hoverEventTriggered = True
    def hoverEventOff(self):
        if self.img2 != None and self.hoverEventTriggered == True:
            tempSurface = self.img
            self.img = self.img2
            self.img2 = tempSurface
            self.hoverEventTriggered = False
    def draw(self,screen,local_x=0,local_y=0):
        self.display(screen,local_x,local_y)
    def get_width(self):
        return self.img.get_width()
    def get_height(self):
        return self.img.get_height()
    def get_size(self):
        return self.img.get_size()

class ButtonWithDes(Button):
    def __init__(self,path,x,y,width,height,des):
        Button.__init__(self,path,x,y)
        width = int(width)
        height = int(height)
        self.img = pygame.transform.scale(self.img,(width,height))
        self.img2 = self.img.copy()
        self.img.set_alpha(150)
        self.width = width
        self.height = height
        self.des = des
        self.des_font_surface = fontRender(des,"black",self.height*0.4)
        self.des_surface = pygame.Surface((self.des_font_surface.get_width()*1.2,self.height*0.6),flags=pygame.SRCALPHA).convert_alpha()
        pygame.draw.rect(self.des_surface,(255,255,255),(0,0, self.des_surface.get_width(),self.des_surface.get_height()))
        self.des_surface.blit(self.des_font_surface,(self.des_font_surface.get_width()*0.1,0))
    def displayDes(self,screen):
        if self.hoverEventTriggered == True:
            screen.blit(self.des_surface,pygame.mouse.get_pos())

class ButtonWithFadeInOut(Button):
    def __init__(self,buttonImgPath,txt,txt_color,alphaWhenNotHovered,x,y,height):
        Button.__init__(self,buttonImgPath,x,y)
        txtSurface = fontRender(txt,txt_color,height*0.6)
        self.img = pygame.transform.scale(self.img,(int(txtSurface.get_width()+height),int(height)))
        self.img.blit(txtSurface,(height*0.5,height*0.15))
        self.img2 = self.img.copy()
        self.img.set_alpha(alphaWhenNotHovered)

#对话框基础模块
class DialogInterface:
    def __init__(self,img,fontSize):
        self.dialoguebox = img
        self.FONTSIZE = int(fontSize)
        self.FONT = createFont(self.FONTSIZE)
        self.content = []
        self.narrator = None
        self.textIndex = None
        self.displayedLine = None
    def update(self,txt,narrator):
        self.textIndex = 0
        self.displayedLine = 0
        self.content = txt
        self.narrator = narrator

#对话框和对话框内容
class DialogBox(DialogInterface,GameObject):
    def __init__(self,imgPath,width,height,x,y,fontSize):
        DialogInterface.__init__(self,pygame.transform.scale(pygame.image.load(os.path.join(imgPath)).convert_alpha(),(int(width),int(height))),fontSize)
        GameObject.__init__(self,x,y)
        self.__surface = None
        self.deafult_x = x
        self.deafult_y = y
        self.txt_x = fontSize
        self.txt_y = fontSize*2
        self.narrator_icon = None
        self.narrator_x = fontSize*3
        self.narrator_y = fontSize/2
        self.updated = False
        self.drew = False
        self.__flipped = False
    def get_width(self):
        return self.dialoguebox.get_width()
    def get_height(self):
        return self.dialoguebox.get_height()
    def set_size(self,width,height):
        self.dialoguebox = pygame.transform.scale(self.dialoguebox,(int(width),int(height)))
    def display(self,screen,characterInfoBoardUI=None):
        #如果对话框需要继续更新
        if self.drew == False:
            self.__surface = self.dialoguebox.copy()
            if self.__flipped == True:
                #讲述人名称
                if self.narrator != None:
                    self.__surface.blit(self.FONT.render(self.narrator,get_fontMode(),(255,255,255)),(self.get_width()*0.6+self.narrator_x,self.narrator_y))
                #角色图标
                if self.narrator_icon != None and characterInfoBoardUI != None:
                    img = characterInfoBoardUI.characterIconImages[self.narrator_icon]
                    self.__surface.blit(img,(self.get_width()-self.txt_x,self.txt_y))
                x = self.txt_x
            else:
                #讲述人名称
                if self.narrator != None:
                    self.__surface.blit(self.FONT.render(self.narrator,get_fontMode(),(255,255,255)),(self.narrator_x,self.narrator_y))
                #角色图标
                if self.narrator_icon != None and characterInfoBoardUI != None:
                    img = characterInfoBoardUI.characterIconImages[self.narrator_icon]
                    self.__surface.blit(img,(self.txt_x,self.txt_y))
                    x = self.txt_x+img.get_width() + self.FONTSIZE
                else:
                    x = self.txt_x
            y = self.txt_y
            if len(self.content)>0:
                #已经播放的行
                for i in range(self.displayedLine):
                    self.__surface.blit(self.FONT.render(self.content[i],get_fontMode(),(255,255,255)),(x,y))
                    y += self.FONTSIZE*1.2
                #正在播放的行
                content = self.FONT.render(self.content[self.displayedLine][:self.textIndex],get_fontMode(),(255,255,255))
                self.__surface.blit(content,(x,y))
                if self.textIndex < len(self.content[self.displayedLine]):
                    self.textIndex += 1
                elif self.displayedLine < len(self.content)-1:
                    self.displayedLine += 1
                    self.textIndex = 0
                elif self.textIndex >= len(self.content[self.displayedLine]):
                    self.drew = True
        screen.blit(self.__surface,(self.x,self.y))
    def update(self,txt,narrator,narrator_icon=None):
        super().update(txt,narrator)
        self.updated = True
        self.drew = False
        self.narrator_icon = narrator_icon
    def reset(self):
        self.x = self.deafult_x
        self.y = self.deafult_y
        self.updated = False
        #刷新对话框surface防止上一段的对话还残留在surface上
        self.content = []
        self.__surface = self.dialoguebox.copy()
    def flip(self):
        self.dialoguebox = pygame.transform.flip(self.dialoguebox,True,False)
        self.__flipped = not self.__flipped

#输入框Interface，请勿实体化
class InputBoxInterface(GameObject):
    def __init__(self,x,y,font_size,txt_color,default_width):
        GameObject.__init__(self,x,y)
        self.FONTSIZE = font_size
        self.FONT = createFont(self.FONTSIZE)
        self.default_width = default_width
        self.deafult_height = self.FONTSIZE*1.5
        self.input_box = pygame.Rect(x, y, default_width, self.deafult_height)
        self.color = pygame.Color('lightskyblue3')
        self.txt_color = txt_color
        self.active = False
        self._text = None
        self._holder = self.FONT.render("|",get_fontMode(),self.txt_color)
        self.holderIndex = 0
        self.needSave = False
    def get_width(self):
        return self.input_box.w
    def get_height(self):
        return self.input_box.h
    def get_fontsize(self):
        return self.FONTSIZE
    def set_fontsize(self,font_size):
        self.FONTSIZE = font_size
        self.FONT = createFont(self.FONTSIZE)
    def set_pos(self,x,y):
        self.x = x
        self.y = y
        self.input_box = pygame.Rect(x, y, self.default_width, self.FONTSIZE*1.5)

#单行输入框
class SingleLineInputBox(InputBoxInterface):
    def __init__(self,x,y,font_size,txt_color,default_width=150):
        InputBoxInterface.__init__(self,x,y,font_size,txt_color,default_width)
        self._text = ""
    def get_text(self):
        self.needSave = False
        if self._text == "":
            return None
        else:
            return self._text
    def set_text(self,new_txt=None):
        if new_txt != None and len(new_txt)>0:
            self._text = new_txt
            self.holderIndex = len(new_txt)-1
        else:
            self._text = ""
            self.holderIndex = 0
        self._reset_inputbox_width()
    def _add_char(self,char):
        if len(char) > 0:
            self._text = self._text[:self.holderIndex]+char+self._text[self.holderIndex:]
            self.holderIndex += len(char)
            self._reset_inputbox_width()
        else:
            print('LinpgEngine-Warning: The value of event.unicode is empty!')
    def _remove_char(self,action):
        if action == "ahead":
            if self.holderIndex > 0:
                self._text = self._text[:self.holderIndex-1]+self._text[self.holderIndex:]
                self.holderIndex -= 1
        elif action == "behind":
            if self.holderIndex < len(self._text):
                self._text = self._text[:self.holderIndex]+self._text[self.holderIndex+1:]
        else:
            raise Exception('LinpgEngine-Error: Action has to be either "ahead" or "behind"!')
        self._reset_inputbox_width()
    def _reset_holderIndex(self,mouse_x):
        last_width = 0
        local_x = mouse_x-self.x
        new_width = 0
        i = 0
        for i in range(len(self._text)):
            new_width = self.FONT.size(self._text[:i])[0]+self.FONTSIZE*0.25
            if new_width>local_x:
                break
            else:
                last_width = new_width
        if (new_width-local_x) < (local_x-last_width):
            self.holderIndex = i
        else:
            self.holderIndex = i-1
    def _reset_inputbox_width(self):
        if self._text != None and len(self._text)>0:
            self.input_box.w = max(self.default_width, self.FONT.size(self._text)[0]+self.FONTSIZE*0.6)
        else:
            self.input_box.w = self.default_width
    def _keyDownEvents(self,event):
        if event.key == pygame.K_BACKSPACE:
            self._remove_char("ahead")
            return True
        elif event.key == pygame.K_DELETE:
            self._remove_char("behind")
            return True
        elif event.key == pygame.K_LEFT and self.holderIndex > 0:
            self.holderIndex -= 1
            return True
        elif event.key == pygame.K_RIGHT and self.holderIndex < len(self._text):
            self.holderIndex += 1
            return True
        elif event.key == pygame.K_LCTRL and pygame.key.get_pressed()[pygame.K_v] or event.key == pygame.K_v and pygame.key.get_pressed()[pygame.K_LCTRL]:
            self._add_char(Tk().clipboard_get())
            return True
        return False
    def display(self,screen,pygame_events=pygame.event.get()):
        mouse_x,mouse_y = pygame.mouse.get_pos()
        for event in pygame_events:
            if self.active:
                if event.type == pygame.KEYDOWN:
                    if self._keyDownEvents(event):
                        pass
                    elif event.key == pygame.K_ESCAPE:
                        self.active = False
                        self.needSave = True
                    else:
                        self._add_char(event.unicode)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.x<=mouse_x<=self.x+self.input_box.w and self.y<=mouse_y<=self.y+self.input_box.h:
                        self._reset_holderIndex(mouse_x)
                    else:
                        self.active = False
                        self.needSave = True
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.x<=mouse_x<=self.x+self.input_box.w and self.y<=mouse_y<=self.y+self.input_box.h:
                self.active = True
                self._reset_holderIndex(mouse_x)
        # 画出文字
        if self._text != None and len(self._text) > 0:
            screen.blit(self.FONT.render(self._text,get_fontMode(),findColorRGBA(self.txt_color)), (self.x+self.FONTSIZE*0.25,self.y))
        #画出输入框
        if self.active:
            pygame.draw.rect(screen, self.color, self.input_box, 2)
            #画出 “|” 符号
            if int(time.time()%2)==0 or len(pygame_events)>0:
                screen.blit(self._holder, (self.x+self.FONTSIZE*0.25+self.FONT.size(self._text[:self.holderIndex])[0], self.y))

#多行输入框
class MultipleLinesInputBox(InputBoxInterface):
    def __init__(self,x,y,font_size,txt_color,default_width=150):
        InputBoxInterface.__init__(self,x,y,font_size,txt_color,default_width)
        self._text = [""]
        self.lineId = 0
    def get_text(self):
        self.needSave = False
        if len(self._text) == 0 or self._text == [""]:
            return None
        else:
            return self._text
    def set_text(self,new_txt=None):
        if new_txt == None or len(self._text) == 0:
            self._text = [""]
        elif isinstance(new_txt,list):
            self._text = new_txt
            self._reset_inputbox_size()
        else:
            raise Exception('LinpgEngine-Error: new_txt for MultipleLinesInputBox.set_text() must be a list!')
    def set_fontsize(self,font_size):
        super().set_fontsize(font_size)
        self._reset_inputbox_size()
    def _reset_inputbox_width(self):
        if self._text != None and len(self._text) > 0:
            width = self.default_width
            for txtTmp in self._text:
                new_width = self.FONT.size(txtTmp)[0]+self.FONTSIZE/2
                if new_width > width:
                    width = new_width
        else:
            width = self.default_width
        self.input_box.w = width
    def _reset_inputbox_height(self):
        self.input_box.h = self.deafult_height*len(self._text)
    def _reset_inputbox_size(self):
        self._reset_inputbox_width()
        self._reset_inputbox_height()
    def _add_char(self,char):
        if len(char) > 0:
            if "\n" not in char:
                self._text[self.lineId] = self._text[self.lineId][:self.holderIndex]+char+self._text[self.lineId][self.holderIndex:]
                self.holderIndex += len(char)
                self._reset_inputbox_width()
            else:
                theStringAfterHolderIndex = self._text[self.lineId][self.holderIndex:]
                self._text[self.lineId] = self._text[self.lineId][:self.holderIndex]
                for i in range(len(char)-1):
                    if char[i] != '\n':
                        self._text[self.lineId] += char[i]
                        self.holderIndex += 1
                    else:
                        self.lineId += 1
                        self._text.insert(self.lineId,"")
                        self.holderIndex = 0
                self._text[self.lineId] += theStringAfterHolderIndex
                self._reset_inputbox_size()
        else:
            print('LinpgEngine-Warning: The value of event.unicode is empty!')
    #删除对应字符
    def _remove_char(self,action):
        if action == "ahead":
            if self.holderIndex > 0:
                self._text[self.lineId] = self._text[self.lineId][:self.holderIndex-1]+self._text[self.lineId][self.holderIndex:]
                self.holderIndex -= 1
            elif self.lineId > 0:
                #如果当前行有内容
                if len(self._text[self.lineId]) > 0:
                    self.holderIndex = len(self._text[self.lineId-1])
                    self._text[self.lineId-1] += self._text[self.lineId]
                    self._text.pop(self.lineId)
                    self.lineId -= 1
                else:
                    self._text.pop(self.lineId)
                    self.lineId -= 1
                    self.holderIndex = len(self._text[self.lineId])
        elif action == "behind":
            if self.holderIndex < len(self._text[self.lineId]):
                self._text[self.lineId] = self._text[self.lineId][:self.holderIndex]+self._text[self.lineId][self.holderIndex+1:]
            elif self.lineId < len(self._text)-1:
                #如果下一行有内容
                if len(self._text[self.lineId+1]) > 0:
                    self._text[self.lineId] += self._text[self.lineId+1]
                self._text.pop(self.lineId+1)
        else:
            raise Exception('LinpgEngine-Error: Action has to be either "ahead" or "behind"!')
        self._reset_inputbox_size()
    def _reset_holderIndex(self,mouse_x,mouse_y):
        self.lineId = round((mouse_y-self.y)/self.FONTSIZE)-1
        if self.lineId < 0:
            self.lineId = 0
        elif self.lineId >= len(self._text):
            self.lineId = len(self._text)-1
        last_width = 0
        local_x = mouse_x-self.x
        new_width = 0
        i = 0
        for i in range(len(self._text[self.lineId])):
            new_width = self.FONT.size(self._text[self.lineId][:i])[0]+self.FONTSIZE*0.25
            if new_width>local_x:
                break
            else:
                last_width = new_width
        if (new_width-local_x) < (local_x-last_width):
            self.holderIndex = i
        else:
            self.holderIndex = i-1
    def display(self,screen,pygame_events=None):
        if pygame_events == None:
            pygame_events = pygame.event.get()
        mouse_x,mouse_y = pygame.mouse.get_pos()
        for event in pygame_events:
            if self.active:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        self._remove_char("ahead")
                    elif event.key == pygame.K_DELETE:
                        self._remove_char("behind")
                    elif event.key == pygame.K_LEFT and self.holderIndex > 0:
                        self.holderIndex -= 1
                    elif event.key == pygame.K_RIGHT and self.holderIndex < len(self._text[self.lineId]):
                        self.holderIndex += 1
                    elif event.key == pygame.K_UP and self.lineId>0:
                        self.lineId -= 1
                        if self.holderIndex > len(self._text[self.lineId])-1:
                            self.holderIndex = len(self._text[self.lineId])-1
                    elif event.key == pygame.K_DOWN and self.lineId<len(self._text)-1:
                        self.lineId += 1
                        if self.holderIndex > len(self._text[self.lineId])-1:
                            self.holderIndex = len(self._text[self.lineId])-1
                    elif event.key == pygame.K_LCTRL and pygame.key.get_pressed()[pygame.K_v] or event.key == pygame.K_v and pygame.key.get_pressed()[pygame.K_LCTRL]:
                        self._add_char(Tk().clipboard_get())
                        return True
                    #ESC，关闭
                    elif event.key == pygame.K_ESCAPE:
                        self.active = False
                        self.needSave = True
                    elif event.key == pygame.K_RETURN:
                        #如果“|”位于最后
                        if self.holderIndex == len(self._text[self.lineId]):
                            self._text.insert(self.lineId+1,"")
                        else:
                            self._text.insert(self.lineId+1,self._text[self.lineId][self.holderIndex:])
                            self._text[self.lineId] = self._text[self.lineId][:self.holderIndex]
                        self.lineId+=1
                        self.holderIndex=0
                        self._reset_inputbox_size()
                    else:
                        self._add_char(event.unicode)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.x<=mouse_x<=self.x+self.input_box.w and self.y<=mouse_y<=self.y+self.input_box.h:
                        self._reset_holderIndex(mouse_x,mouse_y)
                    else:
                        self.active = False
                        self.needSave = True
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.x<=mouse_x<=self.x+self.input_box.w and self.y<=mouse_y<=self.y+self.input_box.h:
                self.active = True
                self._reset_holderIndex(mouse_x,mouse_y)
        if self._text != None:
            for i in range(len(self._text)): 
                # 画出文字
                screen.blit(self.FONT.render(self._text[i],get_fontMode(),findColorRGBA(self.txt_color)),(self.x+self.FONTSIZE*0.25,self.y+i*self.deafult_height))
        if self.active:
            # 画出输入框
            pygame.draw.rect(screen, self.color, self.input_box, 2)
            #画出 “|” 符号
            if int(time.time()%2)==0 or len(pygame_events)>0:
                screen.blit(self._holder, (self.x+self.FONTSIZE*0.1+self.FONT.size(self._text[self.lineId][:self.holderIndex])[0], self.y+self.lineId*self.deafult_height))

#控制台
class Console(SingleLineInputBox):
    def __init__(self,x,y,font_size=32,default_width=150):
        self.color_inactive = pygame.Color('lightskyblue3')
        self.color_active = pygame.Color('dodgerblue2')
        SingleLineInputBox.__init__(self,x,y,font_size,self.color_active,default_width)
        self.color = self.color_active
        self.active = True
        self.hidden = True
        self.textHistory = []
        self.backwordID = 1
        self.events = {}
        self.txtOutput = []
    def get_events(self,key=None):
        if key==None:
            return self.events
        elif key!=None and key in self.events:
            return self.events[key]
        else:
            return None
    def _keyDownEvents(self,event):
        if super()._keyDownEvents(event):
            return True
        #向上-过去历史
        elif event.key == pygame.K_UP and self.backwordID<len(self.textHistory):
            self.backwordID += 1
            self.set_text(self.textHistory[len(self.textHistory)-self.backwordID])
            return True
        #向下-过去历史，最近的一个
        elif event.key == pygame.K_DOWN and self.backwordID>1:
            self.backwordID -= 1
            self.set_text(self.textHistory[len(self.textHistory)-self.backwordID])
            return True
        #回车
        elif event.key == pygame.K_RETURN:
            if len(self._text)>0:
                if self._text[0]=="/":
                    if self._text == "/cheat on":
                        self.events["cheat"] = True
                        self.txtOutput.append("Cheat mode activated")
                    elif self._text == "/cheat off":
                        self.events["cheat"] = False
                        self.txtOutput.append("Cheat mode deactivated")
                    elif self._text[:5] == "/say ":
                        self.txtOutput.append(self._text[5:])
                    elif self._text == "/dev on":
                        self.txtOutput.append("Development mode activated")
                        self.events["dev"] = True
                    elif self._text == "/dev off":
                        self.txtOutput.append("Development mode deactivated")
                        self.events["dev"] = False
                    else:
                        self.txtOutput.append("Unknown command")
                else:
                    self.txtOutput.append(self._text)
                self.textHistory.append(self._text) 
                self.set_text()
                self.backwordID = 1
            else:
                print('LinpgEngine-Warning: The input box is empty!')
            return True
        #ESC，关闭
        elif event.key == pygame.K_ESCAPE:
            self.active = False
            # Change the current color of the input box.
            self.color = self.color_active if self.active else self.color_inactive
            return True
        return False
    def display(self,screen,pygame_events=pygame.event.get()):
        if self.hidden == True:
            for event in pygame_events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_BACKQUOTE:
                    self.hidden = False
                    break
        elif self.hidden == False:
            for event in pygame_events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x,mouse_y = pygame.mouse.get_pos()
                    if self.x <= mouse_x <= self.x+self.input_box.w and self.y <= mouse_y <= self.y+self.input_box.h:
                        self.active = not self.active
                        # Change the current color of the input box.
                        self.color = self.color_active if self.active else self.color_inactive
                    else:
                        self.active = False
                        self.color = self.color_inactive
                elif event.type == pygame.KEYDOWN:
                    if self.active:
                        if self._keyDownEvents(event):
                            pass
                        else:
                            self._add_char(event.unicode)
                    else:
                        if event.key == pygame.K_BACKQUOTE or event.key == pygame.K_ESCAPE:
                            self.hidden = True
                            self.set_text()
            #画出输出信息
            for i in range(len(self.txtOutput)):
                screen.blit(self.FONT.render(self.txtOutput[i],get_fontMode(),self.color),(self.x+self.FONTSIZE*0.25, self.y-(len(self.txtOutput)-i)*self.FONTSIZE*1.5))
            # 画出文字
            if self._text != None and len(self._text) > 0:
                screen.blit(self.FONT.render(self._text,get_fontMode(),self.color),(self.x+self.FONTSIZE*0.25, self.y))
            #画出输入框
            pygame.draw.rect(screen, self.color, self.input_box, 2)
            #画出 “|” 符号
            if int(time.time()%2)==0 or len(pygame_events)>0:
                screen.blit(self._holder, (self.x+self.FONTSIZE*0.25+self.FONT.size(self._text[:self.holderIndex])[0], self.y))

#初始化控制台模块
console = Console(0,0)

#gif图片管理
class GifObject(GameObject):
    def __init__(self,imgList,x,y,width,height,updateGap):
        GameObject.__init__(self,x,y)
        self.imgList = imgList
        self.imgId = 0
        self.width = int(width)
        self.height = int(height)
        self.updateGap = updateGap
        self.countDown = 0
        self.alpha = 255
    def display(self,screen):
        img = pygame.transform.scale(self.imgList[self.imgId],(self.width,self.height))
        if self.alpha != 255:
            img.set_alpha(self.alpha)
        screen.blit(img,(self.x,self.y))
        if self.countDown >= self.updateGap:
            self.countDown = 0
            self.imgId += 1
            if self.imgId == len(self.imgList):
                self.imgId = 0
        else:
            self.countDown += 1
    def set_pos(self,x=None,y=None):
        self.x = x if x != None else self.x
        self.y = y if y != None else self.y
    def draw(self,screen):
        self.display(screen)
    def set_alpha(self,alpha):
        self.alpha = alpha

#暂停菜单
class PauseMenu:
    def __init__(self):
        self.white_bg = None
        self.button_resume = None
        self.button_save = None
        self.button_setting = None
        self.button_back = None
        self.ifBackToMainMenu = False
        self.ifSave = False
    def __initial(self,screen):
        width,height = display.get_size()
        surfaceTmp = pygame.Surface((width,height),flags=pygame.SRCALPHA).convert_alpha()
        pygame.draw.rect(surfaceTmp,(0,0,0),(0,0,width,height))
        self.white_bg = ImageSurface(surfaceTmp,0,0,width,height)
        self.white_bg.set_alpha(50)
        self.button_resume = fontRenderPro(get_lang("MainMenu","menu_main")["0_continue"],"white",(screen.get_width()*0.1,screen.get_height()*0.4,screen.get_width()/38))
        self.button_save = fontRenderPro(get_lang("SaveGame"),"white",(screen.get_width()*0.1,screen.get_height()*0.5,screen.get_width()/38))
        self.button_setting = fontRenderPro(get_lang("MainMenu","menu_main")["5_setting"],"gray",(screen.get_width()*0.1,screen.get_height()*0.6,screen.get_width()/38))
        self.button_back = fontRenderPro(get_lang("DialogCreator","back"),"white",(screen.get_width()*0.1,screen.get_height()*0.7,screen.get_width()/38))
    def checkIfBackToMainMenu(self):
        if self.ifBackToMainMenu == False:
            return False
        else:
            self.ifBackToMainMenu = False
            return True
    def display(self,screen):
        screenshot = screen.copy()
        ifPauseMenu = True
        if self.white_bg == None:
            self.__initial(screen)
        while ifPauseMenu:
            screen.blit(screenshot,(0,0))
            self.white_bg.draw(screen)
            left_click = False
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    ifPauseMenu = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    left_click = True
            #判定按钮
            if self.button_resume.ifHover() and left_click == True:
                ifPauseMenu = False
            if self.button_back.ifHover() and left_click == True:
                ifPauseMenu = False
                self.ifBackToMainMenu = True
            if self.button_save.ifHover() and left_click == True:
                ifPauseMenu = False
                self.ifSave = True
            #展示按钮
            self.button_resume.draw(screen)
            self.button_save.draw(screen)
            self.button_setting.draw(screen)
            self.button_back.draw(screen)
            display.flip()
#暂停菜单
pause_menu = PauseMenu()

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
                self.sound_id = random.randint(0,len(self.__sounds_list)-1)
            else:
                self.sound_id = sound_id
            pygame.mixer.Channel(self.channel_id).play(self.__sounds_list[self.sound_id])
    def stop(self):
        pygame.mixer.Channel(self.channel_id).stop()
    def set_volume(self,volume):
        for i in range(len(self.__sounds_list)):
            self.__sounds_list[i].set_volume(volume)