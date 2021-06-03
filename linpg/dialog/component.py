# cython: language_level=3
from .movie import *

#ui路径
DIALOG_UI_PATH:str = os.path.join("Assets", "image", "UI")

#对话框和对话框内容
class DialogContent:
    def __init__(self, fontSize:int_f):
        self.dialoguebox = quickly_load_img(os.path.join(DIALOG_UI_PATH, "dialoguebox.png"))
        self.FONTSIZE = int(fontSize)
        self.FONT = create_font(self.FONTSIZE)
        self.content = []
        self.narrator = None
        self.textIndex = None
        self.displayedLine = None
        try:
            self.__textPlayingSound = load_sound(r"Assets/sound/ui/dialog_words_playing.ogg")
        except FileNotFoundError:
            self.__textPlayingSound = None
            throw_exception(
                "warning",
                "Cannot find 'dialog_words_playing.ogg' in 'Assets/sound/ui'!\nAs a result, the text playing sound will be disabled."
                )
        self.READINGSPEED = get_setting("ReadingSpeed")
        self.dialoguebox_max_height = None
        #鼠标图标
        self.mouseImg = load_gif(
            (os.path.join(DIALOG_UI_PATH,"mouse_none.png"), os.path.join(DIALOG_UI_PATH,"mouse.png")),
            (display.get_width()*0.82,display.get_height()*0.83),(self.FONTSIZE,self.FONTSIZE), 50
            )
        self.hidden:bool = False
        self.readTime = 0
        self.totalLetters = 0
        self.autoMode = False
        self.reset()
    #是否所有内容均已展出
    def is_all_played(self) -> bool:
        #如果self.content是空的，也就是说没有任何内容，那么应当视为所有内容都被播放了
        if len(self.content) == 0:
            return True
        else:
            return self.displayedLine >= len(self.content)-1 and self.textIndex >= len(self.content[self.displayedLine])-1
    #立刻播出所有内容
    def play_all(self) -> None:
        if not self.is_all_played():
            self.displayedLine = len(self.content)-1
            self.textIndex = len(self.content[self.displayedLine])-1
    #更新内容
    def update(self, txt:list, narrator:str, forceNotResizeDialoguebox:bool=False) -> None:
        self.totalLetters = 0
        self.readTime = 0
        for i in range(len(self.content)):
            self.totalLetters += len(self.content[i])
        if self.narrator != narrator and not forceNotResizeDialoguebox:
            self.__fade_out_stage = True
        self.textIndex = 0
        self.displayedLine = 0
        self.content = txt
        self.narrator = narrator
        self.stop_playing_text_sound()
    def reset(self) -> None:
        self.__fade_out_stage = False
        self.dialoguebox_height = 0
        self.dialoguebox_y = None
        self.__txt_alpha = 255
    #获取文字播放时的音效的音量
    def get_sound_volume(self) -> float: 
        if self.__textPlayingSound is not None:
            return self.__textPlayingSound.get_volume()
        else:
            return 0.0
    #修改文字播放时的音效的音量
    def set_sound_volume(self, num:Union[float,int]) -> None:
        if self.__textPlayingSound is not None: self.__textPlayingSound.set_volume(num/100.0)
    #是否需要更新
    def needUpdate(self) -> bool:
        return True if self.autoMode and self.readTime >= self.totalLetters else False
    #渲染文字
    def render_font(self, txt:str, color:tuple) -> ImageSurface: return self.FONT.render(txt,get_antialias(),color)
    #如果音效还在播放则停止播放文字音效
    def stop_playing_text_sound(self) -> None:
        if is_any_sound_playing() and self.__textPlayingSound is not None: self.__textPlayingSound.stop()
    #渐入
    def __fade_in(self, surface:ImageSurface) -> None:
        #如果对话框图片的最高高度没有被设置，则根据屏幕大小设置一个
        if self.dialoguebox_max_height is None:
            self.dialoguebox_max_height = surface.get_height()/4
        #如果当前对话框图片的y坐标不存在（一般出现在对话系统例行初始化后），则根据屏幕大小设置一个
        if self.dialoguebox_y is None:
            self.dialoguebox_y = surface.get_height()*0.65+self.dialoguebox_max_height/2
        #画出对话框图片
        surface.blit(smoothly_resize_img(self.dialoguebox,(surface.get_width()*0.74,self.dialoguebox_height)),
        (surface.get_width()*0.13,self.dialoguebox_y))
        #如果对话框图片还在放大阶段
        if self.dialoguebox_height < self.dialoguebox_max_height:
            self.dialoguebox_height = min(
                int(self.dialoguebox_height+self.dialoguebox_max_height*display.sfpsp/10), self.dialoguebox_max_height
                )
            self.dialoguebox_y -= int(self.dialoguebox_max_height*display.sfpsp/20)
        #如果已经放大好了
        else:
            self.__blit_txt(surface)
    #淡出
    def __fade_out(self, surface:ImageSurface) -> None:
        #画出对话框图片
        if self.dialoguebox_y is not None:
            surface.blit(
                smoothly_resize_img(self.dialoguebox,(surface.get_width()*0.74,self.dialoguebox_height)),
                (surface.get_width()*0.13,self.dialoguebox_y)
                )
        if self.dialoguebox_height > 0:
            self.dialoguebox_height = max(int(self.dialoguebox_height-self.dialoguebox_max_height*display.sfpsp/10), 0)
            self.dialoguebox_y += int(self.dialoguebox_max_height*display.sfpsp/20)
        else:
            self.reset()
    #展示
    def draw(self, surface:ImageSurface) -> None:
        if not self.hidden:
            if not self.__fade_out_stage:
                self.__fade_in(surface)
            else:
                self.__fade_out(surface)
    #将文字画到屏幕上
    def __blit_txt(self, surface:ImageSurface) -> None:
        x:int = int(surface.get_width()*0.2)
        y:int = int(surface.get_height()*0.73)
        #写上当前讲话人的名字
        if self.narrator is not None:
            surface.blit(self.render_font(self.narrator,(255, 255, 255)),(x,self.dialoguebox_y+self.FONTSIZE))
        #画出鼠标gif
        self.mouseImg.draw(surface)
        #对话框已播放的内容
        for i in range(self.displayedLine):
            surface.blit(self.render_font(self.content[i],(255, 255, 255)),(x,y+self.FONTSIZE*1.5*i))
        #对话框正在播放的内容
        surface.blit(
            self.render_font(self.content[self.displayedLine][:self.textIndex],(255, 255, 255)),
            (x,y+self.FONTSIZE*1.5*self.displayedLine)
            )
        #如果当前行的字符还没有完全播出
        if self.textIndex < len(self.content[self.displayedLine]):
            if not is_any_sound_playing() and self.__textPlayingSound is not None:
                self.__textPlayingSound.play()
            self.textIndex +=1
        #当前行的所有字都播出后，播出下一行
        elif self.displayedLine < len(self.content)-1:
            if not is_any_sound_playing() and self.__textPlayingSound is not None:
                self.__textPlayingSound.play()
            self.textIndex = 1
            self.displayedLine += 1
        #当所有行都播出后
        else:
            self.stop_playing_text_sound()
            if self.autoMode and self.readTime < self.totalLetters:
                self.readTime += self.READINGSPEED

#对话系统按钮UI模块
class DialogButtons:
    def __init__(self):
        self.__button_hovered:int = 0
        self.hidden:bool = False
        self.initialize()
    #初始化
    def initialize(self) -> None:
        #从设置中读取信息
        window_x,window_y = display.get_size()
        self.FONTSIZE:int = int(window_x*0.0175)
        self.FONT = create_font(self.FONTSIZE)
        #从语言文件中读取按钮文字
        dialog_txt:dict = get_lang("Dialog")
        #生成跳过按钮
        tempButtonIcon = load_img(os.path.join(DIALOG_UI_PATH,"dialog_skip.png"),(self.FONTSIZE,self.FONTSIZE))
        tempButtonTxt = self.FONT.render(dialog_txt["skip"],get_antialias(),(255, 255, 255))
        temp_w = tempButtonTxt.get_width()+self.FONTSIZE*1.5
        self.choiceTxt = dialog_txt["choice"]
        self.skipButton = new_transparent_surface((temp_w,tempButtonTxt.get_height()))
        self.skipButtonHovered = new_transparent_surface((temp_w,tempButtonTxt.get_height()))
        self.icon_y = (tempButtonTxt.get_height()-tempButtonIcon.get_height())/2
        self.skipButtonHovered.blit(tempButtonIcon,(tempButtonTxt.get_width()+self.FONTSIZE*0.5,self.icon_y))
        self.skipButtonHovered.blit(tempButtonTxt,(0,0))
        tempButtonTxt = self.FONT.render(dialog_txt["skip"],get_antialias(),(105, 105, 105))
        tempButtonIcon = add_darkness(tempButtonIcon, 100)
        self.skipButton.blit(tempButtonIcon,(tempButtonTxt.get_width()+self.FONTSIZE*0.5,self.icon_y))
        self.skipButton.blit(tempButtonTxt,(0,0))
        self.skipButton = load_static_image(self.skipButton,(window_x*0.9,window_y*0.05))
        self.skipButtonHovered = load_static_image(self.skipButtonHovered,(window_x*0.9,window_y*0.05))
        #生成自动播放按钮
        self.autoIconHovered = load_img(os.path.join(DIALOG_UI_PATH,"dialog_auto.png"),(self.FONTSIZE,self.FONTSIZE))
        self.autoIcon = add_darkness(self.autoIconHovered, 100)
        self.autoIconDegree = 0
        self.autoIconDegreeChange = (2**0.5-1)*self.FONTSIZE/45
        self.autoMode:bool = False
        tempButtonTxt = self.FONT.render(dialog_txt["auto"],get_antialias(),(105, 105, 105))
        temp_w = tempButtonTxt.get_width()+self.FONTSIZE*1.5
        self.autoButton = new_transparent_surface((temp_w,tempButtonTxt.get_height()))
        self.autoButtonHovered = new_transparent_surface((temp_w,tempButtonTxt.get_height()))
        self.autoButton.blit(tempButtonTxt,(0,0))
        self.autoButtonHovered.blit(self.FONT.render(dialog_txt["auto"],get_antialias(),(255, 255, 255)),(0,0))
        self.autoButton = load_dynamic_image(self.autoButton,(window_x*0.8,window_y*0.05))
        self.autoButton.tag = int(self.autoButton.x+self.autoButton.img.get_width()-self.FONTSIZE)
        self.autoButtonHovered = load_dynamic_image(self.autoButtonHovered,(window_x*0.8,window_y*0.05))
        self.autoButtonHovered.tag = int(self.autoButtonHovered.x+self.autoButtonHovered.img.get_width()-self.FONTSIZE)
        #隐藏按钮
        self.hideButton = load_button(
            os.path.join(DIALOG_UI_PATH,"dialog_hide.png"), (window_x*0.05, window_y*0.05),(self.FONTSIZE,self.FONTSIZE), 150
            )
        #取消隐藏按钮
        self.showButton = load_button(
            os.path.join(DIALOG_UI_PATH,"dialog_show.png"), (window_x*0.05, window_y*0.05),(self.FONTSIZE,self.FONTSIZE), 150
        )
        #历史回溯按钮
        self.historyButton = load_button(
            os.path.join(DIALOG_UI_PATH,"dialog_history.png"), (window_x*0.1, window_y*0.05),(self.FONTSIZE,self.FONTSIZE), 150
        )
    @property
    def item_hovered(self) -> str:
        if self.__button_hovered == 1:
            return "hide"
        elif self.__button_hovered == 2:
            return "skip"
        elif self.__button_hovered == 3:
            return "auto"
        elif self.__button_hovered == 4:
            return "history"
        else:
            return ""
    def draw(self, surface: ImageSurface) -> None:
        self.__button_hovered = 0
        if self.hidden is True:
            self.showButton.draw(surface)
            if self.showButton.is_hover(): self.__button_hovered = 1
        else:
            self.hideButton.draw(surface)
            self.historyButton.draw(surface)
            if self.skipButton.is_hover():
                self.skipButtonHovered.draw(surface)
                self.__button_hovered = 2
            else:
                self.skipButton.draw(surface)
            if self.autoButton.is_hover():
                self.autoButtonHovered.draw(surface)
                if self.autoMode:
                    rotatedIcon = rotate_img(self.autoIconHovered, self.autoIconDegree)
                    surface.blit(rotatedIcon,(
                        self.autoButtonHovered.tag+self.autoIconHovered.get_width()/2-rotatedIcon.get_width()/2,
                        self.autoButtonHovered.y+self.icon_y+self.autoIconHovered.get_height()/2-rotatedIcon.get_height()/2
                        ))
                    if self.autoIconDegree < 180:
                        self.autoIconDegree+=1
                    else:
                        self.autoIconDegree=0
                else:
                    surface.blit(self.autoIconHovered,(self.autoButtonHovered.tag,self.autoButtonHovered.y+self.icon_y))
                self.__button_hovered = 3
            else:
                if self.autoMode:
                    self.autoButtonHovered.draw(surface)
                    rotatedIcon = rotate_img(self.autoIconHovered,self.autoIconDegree)
                    surface.blit(rotatedIcon,(
                        self.autoButtonHovered.tag+self.autoIconHovered.get_width()/2-rotatedIcon.get_width()/2,
                        self.autoButtonHovered.y+self.icon_y+self.autoIconHovered.get_height()/2-rotatedIcon.get_height()/2
                        ))
                    if self.autoIconDegree < 180:
                        self.autoIconDegree += 1
                    else:
                        self.autoIconDegree = 0
                else:
                    self.autoButton.draw(surface)
                    surface.blit(self.autoIcon,(self.autoButton.tag,self.autoButton.y+self.icon_y))
            if self.hideButton.is_hover():
                self.__button_hovered = 1
            elif self.historyButton.is_hover():
                self.__button_hovered = 4
    def autoModeSwitch(self) -> None:
        if not self.autoMode:
            self.autoMode = True
        else:
            self.autoMode = False
            self.autoIconDegree = 0
