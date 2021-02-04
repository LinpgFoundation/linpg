# cython: language_level=3
from ..scr_core.function import *
from ..scr_pyd.movie import cutscene,VedioFrame,VedioPlayer

#视觉小说系统接口
class DialogSystemInterface(SystemObject):
    def __init__(self) -> None:
        SystemObject.__init__(self)
        #加载对话的背景图片模块
        self.backgroundContent = DialogBackground()
        #加载npc立绘系统并初始化
        self.npc_img_dic = NpcImageSystem()
        #黑色Void帘幕
        self.black_bg = get_SingleColorSurface("black")
        #选项栏
        self.optionBox = loadImg("Assets/image/UI/option.png")
    #初始化关键参数
    def _initialize(self,chapterType:str,chapterId:int,part:str,collection_name:str,dialogId:str="head",dialog_options:dict={}) -> None:
        #类型
        self.chapterType = chapterType
        #章节id
        self.chapterId = chapterId
        #部分
        self.part = part
        #对白id
        self.dialogId = dialogId
        #玩家做出的选项
        self.dialog_options = dialog_options
        #合集名称-用于dlc和创意工坊
        self.collection_name = collection_name

#npc立绘系统
class NpcImageSystem:
    def __init__(self):
        self.imgDic = {}
        #如果是开发模式，则在初始化时加载所有图片
        self.npcLastRound = []
        self.npcLastRoundImgAlpha = 255
        self.npcThisRound = []
        self.npcThisRoundImgAlpha = 0
        self.communication = loadImg("Assets/image/UI/communication.png")
        self.__NPC_IMAGE_DATABASE = NpcImageDatabase()
        self.img_width = int(display.get_width()/2)
        self.move_x = 0
        self.dev_mode = False
        self.npc_get_click = None
    def devMode(self):
        for imgPath in glob.glob("Assets/image/npc/*"):
            self.__loadNpcImg(imgPath,self.img_width)
            self.dev_mode = True
    def __loadNpcImg(self,path,width):
        name = os.path.basename(path)
        self.imgDic[name] = {"normal":loadImg(path,(width,width))}
        #生成深色图片
        self.imgDic[name]["dark"] = self.imgDic[name]["normal"].copy()
        self.imgDic[name]["dark"].fill((50, 50, 50), special_flags=pygame.BLEND_RGB_SUB)
    def displayTheNpc(self,name,x,y,alpha,screen):
        if alpha <= 0:
            return False
        nameTemp = name.replace("&communication","").replace("&dark","")
        #加载npc的基础立绘
        if nameTemp not in self.imgDic:
            self.__loadNpcImg(os.path.join("Assets/image/npc",nameTemp),self.img_width)
        if "&communication" in name:
            if "communication" not in self.imgDic[nameTemp]:
                #生成通讯图片
                self.imgDic[nameTemp]["communication"] = pygame.Surface(
                    (int(self.img_width/1.9), int(self.img_width/1.8)),
                    flags=pygame.SRCALPHA)
                self.imgDic[nameTemp]["communication"].blit(self.imgDic[nameTemp]["normal"],(-int(self.img_width/4),0))
                self.imgDic[nameTemp]["communication"].blit(resizeImg(self.communication,(self.img_width/1.9,self.img_width/1.7)),(0,0))
                #生成深色的通讯图片
                self.imgDic[nameTemp]["communication_dark"] = self.imgDic[nameTemp]["communication"].copy()
                dark = pygame.Surface((int(self.img_width/1.9), int(self.img_width/1.8)), flags=pygame.SRCALPHA).convert_alpha()
                dark.fill((50,50,50))
                self.imgDic[nameTemp]["communication_dark"].blit(dark, (0, 0), special_flags=pygame.BLEND_RGB_SUB)
            x+=int(self.img_width/4)
            if "&dark" in name:
                img = self.imgDic[nameTemp]["communication_dark"].copy()
            else:
                img = self.imgDic[nameTemp]["communication"].copy()
        elif "&dark" in name:
            img = self.imgDic[nameTemp]["dark"].copy()
        else:
            img = self.imgDic[nameTemp]["normal"].copy()
        if alpha != 255:
            img.set_alpha(alpha)
        if not self.dev_mode:
            screen.blit(img,(x,y))
        else:
            self.npc_get_click = None
            if isHover(img,(x,y)):
                img.fill((60, 60, 60), special_flags=pygame.BLEND_RGB_ADD)
                self.npc_get_click = name
            screen.blit(img,(x,y))
    def display(self,screen):
        window_x = screen.get_width()
        window_y = screen.get_height()
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
                self.displayTheNpc(self.npcThisRound[0],window_x/4+x_moved_forNpcThisRound,npcImg_y,self.npcThisRoundImgAlpha,screen)
            #同时新增左右两边的立绘
            elif len(self.npcThisRound) == 2:
                self.displayTheNpc(self.npcThisRound[0],x_moved_forNpcThisRound,npcImg_y,self.npcThisRoundImgAlpha,screen)
                self.displayTheNpc(self.npcThisRound[1],window_x/2+x_moved_forNpcThisRound,npcImg_y,self.npcThisRoundImgAlpha,screen)
        elif len(self.npcLastRound) == 1:
            #很快不再需要显示原来中间的立绘
            if len(self.npcThisRound) == 0:
                self.displayTheNpc(self.npcLastRound[0],window_x/4+x_moved_forNpcLastRound,npcImg_y,self.npcLastRoundImgAlpha,screen)
            #更换中间的立绘
            elif len(self.npcThisRound) == 1:
                self.displayTheNpc(self.npcLastRound[0],window_x/4,npcImg_y,self.npcLastRoundImgAlpha,screen)
                self.displayTheNpc(self.npcThisRound[0],window_x/4,npcImg_y,self.npcThisRoundImgAlpha,screen)
            elif len(self.npcThisRound) == 2:
                #如果之前的中间变成了现在的左边，则立绘应该先向左移动
                if self.__NPC_IMAGE_DATABASE.ifSameKind(self.npcLastRound[0],self.npcThisRound[0]):
                    if self.move_x+window_x/4 > 0:
                        self.move_x -= window_x/40
                    #显示左边立绘
                    self.displayTheNpc(self.npcLastRound[0],self.move_x+window_x/4,npcImg_y,self.npcLastRoundImgAlpha,screen)
                    self.displayTheNpc(self.npcThisRound[0],self.move_x+window_x/4,npcImg_y,self.npcThisRoundImgAlpha,screen)
                    #显示右边立绘
                    self.displayTheNpc(self.npcThisRound[1],window_x/2,npcImg_y,self.npcThisRoundImgAlpha,screen)
                #如果之前的中间变成了现在的右边，则立绘应该先向右移动 - checked
                elif self.__NPC_IMAGE_DATABASE.ifSameKind(self.npcLastRound[0],self.npcThisRound[1]):
                    if self.move_x+window_x/4 < window_x/2:
                        self.move_x += window_x/40
                    #显示左边立绘
                    self.displayTheNpc(self.npcThisRound[0],0,npcImg_y,self.npcThisRoundImgAlpha,screen)
                    #显示右边立绘
                    self.displayTheNpc(self.npcLastRound[0],self.move_x+window_x/4,npcImg_y,self.npcLastRoundImgAlpha,screen)
                    self.displayTheNpc(self.npcThisRound[1],self.move_x+window_x/4,npcImg_y,self.npcThisRoundImgAlpha,screen)
                #之前的中间和现在两边无任何关系，先隐藏之前的立绘，然后显示现在的立绘 - checked
                else:
                    if self.npcLastRoundImgAlpha > 0:
                        self.npcThisRoundImgAlpha -= 25
                        self.displayTheNpc(self.npcLastRound[0],window_x/4,npcImg_y,self.npcLastRoundImgAlpha,screen)
                    else:
                        self.displayTheNpc(self.npcThisRound[0],0,npcImg_y,self.npcThisRoundImgAlpha,screen)
                        self.displayTheNpc(self.npcThisRound[1],window_x/2,npcImg_y,self.npcThisRoundImgAlpha,screen)
        elif len(self.npcLastRound)==2:
            #隐藏之前的左右两边立绘
            if len(self.npcThisRound) == 0:
                self.displayTheNpc(self.npcLastRound[0],x_moved_forNpcLastRound,npcImg_y,self.npcLastRoundImgAlpha,screen)
                self.displayTheNpc(self.npcLastRound[1],window_x/2+x_moved_forNpcLastRound,npcImg_y,self.npcLastRoundImgAlpha,screen)
            elif len(self.npcThisRound) == 1:
                #如果之前的左边变成了现在的中间，则立绘应该先向右边移动
                if self.__NPC_IMAGE_DATABASE.ifSameKind(self.npcLastRound[0],self.npcThisRound[0]):
                    if self.move_x < window_x/4:
                        self.move_x += window_x/40
                    #左边立绘向右移动
                    self.displayTheNpc(self.npcLastRound[0],self.move_x,npcImg_y,self.npcLastRoundImgAlpha,screen)
                    self.displayTheNpc(self.npcThisRound[0],self.move_x,npcImg_y,self.npcThisRoundImgAlpha,screen)
                    #右边立绘消失
                    self.displayTheNpc(self.npcLastRound[1],window_x/2,npcImg_y,self.npcLastRoundImgAlpha,screen)
                #如果之前的右边变成了现在的中间，则立绘应该先向左边移动
                elif self.__NPC_IMAGE_DATABASE.ifSameKind(self.npcLastRound[1],self.npcThisRound[0]):
                    if self.move_x+window_x/2 > window_x/4:
                        self.move_x -= window_x/40
                    #左边立绘消失
                    self.displayTheNpc(self.npcLastRound[0],0,npcImg_y,self.npcLastRoundImgAlpha,screen)
                    #右边立绘向左移动
                    self.displayTheNpc(self.npcLastRound[1],self.move_x+window_x/2,npcImg_y,self.npcLastRoundImgAlpha,screen)
                    self.displayTheNpc(self.npcThisRound[0],self.move_x+window_x/2,npcImg_y,self.npcThisRoundImgAlpha,screen)
                else:
                    if self.npcLastRoundImgAlpha > 0:
                        self.npcThisRoundImgAlpha -= 25
                        self.displayTheNpc(self.npcLastRound[0],0,npcImg_y,self.npcLastRoundImgAlpha,screen)
                        self.displayTheNpc(self.npcLastRound[1],window_x/2,npcImg_y,self.npcLastRoundImgAlpha,screen)
                    else:
                        self.displayTheNpc(self.npcThisRound[0],window_x/4,npcImg_y,self.npcThisRoundImgAlpha,screen)
            elif len(self.npcThisRound) == 2:
                if self.__NPC_IMAGE_DATABASE.ifSameKind(self.npcLastRound[0],self.npcThisRound[1]) and\
                    self.__NPC_IMAGE_DATABASE.ifSameKind(self.npcLastRound[1],self.npcThisRound[0]):
                    if self.move_x+window_x/2 > 0:
                        self.move_x -= window_x/30
                    #左边到右边去
                    self.displayTheNpc(self.npcLastRound[0],-self.move_x,npcImg_y,self.npcLastRoundImgAlpha,screen)
                    self.displayTheNpc(self.npcThisRound[1],-self.move_x,npcImg_y,self.npcThisRoundImgAlpha,screen)
                    #右边到左边去
                    self.displayTheNpc(self.npcLastRound[1],window_x/2+self.move_x,npcImg_y,self.npcLastRoundImgAlpha,screen)
                    self.displayTheNpc(self.npcThisRound[0],window_x/2+self.move_x,npcImg_y,self.npcThisRoundImgAlpha,screen)
                else:
                    self.displayTheNpc(self.npcLastRound[0],0,npcImg_y,self.npcLastRoundImgAlpha,screen)
                    self.displayTheNpc(self.npcLastRound[1],window_x/2,npcImg_y,self.npcLastRoundImgAlpha,screen)
                    self.displayTheNpc(self.npcThisRound[0],0,npcImg_y,self.npcThisRoundImgAlpha,screen)
                    self.displayTheNpc(self.npcThisRound[1],window_x/2,npcImg_y,self.npcThisRoundImgAlpha,screen)
    def process(self,thisRoundCharacterNameList):
        self.npcLastRound = self.npcThisRound
        if isinstance(thisRoundCharacterNameList,(list,tuple)):
            self.npcThisRound = thisRoundCharacterNameList
        else:
            self.npcThisRound = []
        self.npcLastRoundImgAlpha = 255
        self.npcThisRoundImgAlpha = 5
        self.move_x = 0

#对话框和对话框内容
class DialogContent(DialogInterface):
    def __init__(self,fontSize):
        DialogInterface.__init__(self,loadImg("Assets/image/UI/dialoguebox.png"),fontSize)
        self.textPlayingSound = pygame.mixer.Sound("Assets/sound/ui/dialog_words_playing.ogg")
        self.READINGSPEED = get_setting("ReadingSpeed")
        self.dialoguebox_y = None
        self.dialoguebox_height = 0
        self.dialoguebox_max_height = None
        #鼠标图标
        self.mouseImg = loadGif((loadImg("Assets/image/UI/mouse_none.png"),\
            loadImg("Assets/image/UI/mouse.png")),\
                (display.get_width()*0.82,display.get_height()*0.83),(self.FONTSIZE,self.FONTSIZE),50)
        self.isHidden = False
        self.readTime = 0
        self.totalLetters = 0
        self.autoMode = False
    def hideSwitch(self):
        self.isHidden = not self.isHidden
    def update(self,txt,narrator,forceNotResizeDialoguebox=False):
        self.totalLetters = 0
        self.readTime = 0
        for i in range(len(self.content)):
            self.totalLetters += len(self.content[i])
        if self.narrator != narrator and not forceNotResizeDialoguebox:
            self.resetDialogueboxData()
        super().update(txt,narrator)
        if pygame.mixer.get_busy():
            self.textPlayingSound.stop()
    def resetDialogueboxData(self):
        self.dialoguebox_height = 0
        self.dialoguebox_y = None
    def get_sound_volume(self):
        self.textPlayingSound.get_volume()
    def set_sound_volume(self,num):
        self.textPlayingSound.set_volume(num/100.0)
    def fontRender(self,txt,color):
        return self.FONT.render(txt,get_fontMode(),color)
    def display(self,screen):
        if not self.isHidden:
            #如果对话框图片的最高高度没有被设置，则根据屏幕大小设置一个
            if self.dialoguebox_max_height == None:
                self.dialoguebox_max_height = screen.get_height()/4
            #如果当前对话框图片的y坐标不存在（一般出现在对话系统例行初始化后），则根据屏幕大小设置一个
            if self.dialoguebox_y == None:
                self.dialoguebox_y = screen.get_height()*0.65+self.dialoguebox_max_height/2
            #画出对话框图片
            screen.blit(resizeImg(self.dialoguebox,(screen.get_width()*0.74,self.dialoguebox_height)),
            (screen.get_width()*0.13,self.dialoguebox_y))
            #如果对话框图片还在放大阶段
            if self.dialoguebox_height < self.dialoguebox_max_height:
                self.dialoguebox_height += self.dialoguebox_max_height/12
                self.dialoguebox_y -= self.dialoguebox_max_height/24
            #如果已经放大好了
            else:
                x = int(screen.get_width()*0.2)
                y = int(screen.get_height()*0.73)
                #写上当前讲话人的名字
                if self.narrator != None:
                    screen.blit(self.FONT.render(self.narrator,get_fontMode(),(255, 255, 255)),(x,self.dialoguebox_y+self.FONTSIZE))
                #画出鼠标gif
                self.mouseImg.display(screen)
                #对话框已播放的内容
                for i in range(self.displayedLine):
                    screen.blit(self.FONT.render(self.content[i],get_fontMode(),(255, 255, 255)),(x,y+self.FONTSIZE*1.5*i))
                #对话框正在播放的内容
                screen.blit(self.FONT.render(self.content[self.displayedLine][:self.textIndex],get_fontMode(),(255, 255, 255)),
                (x,y+self.FONTSIZE*1.5*self.displayedLine))
                #如果当前行的字符还没有完全播出
                if self.textIndex < len(self.content[self.displayedLine]):
                    if not pygame.mixer.get_busy():
                        self.textPlayingSound.play()
                    self.textIndex +=1
                #当前行的所有字都播出后，播出下一行
                elif self.displayedLine < len(self.content)-1:
                    if not pygame.mixer.get_busy():
                        self.textPlayingSound.play()
                    self.textIndex = 1
                    self.displayedLine += 1
                #当所有行都播出后
                else:
                    if pygame.mixer.get_busy():
                        self.textPlayingSound.stop()
                    if self.autoMode and self.readTime < self.totalLetters:
                        self.readTime += self.READINGSPEED
                    return True
        return False
    def forceUpdate(self):
        if self.autoMode and self.readTime >= self.totalLetters:
            return True
        else:
            return False

#背景音乐和图片管理
class DialogBackground:
    def __init__(self):
        self.backgroundImgName = None
        self.backgroundImgSurface = None
        self.nullSurface = get_SingleColorSurface("black")
        self.backgroundMusicName = None
    def get_sound_volume(self):
        return pygame.mixer.music.get_volume()
    def set_sound_volume(self,volume):
        pygame.mixer.music.set_volume(volume/100.0)
    def update(self,backgroundImgName,backgroundMusicName):
        #如果需要更新背景图片
        if self.backgroundImgName != backgroundImgName:
            self.backgroundImgName = backgroundImgName
            if self.backgroundImgName != None:
                #尝试背景加载图片
                if os.path.exists("Assets/image/dialog_background/{}".format(self.backgroundImgName)):
                    self.backgroundImgSurface = loadImage(os.path.join("Assets/image/dialog_background",self.backgroundImgName),
                    (0,0),display.get_width(),display.get_height())
                #如果在背景图片的文件夹里找不到对应的图片，则查看是否是视频文件
                elif os.path.exists("Assets/movie/"+self.backgroundImgName):
                    try:
                        self.backgroundImgSurface = VedioFrame("Assets/movie/"+self.backgroundImgName,display.get_width()
                        ,display.get_height(),True)
                    except BaseException:
                        raise Exception('LinpgEngine-Error: Cannot run movie module')
                else:
                    raise Exception('LinpgEngine-Error: Cannot find background image or video file.')
            else:
                self.backgroundImgSurface = None
        #如果需要更新背景音乐
        if self.backgroundMusicName != backgroundMusicName:
            self.backgroundMusicName = backgroundMusicName
            if self.backgroundMusicName != None:
                if os.path.exists("Assets/music/{}".format(self.backgroundMusicName)):
                    pygame.mixer.music.load("Assets/music/{}".format(self.backgroundMusicName))
                else:
                    raise Exception('LinpgEngine-Error: Cannot find background music file.')
                pygame.mixer.music.play(-1)
            else:
                pygame.mixer.music.unload()
    def display(self,screen):
        if self.backgroundImgName != None:
            self.backgroundImgSurface.display(screen)
        else:
            self.nullSurface.draw(screen)

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
        self.hideButton.setHoverImg(hideUI_img)
        showUI_img = loadImg("Assets/image/UI/dialog_show.png",(self.FONTSIZE,self.FONTSIZE))
        showUI_imgTemp = showUI_img.copy()
        showUI_imgTemp.fill((100,100,100), special_flags=pygame.BLEND_RGB_SUB)
        self.showButton = Button(showUI_imgTemp,window_x*0.05,window_y*0.05)
        self.showButton.setHoverImg(showUI_img)
        #历史回溯按钮
        history_img = loadImg("Assets/image/UI/dialog_history.png",(self.FONTSIZE,self.FONTSIZE))
        history_imgTemp = history_img.copy()
        history_imgTemp.fill((100,100,100), special_flags=pygame.BLEND_RGB_SUB)
        self.historyButton = Button(history_imgTemp,window_x*0.1,window_y*0.05)
        self.historyButton.setHoverImg(history_img)
    def display(self,screen,isHidden):
        if isHidden:
            self.showButton.display(screen)
            return "hide" if isHover(self.showButton) else ""
        elif isHidden == False:
            self.hideButton.display(screen)
            self.historyButton.display(screen)
            action = ""
            if isHover(self.skipButton):
                self.skipButtonHovered.draw(screen)
                action = "skip"
            else:
                self.skipButton.draw(screen)
            if isHover(self.autoButton):
                self.autoButtonHovered.draw(screen)
                if self.autoMode:
                    rotatedIcon = pygame.transform.rotate(self.autoIconHovered,self.autoIconDegree)
                    screen.blit(rotatedIcon,(
                        self.autoButtonHovered.description+self.autoIconHovered.get_width()/2-rotatedIcon.get_width()/2,
                        self.autoButtonHovered.y+self.icon_y+self.autoIconHovered.get_height()/2-rotatedIcon.get_height()/2
                        ))
                    if self.autoIconDegree < 180:
                        self.autoIconDegree+=1
                    else:
                        self.autoIconDegree=0
                else:
                    screen.blit(self.autoIconHovered,(self.autoButtonHovered.description,self.autoButtonHovered.y+self.icon_y))
                action = "auto"
            else:
                if self.autoMode:
                    self.autoButtonHovered.draw(screen)
                    rotatedIcon = pygame.transform.rotate(self.autoIconHovered,self.autoIconDegree)
                    screen.blit(rotatedIcon,(
                        self.autoButtonHovered.description+self.autoIconHovered.get_width()/2-rotatedIcon.get_width()/2,
                        self.autoButtonHovered.y+self.icon_y+self.autoIconHovered.get_height()/2-rotatedIcon.get_height()/2
                        ))
                    if self.autoIconDegree < 180:
                        self.autoIconDegree+=1
                    else:
                        self.autoIconDegree=0
                else:
                    self.autoButton.draw(screen)
                    screen.blit(self.autoIcon,(self.autoButton.description,self.autoButton.y+self.icon_y))
            if isHover(self.hideButton):
                action = "hide"
            elif isHover(self.historyButton):
                action = "history"
            return action
    def autoModeSwitch(self):
        if self.autoMode == False:
            self.autoMode = True
        else:
            self.autoMode = False
            self.autoIconDegree = 0

#立绘配置信息数据库
class NpcImageDatabase:
    def __init__(self) -> None: self.__DATA = loadConfig("Data/npcImageDatabase.yaml","Data")
    def get_kind(self,fileName:str) -> str:
        for key in self.__DATA:
            if fileName in self.__DATA[key]: return key
        return None
    def ifSameKind(self,fileName1:str,fileName2:str) -> bool:
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