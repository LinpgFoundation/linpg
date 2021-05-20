# cython: language_level=3
from .ui import *

#视觉小说系统接口
class AbstractDialogSystem(AbstractGameSystem):
    def __init__(self):
        super().__init__()
        #加载对话的背景图片模块
        self._npc_manager = NpcImageManager()
        #黑色Void帘幕
        self._black_bg = get_single_color_surface("black")
        #选项栏
        self._option_box_surface = StaticImage(os.path.join(DIALOG_UI_PATH,"option.png"),0,0)
        #选项栏-选中
        try:
            self._option_box_selected_surface = StaticImage(os.path.join(DIALOG_UI_PATH,"option_selected.png"),0,0)
        except:
            throw_exception("warning","Cannot find 'option_selected.png' in 'UI' file, 'option.png' will be loaded instead.")
            self._option_box_selected_surface = self._option_box_surface.light_copy()
        #对话文件路径
        self._dialog_folder_path:str = "Data"
        #背景音乐路径
        self._background_music_folder_path:str = "Assets/music"
        #背景图片路径
        self._background_image_folder_path:str = "Assets/image/dialog_background"
        self._dynamic_background_folder_path:str = "Assets/movie"
        #背景图片
        self.__background_image_name = None
        self.__background_image_surface = self._black_bg.copy()
        #是否开启自动保存
        self.auto_save:bool = False
    #获取对话文件所在的具体路径
    def get_dialog_file_location(self, lang:str) -> str:
        return os.path.join(
            self._dialog_folder_path, self._chapter_type, "chapter{0}_dialogs_{1}.yaml".format(self._chapter_id, lang)
            ) if self._project_name is None else os.path.join(
                self._dialog_folder_path, self._chapter_type, self._project_name, "chapter{0}_dialogs_{1}.yaml".format(self._chapter_id, lang)
                )
    #获取对话文件的主语言
    def get_default_lang(self) -> str:
        return load_config(os.path.join(self._dialog_folder_path,self._chapter_type,"info.yaml"),"default_lang") if self._project_name is None\
            else load_config(os.path.join(self._dialog_folder_path,self._chapter_type,self._project_name,"info.yaml"),"default_lang")
    #初始化关键参数
    def _initialize(self, chapterType:str, chapterId:int, projectName:str, dialogId:Union[str,int]="head", dialog_options:dict={}) -> None:
        super()._initialize(chapterType,chapterId,projectName)
        #对白id
        self._dialog_id = dialogId
        #玩家做出的选项
        self.dialog_options = dialog_options
    #更新背景图片
    def _update_background_image(self, image_name:str) -> None:
        if self.__background_image_name != image_name:
            #更新背景的名称
            self.__background_image_name = image_name
            #更新背景的图片数据
            if self.__background_image_name is not None:
                #尝试加载图片式的背景
                img_path = os.path.join(self._background_image_folder_path,self.__background_image_name)
                if os.path.exists(img_path):
                    self.__background_image_surface = load_static_image(img_path,(0,0))
                #如果在背景图片的文件夹里找不到对应的图片，则查看是否是视频文件
                elif os.path.exists(os.path.join(self._dynamic_background_folder_path,self.__background_image_name)):
                    self.__background_image_surface = VedioSurface(
                        os.path.join(self._dynamic_background_folder_path,self.__background_image_name),display.get_width(),display.get_height()
                        )
                    self.__background_image_surface.start()
                else:
                    throw_exception("error","Cannot find a background image or video file called '{}'.".format(self.__background_image_name))
            else:
                self.__background_image_surface = self._black_bg.copy()
    #停止播放
    def stop(self) -> None:
        #如果背景是多线程的VedioSurface，则应该退出占用
        if isinstance(self.__background_image_surface,VedioSurface): self.__background_image_surface.stop()
        #设置停止播放
        super().stop()
    #将背景图片画到surface上
    def display_background_image(self, surface:ImageSurface) -> None:
        if isinstance(self.__background_image_surface, Rect):
            self.__background_image_surface.set_size(surface.get_width(), surface.get_height())
        self.__background_image_surface.draw(surface)
    #把基础内容画到surface上
    def draw(self, surface:ImageSurface) -> None:
        #检测章节是否初始化
        if self._chapter_id is None: raise throw_exception("error","The dialog has not been initialized!")
        #展示背景图片和npc立绘
        self.display_background_image(surface)
        self._npc_manager.draw(surface)

#npc立绘系统
class NpcImageManager:
    def __init__(self):
        #用于存放立绘的字典
        self.__npcImageDict:dict = {}
        #如果是开发模式，则在初始化时加载所有图片
        self.__npcLastRound:tuple = tuple()
        self.__npcLastRoundImgAlpha:int = 255
        self.__npcThisRound:tuple = tuple()
        self.__npcThisRoundImgAlpha:int = 0
        self.__darkness:int = 50
        self.__img_width:int = int(display.get_width()/2)
        try:
            self.__communication_surface_rect:object = Rect(int(self.__img_width*0.25),0,int(self.__img_width*0.5),int(self.__img_width*0.56))
            self.__communication = StaticImage(
                os.path.join(DIALOG_UI_PATH,"communication.png"),0,0,self.__communication_surface_rect.width,self.__communication_surface_rect.height
                )
            self.__communication_dark = self.__communication.copy()
            self.__communication_dark.add_darkness(self.__darkness)
        except:
            self.__communication = None
            self.__communication_dark = None
        self.__NPC_IMAGE_DATABASE:object = NpcImageDatabase()
        self.__move_x:int = 0
        self.dev_mode:bool = False
        self.npc_get_click = None
        self.image_folder_path:str = "Assets/image/npc"
    #确保角色存在
    def __ensure_the_existence_of(self, name:str) -> None:
        if name not in self.__npcImageDict: self.__loadNpc(os.path.join(self.image_folder_path,name))
    #加载角色
    def __loadNpc(self, path:str) -> None:
        name = os.path.basename(path)
        self.__npcImageDict[name] = {}
        self.__npcImageDict[name]["normal"] = StaticImage(path,0,0,self.__img_width,self.__img_width)
        #生成深色图片
        self.__npcImageDict[name]["dark"] = self.__npcImageDict[name]["normal"].copy()
        self.__npcImageDict[name]["dark"].add_darkness(self.__darkness)
    #画出角色
    def __displayNpc(self, name:str, x:Union[int,float], y:Union[int,float], alpha:int, surface:ImageSurface) -> None:
        if alpha > 0:
            nameTemp = name.replace("<c>","").replace("<d>","")
            self.__ensure_the_existence_of(nameTemp)
            #加载npc的基础立绘
            img = self.__npcImageDict[nameTemp]["dark"] if "<d>" in name else self.__npcImageDict[nameTemp]["normal"]
            img.set_size(self.__img_width,self.__img_width)
            img.set_alpha(alpha)
            img.set_pos(x,y)
            if "<c>" in name:
                img.set_crop_rect(self.__communication_surface_rect)
                img.draw(surface)
                if "<d>" in name:
                    self.__communication_dark.set_pos(x+self.__communication_surface_rect.x,y+self.__communication_surface_rect.y)
                    self.__communication_dark.draw(surface)
                else:
                    self.__communication.set_pos(x+self.__communication_surface_rect.x,y+self.__communication_surface_rect.y)
                    self.__communication.draw(surface)
            else:
                img.set_crop_rect(None)
                img.draw(surface)
            #如果是开发模式
            if self.dev_mode is True and is_hover(img,(x,y)):
                img.draw_outline(surface)
                self.npc_get_click = name
    def draw(self, surface:ImageSurface) -> None:
        window_x = surface.get_width()
        window_y = surface.get_height()
        npcImg_y = window_y-window_x/2
        #调整alpha值
        if self.__npcLastRoundImgAlpha > 0:
            self.__npcLastRoundImgAlpha -= 15
            x_moved_forNpcLastRound = self.__img_width/4-self.__img_width/4*self.__npcLastRoundImgAlpha/255
        else:
            x_moved_forNpcLastRound = 0
        if self.__npcThisRoundImgAlpha < 255:
            self.__npcThisRoundImgAlpha += 25
            x_moved_forNpcThisRound = self.__img_width/4*self.__npcThisRoundImgAlpha/255-self.__img_width/4
        else:
            x_moved_forNpcThisRound = 0
        #初始化被选择的角色名字
        self.npc_get_click = None
        #画上上一幕的立绘
        if len(self.__npcLastRound) == 0:
            #前后都无立绘，那干嘛要显示东西
            if len(self.__npcThisRound) == 0:
                pass
            #新增中间那个立绘
            elif len(self.__npcThisRound) == 1:
                self.__displayNpc(self.__npcThisRound[0],window_x/4+x_moved_forNpcThisRound,npcImg_y,self.__npcThisRoundImgAlpha,surface)
            #同时新增左右两边的立绘
            elif len(self.__npcThisRound) == 2:
                self.__displayNpc(self.__npcThisRound[0],x_moved_forNpcThisRound,npcImg_y,self.__npcThisRoundImgAlpha,surface)
                self.__displayNpc(self.__npcThisRound[1],window_x/2+x_moved_forNpcThisRound,npcImg_y,self.__npcThisRoundImgAlpha,surface)
        elif len(self.__npcLastRound) == 1:
            #很快不再需要显示原来中间的立绘
            if len(self.__npcThisRound) == 0:
                self.__displayNpc(self.__npcLastRound[0],window_x/4+x_moved_forNpcLastRound,npcImg_y,self.__npcLastRoundImgAlpha,surface)
            #更换中间的立绘
            elif len(self.__npcThisRound) == 1:
                self.__displayNpc(self.__npcLastRound[0],window_x/4,npcImg_y,self.__npcLastRoundImgAlpha,surface)
                self.__displayNpc(self.__npcThisRound[0],window_x/4,npcImg_y,self.__npcThisRoundImgAlpha,surface)
            elif len(self.__npcThisRound) == 2:
                #如果之前的中间变成了现在的左边，则立绘应该先向左移动
                if self.__NPC_IMAGE_DATABASE.ifSameKind(self.__npcLastRound[0],self.__npcThisRound[0]):
                    if self.__move_x+window_x/4 > 0:
                        self.__move_x -= int(window_x/40)
                    #显示左边立绘
                    self.__displayNpc(self.__npcLastRound[0],self.__move_x+window_x/4,npcImg_y,self.__npcLastRoundImgAlpha,surface)
                    self.__displayNpc(self.__npcThisRound[0],self.__move_x+window_x/4,npcImg_y,self.__npcThisRoundImgAlpha,surface)
                    #显示右边立绘
                    self.__displayNpc(self.__npcThisRound[1],window_x/2,npcImg_y,self.__npcThisRoundImgAlpha,surface)
                #如果之前的中间变成了现在的右边，则立绘应该先向右移动 - checked
                elif self.__NPC_IMAGE_DATABASE.ifSameKind(self.__npcLastRound[0],self.__npcThisRound[1]):
                    if self.__move_x+window_x/4 < window_x/2:
                        self.__move_x += int(window_x/40)
                    #显示左边立绘
                    self.__displayNpc(self.__npcThisRound[0],0,npcImg_y,self.__npcThisRoundImgAlpha,surface)
                    #显示右边立绘
                    self.__displayNpc(self.__npcLastRound[0],self.__move_x+window_x/4,npcImg_y,self.__npcLastRoundImgAlpha,surface)
                    self.__displayNpc(self.__npcThisRound[1],self.__move_x+window_x/4,npcImg_y,self.__npcThisRoundImgAlpha,surface)
                #之前的中间和现在两边无任何关系，先隐藏之前的立绘，然后显示现在的立绘 - checked
                else:
                    if self.__npcLastRoundImgAlpha > 0:
                        self.__npcThisRoundImgAlpha -= 25
                        self.__displayNpc(self.__npcLastRound[0],window_x/4,npcImg_y,self.__npcLastRoundImgAlpha,surface)
                    else:
                        self.__displayNpc(self.__npcThisRound[0],0,npcImg_y,self.__npcThisRoundImgAlpha,surface)
                        self.__displayNpc(self.__npcThisRound[1],window_x/2,npcImg_y,self.__npcThisRoundImgAlpha,surface)
        elif len(self.__npcLastRound)==2:
            #隐藏之前的左右两边立绘
            if len(self.__npcThisRound) == 0:
                self.__displayNpc(self.__npcLastRound[0],x_moved_forNpcLastRound,npcImg_y,self.__npcLastRoundImgAlpha,surface)
                self.__displayNpc(self.__npcLastRound[1],window_x/2+x_moved_forNpcLastRound,npcImg_y,self.__npcLastRoundImgAlpha,surface)
            elif len(self.__npcThisRound) == 1:
                #如果之前的左边变成了现在的中间，则立绘应该先向右边移动
                if self.__NPC_IMAGE_DATABASE.ifSameKind(self.__npcLastRound[0],self.__npcThisRound[0]):
                    if self.__move_x < window_x/4:
                        self.__move_x += int(window_x/40)
                    #左边立绘向右移动
                    self.__displayNpc(self.__npcLastRound[0],self.__move_x,npcImg_y,self.__npcLastRoundImgAlpha,surface)
                    self.__displayNpc(self.__npcThisRound[0],self.__move_x,npcImg_y,self.__npcThisRoundImgAlpha,surface)
                    #右边立绘消失
                    self.__displayNpc(self.__npcLastRound[1],window_x/2,npcImg_y,self.__npcLastRoundImgAlpha,surface)
                #如果之前的右边变成了现在的中间，则立绘应该先向左边移动
                elif self.__NPC_IMAGE_DATABASE.ifSameKind(self.__npcLastRound[1],self.__npcThisRound[0]):
                    if self.__move_x+window_x/2 > window_x/4:
                        self.__move_x -= int(window_x/40)
                    #左边立绘消失
                    self.__displayNpc(self.__npcLastRound[0],0,npcImg_y,self.__npcLastRoundImgAlpha,surface)
                    #右边立绘向左移动
                    self.__displayNpc(self.__npcLastRound[1],self.__move_x+window_x/2,npcImg_y,self.__npcLastRoundImgAlpha,surface)
                    self.__displayNpc(self.__npcThisRound[0],self.__move_x+window_x/2,npcImg_y,self.__npcThisRoundImgAlpha,surface)
                else:
                    if self.__npcLastRoundImgAlpha > 0:
                        self.__npcThisRoundImgAlpha -= 25
                        self.__displayNpc(self.__npcLastRound[0],0,npcImg_y,self.__npcLastRoundImgAlpha,surface)
                        self.__displayNpc(self.__npcLastRound[1],window_x/2,npcImg_y,self.__npcLastRoundImgAlpha,surface)
                    else:
                        self.__displayNpc(self.__npcThisRound[0],window_x/4,npcImg_y,self.__npcThisRoundImgAlpha,surface)
            elif len(self.__npcThisRound) == 2:
                if self.__NPC_IMAGE_DATABASE.ifSameKind(self.__npcLastRound[0],self.__npcThisRound[1]) and\
                    self.__NPC_IMAGE_DATABASE.ifSameKind(self.__npcLastRound[1],self.__npcThisRound[0]):
                    if self.__move_x+window_x/2 > 0:
                        self.__move_x -= int(window_x/30)
                    #左边到右边去
                    self.__displayNpc(self.__npcLastRound[0],-self.__move_x,npcImg_y,self.__npcLastRoundImgAlpha,surface)
                    self.__displayNpc(self.__npcThisRound[1],-self.__move_x,npcImg_y,self.__npcThisRoundImgAlpha,surface)
                    #右边到左边去
                    self.__displayNpc(self.__npcLastRound[1],window_x/2+self.__move_x,npcImg_y,self.__npcLastRoundImgAlpha,surface)
                    self.__displayNpc(self.__npcThisRound[0],window_x/2+self.__move_x,npcImg_y,self.__npcThisRoundImgAlpha,surface)
                else:
                    self.__displayNpc(self.__npcLastRound[0],0,npcImg_y,self.__npcLastRoundImgAlpha,surface)
                    self.__displayNpc(self.__npcLastRound[1],window_x/2,npcImg_y,self.__npcLastRoundImgAlpha,surface)
                    self.__displayNpc(self.__npcThisRound[0],0,npcImg_y,self.__npcThisRoundImgAlpha,surface)
                    self.__displayNpc(self.__npcThisRound[1],window_x/2,npcImg_y,self.__npcThisRoundImgAlpha,surface)
    #更新立绘
    def update(self, characterNameList:Union[list,tuple,None]) -> None:
        self.__npcLastRound = self.__npcThisRound
        self.__npcThisRound = tuple(characterNameList) if isinstance(characterNameList,(list,tuple)) else tuple()
        self.__npcLastRoundImgAlpha = 255
        self.__npcThisRoundImgAlpha = 5
        self.__move_x = 0

#对话框和对话框内容
class DialogContent(AbstractDialog):
    def __init__(self, fontSize:int):
        super().__init__(load_img(os.path.join(DIALOG_UI_PATH,"dialoguebox.png")),fontSize)
        try:
            self.__textPlayingSound = load_sound("Assets/sound/ui/dialog_words_playing.ogg")
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
        self.resetDialogueboxData()
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
    def render_font(self, txt:str, color:tuple) -> ImageSurface: return self.FONT.render(txt,get_antialias(),color)
    #如果音效还在播放则停止播放文字音效
    def stop_playing_text_sound(self) -> None:
        if is_any_sound_playing() and self.__textPlayingSound is not None: self.__textPlayingSound.stop()
    def draw(self, surface:ImageSurface) -> None:
        if not self.hidden:
            if not self.__fade_out_stage:
                self.__fadeIn(surface)
            else:
                self.__fadeOut(surface)
    #渐入
    def __fadeIn(self, surface:ImageSurface) -> None:
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
            self.dialoguebox_height += self.dialoguebox_max_height/10
            self.dialoguebox_y -= self.dialoguebox_max_height/20
        #如果已经放大好了
        else:
            self.__blit_txt(surface)
    #淡出
    def __fadeOut(self, surface:ImageSurface) -> None:
        #画出对话框图片
        if self.dialoguebox_y is not None:
            surface.blit(
                smoothly_resize_img(self.dialoguebox,(surface.get_width()*0.74,self.dialoguebox_height)),
                (surface.get_width()*0.13,self.dialoguebox_y)
                )
        if self.dialoguebox_height > 0:
            self.dialoguebox_height = max(self.dialoguebox_height-self.dialoguebox_max_height/10,0)
            self.dialoguebox_y += self.dialoguebox_max_height/20
        else:
            self.resetDialogueboxData()
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

#立绘配置信息数据库
class NpcImageDatabase:
    def __init__(self):
        try:
            self.__DATA = load_config("Data/npcImageDatabase.yaml")
        except FileNotFoundError:
            self.__DATA = {}
            save_config("Data/npcImageDatabase.yaml",self.__DATA)
            throw_exception("warning","Cannot find 'npcImageDatabase.yaml' in 'Data' file, a new one is created.")
    def get_kind(self, fileName:str) -> str:
        for key in self.__DATA:
            if fileName in self.__DATA[key]: return key
        return None
    def ifSameKind(self, fileName1:str, fileName2:str) -> bool:
        fileName1 = fileName1.replace("<c>","").replace("<d>","")
        fileName2 = fileName2.replace("<c>","").replace("<d>","")
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