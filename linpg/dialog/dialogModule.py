# cython: language_level=3
from .movie import *

#视觉小说系统接口
class AbstractDialogSystem(SystemWithBackgroundMusic):
    def __init__(self):
        SystemWithBackgroundMusic.__init__(self)
        #加载对话的背景图片模块
        self._npcManager = NpcImageManager()
        #黑色Void帘幕
        self._black_bg = get_SingleColorSurface("black")
        #选项栏
        self._optionBox = SrcalphaSurface("Assets/image/UI/option.png",0,0)
        #选项栏-选中
        try:
            self.optionBoxSelected = SrcalphaSurface("Assets/image/UI/option_selected.png",0,0)
        except:
            throwException("warning","Cannot find 'option_selected.png' in 'UI' file, 'option.png' will be loaded instead.")
            self.optionBoxSelected = self._optionBox.light_copy()
        #是否开启自动保存
        self.auto_save = False
        #背景图片
        self.__backgroundImageFilePath = "Assets/image/dialog_background"
        self.__dynamicBackgroundFilePath = "Assets/movie"
        self.__backgroundImageName = None
        self.__backgroundImageSurface = self._black_bg.copy()
    #初始化关键参数
    def _initialize(self, chapterType:str, chapterId:int, collection_name:str, dialogId:str="head", dialog_options:dict={}) -> None:
        #类型
        self.chapterType = chapterType
        #章节id
        self.chapterId = chapterId
        #对白id
        self.dialogId = dialogId
        #玩家做出的选项
        self.dialog_options = dialog_options
        #合集名称-用于dlc和创意工坊
        self.collection_name = collection_name
    #更新背景图片
    def _update_background_image(self, image_name:str) -> None:
        if self.__backgroundImageName != image_name:
            #更新背景的名称
            self.__backgroundImageName = image_name
            #更新背景的图片数据
            if self.__backgroundImageName is not None:
                #尝试加载图片式的背景
                img_path = os.path.join(self.__backgroundImageFilePath,self.__backgroundImageName)
                if os.path.exists(img_path):
                    self.__backgroundImageSurface = loadImage(img_path,(0,0))
                #如果在背景图片的文件夹里找不到对应的图片，则查看是否是视频文件
                elif os.path.exists(os.path.join(self.__dynamicBackgroundFilePath,self.__backgroundImageName)):
                    try:
                        self.__backgroundImageSurface = VedioFrame(os.path.join(self.__dynamicBackgroundFilePath,self.__backgroundImageName),display.get_width(),display.get_height())
                    except BaseException:
                        throwException("error","Cannot run movie module.")
                else:
                    throwException("error","Cannot find a background image or video file called '{}'.".format(self.__backgroundImageName))
            else:
                self.__backgroundImageSurface = self._black_bg.copy()
    #将背景图片画到surface上
    def display_background_image(self, surface:pygame.Surface) -> None:
        if isinstance(self.__backgroundImageSurface,ImageSurface):
            self.__backgroundImageSurface.set_size(surface.get_width(),surface.get_height())
        self.__backgroundImageSurface.draw(surface)
    #把基础内容画到surface上
    def draw(self, surface:pygame.Surface) -> None:
        #更新事件
        self._update_event()
        #检测章节是否初始化
        if self.chapterId is None: raise throwException("error","The dialog has not been initialized!")
        #展示背景图片和npc立绘
        self.display_background_image(surface)
        self._npcManager.draw(surface)

#npc立绘系统
class NpcImageManager:
    def __init__(self):
        #用于存放立绘的字典
        self.npcImageDict = {}
        #如果是开发模式，则在初始化时加载所有图片
        self.npcLastRound = []
        self.npcLastRoundImgAlpha = 255
        self.npcThisRound = []
        self.npcThisRoundImgAlpha = 0
        try:
            self.communication = loadImg("Assets/image/UI/communication.png")
        except:
            self.communication = None
        self.__NPC_IMAGE_DATABASE = NpcImageDatabase()
        self.img_width = int(display.get_width()/2)
        self.move_x = 0
        self.dev_mode = False
        self.npcGetClick = None
    def devMode(self) -> None:
        for imgPath in glob("Assets/image/npc/*"):
            self.__loadNpc(imgPath)
            self.dev_mode = True
    #确保角色存在
    def __ensure_the_existence_of(self, name:str) -> None:
        if name not in self.npcImageDict: self.__loadNpc(os.path.join("Assets/image/npc",name))
    #加载角色
    def __loadNpc(self, path:str) -> None:
        name = os.path.basename(path)
        self.npcImageDict[name] = {}
        self.npcImageDict[name]["normal"] = SrcalphaSurface(path,0,0,self.img_width,self.img_width)
        #生成深色图片
        self.npcImageDict[name]["dark"] = self.npcImageDict[name]["normal"].copy()
        self.npcImageDict[name]["dark"].addDarkness(50)
    #画出角色
    def __displayNpc(self, name:str, x:Union[int,float], y:Union[int,float], alpha:int, surface:pygame.Surface) -> None:
        if alpha > 0:
            nameTemp = name.replace("&communication","").replace("&dark","")
            self.__ensure_the_existence_of(nameTemp)
            #加载npc的基础立绘
            img = self.npcImageDict[nameTemp]["dark"] if "&dark" in name else self.npcImageDict[nameTemp]["normal"]
            img.set_size(self.img_width,self.img_width)
            img.set_alpha(alpha)
            """
            if "&communication" in name:
                if "communication" not in self.npcImageDict[nameTemp]:
                    #生成通讯图片
                    self.npcImageDict[nameTemp]["communication"] = getSurface((int(self.img_width/1.9), int(self.img_width/1.8)),pygame.SRCALPHA)
                    self.npcImageDict[nameTemp]["communication"].blit(self.npcImageDict[nameTemp]["normal"],(-int(self.img_width/4),0))
                    self.npcImageDict[nameTemp]["communication"].blit(resizeImg(self.communication,(self.img_width/1.9,self.img_width/1.7)),(0,0))
                    #生成深色的通讯图片
                    self.npcImageDict[nameTemp]["communication_dark"] = self.npcImageDict[nameTemp]["communication"].copy()
                    dark = pygame.Surface((int(self.img_width/1.9), int(self.img_width/1.8)), flags=pygame.SRCALPHA).convert_alpha()
                    dark.fill((50,50,50))
                    self.npcImageDict[nameTemp]["communication_dark"].blit(dark, (0, 0), special_flags=pygame.BLEND_RGB_SUB)
                    x+=int(self.img_width/4)
            """
            img.set_pos(x,y)
            img.draw(surface)
            #如果是开发模式
            if self.dev_mode:
                self.npcGetClick = None
                if is_hover(img,(x,y)):
                    img.draw_outline(surface)
                    self.npcGetClick = name
    def draw(self, surface:pygame.Surface) -> None:
        window_x = surface.get_width()
        window_y = surface.get_height()
        npcImg_y = window_y-window_x/2
        #调整alpha值
        if self.npcLastRoundImgAlpha > 0:
            self.npcLastRoundImgAlpha -= 15
            x_moved_forNpcLastRound = self.img_width/4-self.img_width/4*self.npcLastRoundImgAlpha/255
        else:
            x_moved_forNpcLastRound = 0
        if self.npcThisRoundImgAlpha < 255:
            self.npcThisRoundImgAlpha += 25
            x_moved_forNpcThisRound = self.img_width/4*self.npcThisRoundImgAlpha/255-self.img_width/4
        else:
            x_moved_forNpcThisRound = 0
        #画上上一幕的立绘
        if len(self.npcLastRound) == 0:
            #前后都无立绘，那干嘛要显示东西
            if len(self.npcThisRound) == 0:
                pass
            #新增中间那个立绘
            elif len(self.npcThisRound) == 1:
                self.__displayNpc(self.npcThisRound[0],window_x/4+x_moved_forNpcThisRound,npcImg_y,self.npcThisRoundImgAlpha,surface)
            #同时新增左右两边的立绘
            elif len(self.npcThisRound) == 2:
                self.__displayNpc(self.npcThisRound[0],x_moved_forNpcThisRound,npcImg_y,self.npcThisRoundImgAlpha,surface)
                self.__displayNpc(self.npcThisRound[1],window_x/2+x_moved_forNpcThisRound,npcImg_y,self.npcThisRoundImgAlpha,surface)
        elif len(self.npcLastRound) == 1:
            #很快不再需要显示原来中间的立绘
            if len(self.npcThisRound) == 0:
                self.__displayNpc(self.npcLastRound[0],window_x/4+x_moved_forNpcLastRound,npcImg_y,self.npcLastRoundImgAlpha,surface)
            #更换中间的立绘
            elif len(self.npcThisRound) == 1:
                self.__displayNpc(self.npcLastRound[0],window_x/4,npcImg_y,self.npcLastRoundImgAlpha,surface)
                self.__displayNpc(self.npcThisRound[0],window_x/4,npcImg_y,self.npcThisRoundImgAlpha,surface)
            elif len(self.npcThisRound) == 2:
                #如果之前的中间变成了现在的左边，则立绘应该先向左移动
                if self.__NPC_IMAGE_DATABASE.ifSameKind(self.npcLastRound[0],self.npcThisRound[0]):
                    if self.move_x+window_x/4 > 0:
                        self.move_x -= window_x/40
                    #显示左边立绘
                    self.__displayNpc(self.npcLastRound[0],self.move_x+window_x/4,npcImg_y,self.npcLastRoundImgAlpha,surface)
                    self.__displayNpc(self.npcThisRound[0],self.move_x+window_x/4,npcImg_y,self.npcThisRoundImgAlpha,surface)
                    #显示右边立绘
                    self.__displayNpc(self.npcThisRound[1],window_x/2,npcImg_y,self.npcThisRoundImgAlpha,surface)
                #如果之前的中间变成了现在的右边，则立绘应该先向右移动 - checked
                elif self.__NPC_IMAGE_DATABASE.ifSameKind(self.npcLastRound[0],self.npcThisRound[1]):
                    if self.move_x+window_x/4 < window_x/2:
                        self.move_x += window_x/40
                    #显示左边立绘
                    self.__displayNpc(self.npcThisRound[0],0,npcImg_y,self.npcThisRoundImgAlpha,surface)
                    #显示右边立绘
                    self.__displayNpc(self.npcLastRound[0],self.move_x+window_x/4,npcImg_y,self.npcLastRoundImgAlpha,surface)
                    self.__displayNpc(self.npcThisRound[1],self.move_x+window_x/4,npcImg_y,self.npcThisRoundImgAlpha,surface)
                #之前的中间和现在两边无任何关系，先隐藏之前的立绘，然后显示现在的立绘 - checked
                else:
                    if self.npcLastRoundImgAlpha > 0:
                        self.npcThisRoundImgAlpha -= 25
                        self.__displayNpc(self.npcLastRound[0],window_x/4,npcImg_y,self.npcLastRoundImgAlpha,surface)
                    else:
                        self.__displayNpc(self.npcThisRound[0],0,npcImg_y,self.npcThisRoundImgAlpha,surface)
                        self.__displayNpc(self.npcThisRound[1],window_x/2,npcImg_y,self.npcThisRoundImgAlpha,surface)
        elif len(self.npcLastRound)==2:
            #隐藏之前的左右两边立绘
            if len(self.npcThisRound) == 0:
                self.__displayNpc(self.npcLastRound[0],x_moved_forNpcLastRound,npcImg_y,self.npcLastRoundImgAlpha,surface)
                self.__displayNpc(self.npcLastRound[1],window_x/2+x_moved_forNpcLastRound,npcImg_y,self.npcLastRoundImgAlpha,surface)
            elif len(self.npcThisRound) == 1:
                #如果之前的左边变成了现在的中间，则立绘应该先向右边移动
                if self.__NPC_IMAGE_DATABASE.ifSameKind(self.npcLastRound[0],self.npcThisRound[0]):
                    if self.move_x < window_x/4:
                        self.move_x += window_x/40
                    #左边立绘向右移动
                    self.__displayNpc(self.npcLastRound[0],self.move_x,npcImg_y,self.npcLastRoundImgAlpha,surface)
                    self.__displayNpc(self.npcThisRound[0],self.move_x,npcImg_y,self.npcThisRoundImgAlpha,surface)
                    #右边立绘消失
                    self.__displayNpc(self.npcLastRound[1],window_x/2,npcImg_y,self.npcLastRoundImgAlpha,surface)
                #如果之前的右边变成了现在的中间，则立绘应该先向左边移动
                elif self.__NPC_IMAGE_DATABASE.ifSameKind(self.npcLastRound[1],self.npcThisRound[0]):
                    if self.move_x+window_x/2 > window_x/4:
                        self.move_x -= window_x/40
                    #左边立绘消失
                    self.__displayNpc(self.npcLastRound[0],0,npcImg_y,self.npcLastRoundImgAlpha,surface)
                    #右边立绘向左移动
                    self.__displayNpc(self.npcLastRound[1],self.move_x+window_x/2,npcImg_y,self.npcLastRoundImgAlpha,surface)
                    self.__displayNpc(self.npcThisRound[0],self.move_x+window_x/2,npcImg_y,self.npcThisRoundImgAlpha,surface)
                else:
                    if self.npcLastRoundImgAlpha > 0:
                        self.npcThisRoundImgAlpha -= 25
                        self.__displayNpc(self.npcLastRound[0],0,npcImg_y,self.npcLastRoundImgAlpha,surface)
                        self.__displayNpc(self.npcLastRound[1],window_x/2,npcImg_y,self.npcLastRoundImgAlpha,surface)
                    else:
                        self.__displayNpc(self.npcThisRound[0],window_x/4,npcImg_y,self.npcThisRoundImgAlpha,surface)
            elif len(self.npcThisRound) == 2:
                if self.__NPC_IMAGE_DATABASE.ifSameKind(self.npcLastRound[0],self.npcThisRound[1]) and\
                    self.__NPC_IMAGE_DATABASE.ifSameKind(self.npcLastRound[1],self.npcThisRound[0]):
                    if self.move_x+window_x/2 > 0:
                        self.move_x -= window_x/30
                    #左边到右边去
                    self.__displayNpc(self.npcLastRound[0],-self.move_x,npcImg_y,self.npcLastRoundImgAlpha,surface)
                    self.__displayNpc(self.npcThisRound[1],-self.move_x,npcImg_y,self.npcThisRoundImgAlpha,surface)
                    #右边到左边去
                    self.__displayNpc(self.npcLastRound[1],window_x/2+self.move_x,npcImg_y,self.npcLastRoundImgAlpha,surface)
                    self.__displayNpc(self.npcThisRound[0],window_x/2+self.move_x,npcImg_y,self.npcThisRoundImgAlpha,surface)
                else:
                    self.__displayNpc(self.npcLastRound[0],0,npcImg_y,self.npcLastRoundImgAlpha,surface)
                    self.__displayNpc(self.npcLastRound[1],window_x/2,npcImg_y,self.npcLastRoundImgAlpha,surface)
                    self.__displayNpc(self.npcThisRound[0],0,npcImg_y,self.npcThisRoundImgAlpha,surface)
                    self.__displayNpc(self.npcThisRound[1],window_x/2,npcImg_y,self.npcThisRoundImgAlpha,surface)
    #更新立绘
    def update(self, characterNameList:Union[list,tuple,None]) -> None:
        self.npcLastRound = self.npcThisRound
        self.npcThisRound = characterNameList if isinstance(characterNameList,(list,tuple)) else []
        self.npcLastRoundImgAlpha = 255
        self.npcThisRoundImgAlpha = 5
        self.move_x = 0

#对话框和对话框内容
class DialogContent(AbstractDialog):
    def __init__(self, fontSize:int):
        AbstractDialog.__init__(self,loadImg("Assets/image/UI/dialoguebox.png"),fontSize)
        try:
            self.__textPlayingSound = pygame.mixer.Sound("Assets/sound/ui/dialog_words_playing.ogg")
        except FileNotFoundError:
            self.__textPlayingSound = None
            throwException("warning","Cannot find 'dialog_words_playing.ogg' in 'Assets/sound/ui'!")
            print("As a result, the text playing sound will be disabled.")
        self.READINGSPEED = get_setting("ReadingSpeed")
        self.dialoguebox_max_height = None
        #鼠标图标
        self.mouseImg = loadGif(
            (loadImg("Assets/image/UI/mouse_none.png"),loadImg("Assets/image/UI/mouse.png")),
            (display.get_width()*0.82,display.get_height()*0.83),(self.FONTSIZE,self.FONTSIZE),50)
        self.isHidden = False
        self.readTime = 0
        self.totalLetters = 0
        self.autoMode = False
        self.resetDialogueboxData()
    def hideSwitch(self) -> None: self.isHidden = not self.isHidden
    def update(self, txt:list, narrator:str, forceNotResizeDialoguebox:bool=False) -> None:
        self.totalLetters = 0
        self.readTime = 0
        for i in range(len(self.content)):
            self.totalLetters += len(self.content[i])
        if self.narrator != narrator and not forceNotResizeDialoguebox:
            self.__fade_out_stage = True
        super().update(txt,narrator)
        self.stop_playing_text_sound()
    def resetDialogueboxData(self) -> None:
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
    def fontRender(self, txt:str, color:tuple) -> pygame.Surface: return self.FONT.render(txt,get_fontMode(),color)
    def __render_font(self, txt:str, color:tuple) ->pygame.Surface:
        return self.FONT.render(txt,get_fontMode(),color) 
        """
        font_surface = self.fontRender(txt,color)
        if self.__txt_alpha != 255: font_surface.set_alpha(self.__txt_alpha)
        return font_surface
        """
    #如果音效还在播放则停止播放文字音效
    def stop_playing_text_sound(self) -> None:
        if pygame.mixer.get_busy() and self.__textPlayingSound is not None: self.__textPlayingSound.stop()
    def draw(self, surface:pygame.Surface) -> None:
        if not self.isHidden:
            if not self.__fade_out_stage:
                self.__fadeIn(surface)
            else:
                self.__fadeOut(surface)
    #渐入
    def __fadeIn(self, surface:pygame.Surface) -> None:
        #如果对话框图片的最高高度没有被设置，则根据屏幕大小设置一个
        if self.dialoguebox_max_height is None:
            self.dialoguebox_max_height = surface.get_height()/4
        #如果当前对话框图片的y坐标不存在（一般出现在对话系统例行初始化后），则根据屏幕大小设置一个
        if self.dialoguebox_y is None:
            self.dialoguebox_y = surface.get_height()*0.65+self.dialoguebox_max_height/2
        #画出对话框图片
        surface.blit(resizeImg(self.dialoguebox,(surface.get_width()*0.74,self.dialoguebox_height)),
        (surface.get_width()*0.13,self.dialoguebox_y))
        #如果对话框图片还在放大阶段
        if self.dialoguebox_height < self.dialoguebox_max_height:
            self.dialoguebox_height += self.dialoguebox_max_height/10
            self.dialoguebox_y -= self.dialoguebox_max_height/20
        #如果已经放大好了
        else:
            self.__blit_txt(surface)
    #淡出
    def __fadeOut(self, surface:pygame.Surface) -> None:
        #画出对话框图片
        surface.blit(resizeImg(self.dialoguebox,(surface.get_width()*0.74,self.dialoguebox_height)),
        (surface.get_width()*0.13,self.dialoguebox_y))
        """
        if self.__txt_alpha > 0:
            self.__txt_alpha -= 17
            self.__blit_txt(surface)
        else:
        """
        if self.dialoguebox_height > 0:
            self.dialoguebox_height -= self.dialoguebox_max_height/10
            self.dialoguebox_y += self.dialoguebox_max_height/20
        else:
            self.resetDialogueboxData()
    #将文字画到屏幕上
    def __blit_txt(self, surface:pygame.Surface) -> None:
        x:int = int(surface.get_width()*0.2)
        y:int = int(surface.get_height()*0.73)
        #写上当前讲话人的名字
        if self.narrator is not None:
            surface.blit(self.__render_font(self.narrator,(255, 255, 255)),(x,self.dialoguebox_y+self.FONTSIZE))
        #画出鼠标gif
        self.mouseImg.draw(surface)
        #对话框已播放的内容
        for i in range(self.displayedLine):
            surface.blit(self.__render_font(self.content[i],(255, 255, 255)),(x,y+self.FONTSIZE*1.5*i))
        #对话框正在播放的内容
        surface.blit(
            self.__render_font(self.content[self.displayedLine][:self.textIndex],(255, 255, 255)),
            (x,y+self.FONTSIZE*1.5*self.displayedLine)
            )
        #如果当前行的字符还没有完全播出
        if self.textIndex < len(self.content[self.displayedLine]):
            if not pygame.mixer.get_busy() and self.__textPlayingSound is not None:
                self.__textPlayingSound.play()
            self.textIndex +=1
        #当前行的所有字都播出后，播出下一行
        elif self.displayedLine < len(self.content)-1:
            if not pygame.mixer.get_busy() and self.__textPlayingSound is not None:
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
        #从设置中读取信息
        window_x,window_y = display.get_size()
        self.FONTSIZE = int(window_x*0.0175)
        self.FONT = createFont(self.FONTSIZE)
        #从语言文件中读取按钮文字
        dialog_txt = get_lang("Dialog")
        #生成跳过按钮
        tempButtonIcon = loadImg("Assets/image/UI/dialog_skip.png",(self.FONTSIZE,self.FONTSIZE))
        tempButtonTxt = self.FONT.render(dialog_txt["skip"],get_fontMode(),(255, 255, 255))
        temp_w = tempButtonTxt.get_width()+self.FONTSIZE*1.5
        self.choiceTxt = dialog_txt["choice"]
        self.skipButton = pygame.Surface((temp_w,tempButtonTxt.get_height()),flags=pygame.SRCALPHA).convert_alpha()
        self.skipButtonHovered = pygame.Surface((temp_w,tempButtonTxt.get_height()),flags=pygame.SRCALPHA).convert_alpha()
        self.icon_y = (tempButtonTxt.get_height()-tempButtonIcon.get_height())/2
        self.skipButtonHovered.blit(tempButtonIcon,(tempButtonTxt.get_width()+self.FONTSIZE*0.5,self.icon_y))
        self.skipButtonHovered.blit(tempButtonTxt,(0,0))
        tempButtonTxt = self.FONT.render(dialog_txt["skip"],get_fontMode(),(105, 105, 105))
        tempButtonIcon.fill((100,100,100), special_flags=pygame.BLEND_RGB_SUB)
        self.skipButton.blit(tempButtonIcon,(tempButtonTxt.get_width()+self.FONTSIZE*0.5,self.icon_y))
        self.skipButton.blit(tempButtonTxt,(0,0))
        self.skipButton = ImageSurface(self.skipButton,window_x*0.9,window_y*0.05)
        self.skipButtonHovered = ImageSurface(self.skipButtonHovered,window_x*0.9,window_y*0.05)
        #生成自动播放按钮
        self.autoIconHovered = loadImg("Assets/image/UI/dialog_auto.png",(self.FONTSIZE,self.FONTSIZE))
        self.autoIcon = self.autoIconHovered.copy()
        self.autoIcon.fill((100,100,100), special_flags=pygame.BLEND_RGB_SUB)
        self.autoIconDegree = 0
        self.autoIconDegreeChange = (2**0.5-1)*self.FONTSIZE/45
        self.autoMode = False
        tempButtonTxt = self.FONT.render(dialog_txt["auto"],get_fontMode(),(105, 105, 105))
        temp_w = tempButtonTxt.get_width()+self.FONTSIZE*1.5
        self.autoButton = pygame.Surface((temp_w,tempButtonTxt.get_height()),flags=pygame.SRCALPHA).convert_alpha()
        self.autoButtonHovered = pygame.Surface((temp_w,tempButtonTxt.get_height()),flags=pygame.SRCALPHA).convert_alpha()
        self.autoButton.blit(tempButtonTxt,(0,0))
        self.autoButtonHovered.blit(self.FONT.render(dialog_txt["auto"],get_fontMode(),(255, 255, 255)),(0,0))
        self.autoButton = ImageSurface(self.autoButton,window_x*0.8,window_y*0.05)
        self.autoButton.description = int(self.autoButton.x+self.autoButton.img.get_width()-self.FONTSIZE)
        self.autoButtonHovered = ImageSurface(self.autoButtonHovered,window_x*0.8,window_y*0.05)
        self.autoButtonHovered.description = int(self.autoButtonHovered.x+self.autoButtonHovered.img.get_width()-self.FONTSIZE)
        #隐藏按钮
        hideUI_img = loadImg("Assets/image/UI/dialog_hide.png",(self.FONTSIZE,self.FONTSIZE))
        hideUI_imgTemp = hideUI_img.copy()
        hideUI_imgTemp.fill((100,100,100), special_flags=pygame.BLEND_RGB_SUB)
        self.hideButton = Button(hideUI_imgTemp,window_x*0.05,window_y*0.05)
        self.hideButton.set_hover_img(hideUI_img)
        showUI_img = loadImg("Assets/image/UI/dialog_show.png",(self.FONTSIZE,self.FONTSIZE))
        showUI_imgTemp = showUI_img.copy()
        showUI_imgTemp.fill((100,100,100), special_flags=pygame.BLEND_RGB_SUB)
        self.showButton = Button(showUI_imgTemp,window_x*0.05,window_y*0.05)
        self.showButton.set_hover_img(showUI_img)
        #历史回溯按钮
        history_img = loadImg("Assets/image/UI/dialog_history.png",(self.FONTSIZE,self.FONTSIZE))
        history_imgTemp = history_img.copy()
        history_imgTemp.fill((100,100,100), special_flags=pygame.BLEND_RGB_SUB)
        self.historyButton = Button(history_imgTemp,window_x*0.1,window_y*0.05)
        self.historyButton.set_hover_img(history_img)
    def draw(self, surface:pygame.Surface, isHidden:bool) -> str:
        if isHidden:
            self.showButton.draw(surface)
            return "hide" if is_hover(self.showButton) else ""
        else:
            self.hideButton.draw(surface)
            self.historyButton.draw(surface)
            action = ""
            if is_hover(self.skipButton):
                self.skipButtonHovered.draw(surface)
                action = "skip"
            else:
                self.skipButton.draw(surface)
            if is_hover(self.autoButton):
                self.autoButtonHovered.draw(surface)
                if self.autoMode:
                    rotatedIcon = pygame.transform.rotate(self.autoIconHovered,self.autoIconDegree)
                    surface.blit(rotatedIcon,(
                        self.autoButtonHovered.description+self.autoIconHovered.get_width()/2-rotatedIcon.get_width()/2,
                        self.autoButtonHovered.y+self.icon_y+self.autoIconHovered.get_height()/2-rotatedIcon.get_height()/2
                        ))
                    if self.autoIconDegree < 180:
                        self.autoIconDegree+=1
                    else:
                        self.autoIconDegree=0
                else:
                    surface.blit(self.autoIconHovered,(self.autoButtonHovered.description,self.autoButtonHovered.y+self.icon_y))
                action = "auto"
            else:
                if self.autoMode:
                    self.autoButtonHovered.draw(surface)
                    rotatedIcon = pygame.transform.rotate(self.autoIconHovered,self.autoIconDegree)
                    surface.blit(rotatedIcon,(
                        self.autoButtonHovered.description+self.autoIconHovered.get_width()/2-rotatedIcon.get_width()/2,
                        self.autoButtonHovered.y+self.icon_y+self.autoIconHovered.get_height()/2-rotatedIcon.get_height()/2
                        ))
                    if self.autoIconDegree < 180:
                        self.autoIconDegree+=1
                    else:
                        self.autoIconDegree=0
                else:
                    self.autoButton.draw(surface)
                    surface.blit(self.autoIcon,(self.autoButton.description,self.autoButton.y+self.icon_y))
            if is_hover(self.hideButton):
                action = "hide"
            elif is_hover(self.historyButton):
                action = "history"
            return action
    def autoModeSwitch(self) -> None:
        if not self.autoMode:
            self.autoMode = True
        else:
            self.autoMode = False
            self.autoIconDegree = 0

#立绘配置信息数据库
class NpcImageDatabase:
    def __init__(self):
        try:
            self.__DATA = loadConfig("Data/npcImageDatabase.yaml")
        except FileNotFoundError:
            self.__DATA = {}
            saveConfig("Data/npcImageDatabase.yaml",self.__DATA)
            throwException("warning","Cannot find 'npcImageDatabase.yaml' in 'Data' file, a new one is created.")
    def get_kind(self, fileName:str) -> str:
        for key in self.__DATA:
            if fileName in self.__DATA[key]: return key
        return None
    def ifSameKind(self, fileName1:str, fileName2:str) -> bool:
        fileName1 = fileName1.replace("&communication","").replace("&dark","")
        fileName2 = fileName2.replace("&communication","").replace("&dark","")
        for key in self.__DATA:
            if fileName1 in self.__DATA[key]:
                if fileName2 in self.__DATA[key]:
                    return True
                else:
                    return False
            elif fileName2 in self.__DATA[key]:
                if fileName1 in self.__DATA[key]:
                    return True
                else:
                    return False
        return False