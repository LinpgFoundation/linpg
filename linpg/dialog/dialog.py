# cython: language_level=3
from .dialogModule import *

#视觉小说系统模块
class DialogSystem(AbstractDialogSystem):
    def __init__(self) -> None:
        super().__init__()
        #UI按钮
        self.ButtonsMananger = DialogButtons()
        #加载对话框系统
        self.dialogTxtSystem = DialogContent(int(display.get_width()*0.015))
        #更新音效
        self.__update_sound_volume()
        #是否要显示历史对白页面
        self.showHistory = False
        self.historySurface = None
        self.historySurface_local_y = 0
        #展示历史界面-返回按钮
        buttonTemp = loadImg("Assets/image/UI/back.png",(display.get_width()*0.03,display.get_height()*0.04))
        self.history_back = Button(addDarkness(buttonTemp,100),display.get_width()*0.04,display.get_height()*0.04)
        self.history_back.set_hover_img(buttonTemp)
        #暂停菜单
        self.pause_menu = PauseMenu()
    #保存数据-子类必须实现
    def save_process(self): throwException("error","You have to overwrite save_process() before continue!")
    #读取章节
    def load(self, save_path:str) -> None:
        saveData = loadConfig(save_path)
        """章节信息"""
        self._initialize(
            saveData["chapterType"],
            saveData["chapterId"],
            saveData["collection_name"],
            saveData["id"],
            saveData["dialog_options"]
            )
        self.part = saveData["type"]
        self.__process_data()
    #新建章节
    def new(self, chapterType:str, chapterId:int, part:str, collection_name:str=None) -> None:
        """章节信息"""
        self._initialize(chapterType,chapterId,collection_name)
        self.part = part
        self.__process_data()
    #加载章节信息
    def __process_data(self) -> None:
        #读取目标对话文件的数据
        dialogData = loadConfig("Data/{0}/chapter{1}_dialogs_{2}.yaml".format(self.chapterType,self.chapterId,get_setting("Language"))
        ) if self.collection_name is None else loadConfig("Data/{0}/{1}/chapter{2}_dialogs_{3}.yaml"
        .format(self.chapterType,self.collection_name,self.chapterId,get_setting("Language")))
        default_lang_of_dialog = loadConfig("Data/{0}/info.yaml".format(self.chapterType),"default_lang") if self.collection_name is None\
            else loadConfig("Data/{0}/{1}/info.yaml".format(self.chapterType,self.collection_name),"default_lang")
        #如果该dialog文件是另一个语言dialog文件的子类
        if default_lang_of_dialog != get_setting("Language"):
            if self.collection_name is None:
                self.dialogContent = loadConfig("Data/{0}/chapter{1}_dialogs_{2}.yaml"
                .format(self.chapterType,self.chapterId,default_lang_of_dialog),"dialogs")[self.part]
            else:
                self.dialogContent = loadConfig("Data/{0}/{1}/chapter{2}_dialogs_{3}.yaml"
                .format(self.chapterType,self.collection_name,self.chapterId,default_lang_of_dialog),"dialogs")[self.part]
            for key,currentDialog in dialogData["dialogs"][self.part].items():
                if key in self.dialogContent:
                    for key2,dataNeedReplace in currentDialog.items():
                        self.dialogContent[key][key2] = dataNeedReplace
                else:
                    self.dialogContent[key] = currentDialog
        #如果该dialog文件是主语言
        else:
            self.dialogContent = dialogData["dialogs"][self.part]
            if len(self.dialogContent) == 0: throwException("error","The dialog file has no content! You need to at least set up a head.")
        #将数据载入刚初始化的模块中
        self.__update_scene(self.dialogId)
        self.dialogTxtSystem.resetDialogueboxData()
    #更新场景
    def __update_scene(self, theNextDialogId:Union[str,int]) -> None:
        #如果dialog Id 不存在
        if theNextDialogId in self.dialogContent:
            #更新背景音乐
            if self.dialogContent[theNextDialogId]["background_music"] is not None:
                self.set_bgm("Assets/music/{}".format(self.dialogContent[theNextDialogId]["background_music"]))
            else:
                self.set_bgm(None)
            #更新背景和立绘
            self._npcManager.update(self.dialogContent[theNextDialogId]["characters_img"])
            self._update_background_image(self.dialogContent[theNextDialogId]["background_img"])
            #更新对话框文字
            self.dialogTxtSystem.update(self.dialogContent[theNextDialogId]["content"],self.dialogContent[theNextDialogId]["narrator"])
            #切换dialogId
            self.dialogId = theNextDialogId
            #自动保存
            if self.auto_save: self.save_process()
        else:
            throwException("error","The dialog id {} does not exist!".format(theNextDialogId))
    #更新音量
    def __update_sound_volume(self) -> None:
        self.set_bgm_volume(get_setting("Sound","background_music")/100)
        self.dialogTxtSystem.set_sound_volume(get_setting("Sound","sound_effects"))
    #淡入
    def fadeIn(self, surface:pygame.Surface) -> None:
        for i in range(255,0,-5):
            self.display_background_image(surface)
            self._black_bg.set_alpha(i)
            self._black_bg.draw(surface)
            pygame.display.flip()
        #重设black_bg的alpha值以便下一次使用
        self._black_bg.set_alpha(255)
    #淡出
    def fadeOut(self, surface:pygame.Surface) -> None:
        pygame.mixer.music.fadeout(1000)
        pygame.mixer.fadeout(1000)
        for i in range(0,255,5):
            self._black_bg.set_alpha(i)
            self._black_bg.draw(surface)
            pygame.display.flip()
    def draw(self, surface:pygame.Surface) -> None:
        super().draw(surface)
        #显示对话框和对应文字
        self.dialogTxtSystem.draw(surface)
        #背景音乐
        self.play_bgm(-1)
        #按钮
        buttonEvent = self.ButtonsMananger.draw(surface,self.dialogTxtSystem.isHidden)
        #按键判定
        leftClick = False
        for event in self.events:
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.JOYBUTTONDOWN:
                if event.button == 1 or controller.joystick.get_button(0) == 1:
                    if buttonEvent == "hide" and not self.showHistory:
                        self.dialogTxtSystem.hideSwitch()
                    #如果接来下没有文档了或者玩家按到了跳过按钮
                    elif buttonEvent == "skip" and not self.showHistory:
                        #淡出
                        self.fadeOut(surface)
                        self._isPlaying = False
                    elif buttonEvent == "auto" and not self.showHistory:
                        self.ButtonsMananger.autoModeSwitch()
                        self.dialogTxtSystem.autoMode = self.ButtonsMananger.autoMode
                    elif buttonEvent == "history" and not self.showHistory:
                        self.showHistory = True
                    elif self.history_back.is_hover() and self.showHistory:
                        self.showHistory = False
                        self.historySurface = None
                    #如果所有行都没有播出，则播出所有行
                    elif not self.dialogTxtSystem.is_all_played():
                        self.dialogTxtSystem.play_all()
                    else:
                        leftClick = True
                elif event.button == 4 and self.historySurface_local_y<0:
                    self.historySurface = None
                    self.historySurface_local_y += display.get_height()*0.1
                elif event.button == 5:
                    self.historySurface = None
                    self.historySurface_local_y -= display.get_height()*0.1
                #返回上一个对话场景（在被允许的情况下）
                elif event.button == 3 or controller.joystick.get_button(1) == 1:
                    if self.dialogContent[self.dialogId]["last_dialog_id"] is not None:
                        self.__update_scene(self.dialogContent[self.dialogId]["last_dialog_id"])
                    else:
                        pass
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                process_saved_text = ImageSurface(
                    self.dialogTxtSystem.FONT.render(get_lang("Global","process_has_been_saved"),get_fontMode(),(255, 255, 255)),0,0
                    )
                process_saved_text.set_alpha(0)
                while True:
                    self._update_event()
                    result = self.pause_menu.draw(surface,self.events)
                    if result == "Break":
                        setting.isDisplaying = False
                        break
                    elif result == "Save":
                        self.save_process()
                        process_saved_text.set_alpha(255)
                    elif result == "Setting":
                        setting.isDisplaying = True
                    elif result == "BackToMainMenu":
                        setting.isDisplaying = False
                        self.fadeOut(surface)
                        self._isPlaying = False
                        break
                    #如果播放玩菜单后发现有东西需要更新
                    if setting.draw(surface,self.events):
                        self.__update_sound_volume()
                    process_saved_text.drawOnTheCenterOf(surface)
                    process_saved_text.fade_out(5)
                    display.flip()
                del process_saved_text
                self.pause_menu.screenshot = None
        #显示选项
        if self.dialogTxtSystem.is_all_played() and self.dialogContent[self.dialogId]["next_dialog_id"] is not None and self.dialogContent[self.dialogId]["next_dialog_id"]["type"] == "option":
            optionBox_y_base = (display.get_height()*3/4-(len(self.dialogContent[self.dialogId]["next_dialog_id"]["target"]))*2*display.get_width()*0.03)/4
            optionBox_height = int(display.get_width()*0.05)
            nextDialogId = None
            i=0
            for i in range(len(self.dialogContent[self.dialogId]["next_dialog_id"]["target"])):
                option_txt = self.dialogTxtSystem.fontRender(self.dialogContent[self.dialogId]["next_dialog_id"]["target"][i]["txt"],findColorRGBA("white"))
                optionBox_width = int(option_txt.get_width()+display.get_width()*0.05) 
                optionBox_x = (display.get_width()-optionBox_width)/2
                optionBox_y = (i+1)*2*display.get_width()*0.03+optionBox_y_base
                mouse_x,mouse_y = pygame.mouse.get_pos()
                if 0<mouse_x-optionBox_x<optionBox_width and 0<mouse_y-optionBox_y<optionBox_height:
                    self.optionBoxSelected.set_size(optionBox_width,optionBox_height)
                    self.optionBoxSelected.set_pos(optionBox_x,optionBox_y)
                    self.optionBoxSelected.draw(surface)
                    displayInCenter(option_txt,self.optionBoxSelected,self.optionBoxSelected.x,self.optionBoxSelected.y,surface)
                    #保存选取的选项
                    if leftClick and not self.showHistory: nextDialogId = self.dialogContent[self.dialogId]["next_dialog_id"]["target"][i]["id"]
                else:
                    self._optionBox.set_size(optionBox_width,optionBox_height)
                    self._optionBox.set_pos(optionBox_x,optionBox_y)
                    self._optionBox.draw(surface)
                    displayInCenter(option_txt,self._optionBox,self._optionBox.x,self._optionBox.y,surface)
            if nextDialogId is not None:
                self.dialog_options[self.dialogId] = {"id":i,"target":nextDialogId}
                #更新场景
                self.__update_scene(nextDialogId)
                leftClick = False
        #展示历史
        if self.showHistory:
            if self.historySurface is None:
                self.historySurface = pygame.Surface(display.get_size(),flags=pygame.SRCALPHA).convert_alpha()
                pygame.draw.rect(self.historySurface,(0,0,0),((0,0),display.get_size()))
                self.historySurface.set_alpha(150)
                dialogIdTemp = "head"
                local_y = self.historySurface_local_y
                while dialogIdTemp is not None:
                    if self.dialogContent[dialogIdTemp]["narrator"] is not None:
                        narratorTemp = self.dialogTxtSystem.fontRender(self.dialogContent[dialogIdTemp]["narrator"]+': ["',(255, 255, 255))
                        self.historySurface.blit(narratorTemp,(display.get_width()*0.15-narratorTemp.get_width(),display.get_height()*0.1+local_y))
                    for i in range(len(self.dialogContent[dialogIdTemp]["content"])):
                        txt = self.dialogContent[dialogIdTemp]["content"][i]
                        txt += '"]' if i == len(self.dialogContent[dialogIdTemp]["content"])-1 and self.dialogContent[dialogIdTemp]["narrator"] is not None else ""
                        self.historySurface.blit(self.dialogTxtSystem.fontRender(txt,(255, 255, 255)),(display.get_width()*0.15,display.get_height()*0.1+local_y))
                        local_y+=self.dialogTxtSystem.FONTSIZE*1.5
                    if dialogIdTemp != self.dialogId:
                        if self.dialogContent[dialogIdTemp]["next_dialog_id"]["type"] == "default" or self.dialogContent[dialogIdTemp]["next_dialog_id"]["type"] == "changeScene":
                            dialogIdTemp = self.dialogContent[dialogIdTemp]["next_dialog_id"]["target"]
                        elif self.dialogContent[dialogIdTemp]["next_dialog_id"]["type"] == "option":
                            narratorTemp = self.dialogTxtSystem.fontRender(self.ButtonsMananger.choiceTxt+" - ",(0,191,255))
                            self.historySurface.blit(narratorTemp,(display.get_width()*0.15-narratorTemp.get_width(),display.get_height()*0.1+local_y))
                            self.historySurface.blit(self.dialogTxtSystem.fontRender(str(self.dialog_options[dialogIdTemp]["target"]),(0,191,255)),(display.get_width()*0.15,display.get_height()*0.1+local_y))
                            local_y+=self.dialogTxtSystem.FONTSIZE*1.5
                            dialogIdTemp = self.dialog_options[dialogIdTemp]["target"]
                        else:
                            dialogIdTemp = None
                    else:
                        dialogIdTemp = None
            surface.blit(self.historySurface,(0,0))
            self.history_back.draw(surface)
            self.history_back.is_hover()
        elif self.dialogTxtSystem.needUpdate() or leftClick:
            if self.dialogContent[self.dialogId]["next_dialog_id"] is None or self.dialogContent[self.dialogId]["next_dialog_id"]["target"] is None:
                self.fadeOut(surface)
                self._isPlaying = False
            elif self.dialogContent[self.dialogId]["next_dialog_id"]["type"] == "default":
                self.__update_scene(self.dialogContent[self.dialogId]["next_dialog_id"]["target"])
            #如果是需要播放过程动画
            elif self.dialogContent[self.dialogId]["next_dialog_id"]["type"] == "cutscene":
                self.fadeOut(surface)
                cutscene(surface,"Assets\movie\{}".format(self.dialogContent[self.dialogId]["next_dialog_id"]["target"]))
                self._isPlaying = False
            #如果是切换场景
            elif self.dialogContent[self.dialogId]["next_dialog_id"]["type"] == "changeScene":
                self.fadeOut(surface)
                pygame.time.wait(2000)
                #更新场景
                self.__update_scene(self.dialogContent[self.dialogId]["next_dialog_id"]["target"])
                self.dialogTxtSystem.resetDialogueboxData()
                self.fadeIn(surface)
        #刷新控制器，并展示自定义鼠标（如果存在）
        controller.draw(surface)

#对话制作器
class DialogEditor(AbstractDialogSystem):
    def __init__(self, chapterType:str, chapterId:int, part:str=None, collection_name:str=None):
        super().__init__()
        self._initialize(chapterType,chapterId,collection_name)
        #设定初始化
        self.fileLocation = "Data/{0}/chapter{1}_dialogs_{2}.yaml".format(self.chapterType,self.chapterId,get_setting("Language")) if self.chapterType == "main_chapter"\
            else "Data/{0}/{1}/chapter{2}_dialogs_{3}.yaml".format(self.chapterType,self.collection_name,self.chapterId,get_setting("Language"))
        #文字
        self.FONTSIZE = display.get_width()*0.015
        self.FONT = createFont(self.FONTSIZE)
        #对话框
        self.dialoguebox = loadImage("Assets/image/UI/dialoguebox.png",(display.get_width()*0.13,display.get_height()*0.65),display.get_width()*0.74,display.get_height()/4)
        self.narrator = SingleLineInputBox(display.get_width()*0.2,self.dialoguebox.y+self.FONTSIZE,self.FONTSIZE,"white")
        self.content = MultipleLinesInputBox(display.get_width()*0.2,display.get_height()*0.73,self.FONTSIZE,"white")
        #将npc立绘系统设置为开发者模式
        self._npcManager.devMode()
        #从配置文件中加载数据
        self.__loadDialogData(part)
        #背景选择界面
        widthTmp = int(display.get_width()*0.2)
        self.UIContainerRight = loadDynamicImage("Assets/image/UI/container.png",(display.get_width()*0.8+widthTmp,0),(display.get_width()*0.8,0),(widthTmp/10,0),widthTmp,display.get_height())
        self.UIContainerRightButton = loadImage("Assets/image/UI/container_button.png",(-display.get_width()*0.03,display.get_height()*0.4),int(display.get_width()*0.04),int(display.get_height()*0.2))
        self.UIContainerRight.rotate(90)
        self.UIContainerRightButton.rotate(90)
        self.background_deselect = loadImg("Assets/image/UI/deselect.png")
        self.UIContainerRight_kind = "background"
        #UI按钮
        CONFIG = get_lang("DialogCreator")
        button_width = display.get_width()*0.05
        button_y = display.get_height()*0.03
        self.button_select_background = ButtonWithFadeInOut("Assets/image/UI/menu.png",CONFIG["background"],"black",100,button_width/3,button_width/3,button_width/3)
        self.button_select_npc = ButtonWithFadeInOut("Assets/image/UI/menu.png",CONFIG["npc"],"black",100,button_width/2+self.button_select_background.get_width(),button_width/3,button_width/3)
        self.npc_local_y = 0
        self.buttonsUI = {
            "save": ButtonWithDes("Assets/image/UI/save.png",button_width*7.25,button_y,button_width,button_width,get_lang("Global","save")),
            "reload": ButtonWithDes("Assets/image/UI/reload.png",button_width*6,button_y,button_width,button_width,CONFIG["reload"]),
            "add": ButtonWithDes("Assets/image/UI/add.png",button_width*4.75,button_y,button_width,button_width,CONFIG["add"]),
            "next": ButtonWithDes("Assets/image/UI/dialog_skip.png",button_width*4.75,button_y,button_width,button_width,CONFIG["next"]),
            "previous": ButtonWithDes("Assets/image/UI/previous.png",button_width*3.5,button_y,button_width,button_width,CONFIG["previous"]),
            "delete": ButtonWithDes("Assets/image/UI/delete.png",button_width*2.25,button_y,button_width,button_width,CONFIG["delete"]),
            "back": ButtonWithDes("Assets/image/UI/back.png",button_width,button_y,button_width,button_width,CONFIG["back"])
        }
        self.please_enter_content = CONFIG["please_enter_content"]
        self.please_enter_name = CONFIG["please_enter_name"]
        self.removeNpcButton = fontRender(CONFIG["removeNpc"],"black",self.FONTSIZE)
        surfaceTmp = pygame.Surface((self.removeNpcButton.get_width()*1.2,self.FONTSIZE*1.2),flags=pygame.SRCALPHA).convert()
        pygame.draw.rect(surfaceTmp,(255,255,255),(0,0, surfaceTmp.get_width(),surfaceTmp.get_height()))
        surfaceTmp.blit(self.removeNpcButton,(self.removeNpcButton.get_width()*0.1,0))
        self.removeNpcButton = surfaceTmp
        #加载背景图片
        self.all_background_image = {}
        for imgPath in glob("Assets/image/dialog_background/*"):
            self.all_background_image[os.path.basename(imgPath)] = loadImg(imgPath)
        self.background_image_local_y = display.get_height()*0.1
        self.smart_add_mode = False
    @property
    def part(self) -> str: return self.parts[self.partId]
    #读取章节信息
    def __loadDialogData(self, part:str) -> None:
        self.dialogData = loadConfig(self.fileLocation,"dialogs")
        self.parts = list(self.dialogData.keys())
        #如果dialogs字典是空的
        if len(self.parts) <= 0:
            default_part_name = "example_dialog"
            self.partId = 0
            self.parts.append(default_part_name)
            self.dialogData[default_part_name] = {}
            self.dialogData[default_part_name]["head"] = self.deafult_dialog_format
            self.isDefault = True
            self.dialogData_default = None
        else:
            self.partId = 0 if part is None else self.parts.index(part)
            default_lang_of_dialog = loadConfig("Data/{0}/info.yaml".format(self.chapterType),"default_lang") if self.collection_name is None\
            else loadConfig("Data/{0}/{1}/info.yaml".format(self.chapterType,self.collection_name),"default_lang")
            #如果不是默认主语言
            if default_lang_of_dialog != get_setting("Language"):
                self.isDefault = False
                #读取原始数据
                self.dialogData_default = loadConfig("Data/{0}/chapter{1}_dialogs_{2}.yaml"
                .format(self.chapterType,self.chapterId,default_lang_of_dialog),"dialogs") if self.chapterType == "main_chapter"\
                    else loadConfig("Data/{0}/{1}/chapter{2}_dialogs_{3}.yaml"
                    .format(self.chapterType,self.collection_name,self.chapterId,default_lang_of_dialog),"dialogs")
                #填入未被填入的数据
                for part in self.dialogData_default:
                    for key,DIALOG_DATA_TEMP in self.dialogData_default[part].items():
                        if key in self.dialogData[part]:
                            for key2,dataNeedReplace in DIALOG_DATA_TEMP.items():
                                if key2 not in self.dialogData[part][key]:
                                    self.dialogData[part][key][key2] = deepcopy(dataNeedReplace)
                        else:
                            self.dialogData[part][key] = deepcopy(DIALOG_DATA_TEMP)
            else:
                self.isDefault = True
                self.dialogData_default = None
        #更新场景
        self.__update_scene(self.dialogId)
    #保存数据
    def __save(self) -> None:
        self.dialogData[self.part][self.dialogId]["narrator"] = self.narrator.get_text()
        self.dialogData[self.part][self.dialogId]["content"] = self.content.get_text()
        if not self.isDefault:
            #移除掉相似的内容
            for part in self.dialogData_default:
                for dialogId,defaultDialogData in self.dialogData_default[part].items():
                    if dialogId in self.dialogData[part]:
                        for dataType in defaultDialogData:
                            if self.dialogData[part][dialogId][dataType] == defaultDialogData[dataType]:
                                del self.dialogData[part][dialogId][dataType]
                        if len(self.dialogData[part][dialogId]) == 0: del self.dialogData[part][dialogId]
        #读取原始数据
        original_data:dict = loadConfig(self.fileLocation)
        original_data["dialogs"] = self.dialogData
        #保存数据
        saveConfig(self.fileLocation,original_data)
        #重新加载self.dialogData以确保准确性
        self.__loadDialogData(self.part)
    #更新场景
    def __update_scene(self, theNextDialogId:Union[str,int]) -> None:
        if theNextDialogId in self.dialogData[self.part]:
            self.dialogId = theNextDialogId
            #更新立绘和背景
            self._npcManager.update(self.dialogData[self.part][self.dialogId]["characters_img"])
            self._update_background_image(self.dialogData[self.part][self.dialogId]["background_img"])
            #更新对话框
            self.narrator.set_text(self.dialogData[self.part][self.dialogId]["narrator"])
            self.content.set_text(self.dialogData[self.part][self.dialogId]["content"])
        elif self.smart_add_mode:
            self.__add_dialog(theNextDialogId)
        else:
            throwException("error","Cannot find the dialog with id '{}' in the data dictionary.".format(theNextDialogId))
    #添加新的对话
    def __add_dialog(self, dialogId:Union[str,int]) -> None:
        self.dialogData[self.part][dialogId] = {
            "background_img": self.dialogData[self.part][self.dialogId]["background_img"],
            "background_music": self.dialogData[self.part][self.dialogId]["background_music"],
            "characters_img": [],
            "content": [self.please_enter_content],
            "last_dialog_id": self.dialogId,
            "narrator": self.please_enter_name,
            "next_dialog_id": None
        }
        self.dialogData[self.part][self.dialogId]["next_dialog_id"] = {"target":dialogId,"type":"default"}
        #检测smart_add_mode是否启动
        if self.smart_add_mode:
            lastId = self.__get_last_id()
            if lastId is not None:
                self.dialogData[self.part][dialogId]["narrator"] = self.dialogData[self.part][lastId]["narrator"]
                self.dialogData[self.part][dialogId]["characters_img"] = deepcopy(self.dialogData[self.part][lastId]["characters_img"])
        #检测是否自动保存
        if not self.auto_save:
            self.__update_scene(dialogId)
        else:
            self.__save()
    #获取上一个对话的ID
    def __get_last_id(self) -> Union[str,int]:
        if "last_dialog_id" in self.dialogData[self.part][self.dialogId] and self.dialogData[self.part][self.dialogId]["last_dialog_id"] is not None:
            return self.dialogData[self.part][self.dialogId]["last_dialog_id"]
        elif self.dialogId == "head":
            return None
        else:
            for key,dialogData in self.dialogData[self.part].items():
                if dialogData["next_dialog_id"] is not None:
                    if dialogData["next_dialog_id"]["type"] == "default" and dialogData["next_dialog_id"]["target"] == self.dialogId:
                        return key
                    elif dialogData["next_dialog_id"]["type"] == "changeScene" and dialogData["next_dialog_id"]["target"] == self.dialogId:
                        return key
                    elif dialogData["next_dialog_id"]["type"] == "option":
                        for optionChoice in dialogData["next_dialog_id"]["target"]:
                            if optionChoice["id"] == self.dialogId:
                                return key
            return None
    #获取下一个对话的ID
    def __get_next_id(self, surface:pygame.Surface) -> Union[str,int]:
        if "next_dialog_id" in self.dialogData[self.part][self.dialogId]:
            theNext:dict = self.dialogData[self.part][self.dialogId]["next_dialog_id"]
            if theNext is not None:
                if theNext["type"] == "default" or theNext["type"] == "changeScene":
                    return theNext["target"]
                elif theNext["type"] == "option":
                    optionBox_y_base = (surface.get_height()*3/4-(len(theNext["target"]))*2*surface.get_width()*0.03)/4
                    option_button_height = surface.get_width()*0.05
                    screenshot = surface.copy()
                    #等待玩家选择一个选项
                    while True:
                        surface.blit(screenshot,(0,0))
                        self._update_event()
                        leftClick = False
                        for event in self.events:
                            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.JOYBUTTONDOWN:
                                leftClick = True
                                break
                        for i in range(len(theNext["target"])):
                            button = theNext["target"][i]
                            option_txt = self.FONT.render(button["txt"],get_fontMode(),findColorRGBA("white"))
                            option_button_width = int(option_txt.get_width()+surface.get_width()*0.05)
                            option_button_x = int((surface.get_width()-option_button_width)/2)
                            option_button_y = int((i+1)*2*surface.get_width()*0.03+optionBox_y_base)
                            mouse_x,mouse_y = pygame.mouse.get_pos()
                            if 0<mouse_x-option_button_x<option_button_width and 0<mouse_y-option_button_y<option_button_height:
                                self.optionBoxSelected.set_size(option_button_width,option_button_height)
                                self.optionBoxSelected.set_pos(option_button_x,option_button_y)
                                self.optionBoxSelected.draw(surface)
                                displayInCenter(option_txt,self.optionBoxSelected,self.optionBoxSelected.x,self.optionBoxSelected.y,surface)
                                if leftClick: return button["id"]
                            else:
                                self._optionBox.set_size(option_button_width,option_button_height)
                                self._optionBox.set_pos(option_button_x,option_button_y)
                                self._optionBox.draw(surface)
                                displayInCenter(option_txt,self._optionBox,self._optionBox.x,self._optionBox.y,surface)
                        display.flip()
        return None
    def draw(self, surface:pygame.Surface) -> None:
        super().draw(surface)
        #画上对话框
        self.dialoguebox.draw(surface)
        if self._npcManager.npcGetClick is not None: surface.blit(self.removeNpcButton,pygame.mouse.get_pos())
        self.narrator.draw(surface,self.events)
        if self.narrator.needSave: self.dialogData[self.part][self.dialogId]["narrator"] = self.narrator.get_text()
        self.content.draw(surface,self.events)
        if self.content.needSave:
            self.dialogData[self.part][self.dialogId]["content"] = self.content.get_text()
        #初始化数值
        buttonHovered = None
        theNextDialogId = self.dialogData[self.part][self.dialogId]["next_dialog_id"]
        #展示按钮
        for button in self.buttonsUI:
            if button == "next" and theNextDialogId is None or button == "next" and len(theNextDialogId)<2:
                if self.buttonsUI["add"].is_hover():
                    buttonHovered = "add"
                self.buttonsUI["add"].draw(surface)
            elif button != "add":
                if self.buttonsUI[button].is_hover():
                    buttonHovered = button
                self.buttonsUI[button].draw(surface)
        leftClick = False
        for event in self.events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if isHover(self.UIContainerRightButton,local_x=self.UIContainerRight.x):
                        self.UIContainerRight.switch()
                        self.UIContainerRightButton.flip(True,False)
                    #退出
                    elif buttonHovered == "back":
                        self._isPlaying = False
                    elif buttonHovered == "previous":
                        lastId = self.__get_last_id()
                        if lastId is not None:
                            self.__update_scene(lastId)
                        else:
                            print("no last_dialog_id")
                    elif buttonHovered == "delete":
                        lastId = self.__get_last_id()
                        nextId = self.__get_next_id(surface)
                        if lastId is not None:
                            if self.dialogData[self.part][lastId]["next_dialog_id"]["type"] == "default" or self.dialogData[self.part][lastId]["next_dialog_id"]["type"] == "changeScene":
                                self.dialogData[self.part][lastId]["next_dialog_id"]["target"] = nextId
                            elif self.dialogData[self.part][lastId]["next_dialog_id"]["type"] == "option":
                                for optionChoice in self.dialogData[self.part][lastId]["next_dialog_id"]["target"]:
                                    if optionChoice["id"] == self.dialogId:
                                        optionChoice["id"] = nextId
                                        break
                            else:
                                #如果当前next_dialog_id的类型不支持的话，报错
                                throwException("error","Cannot recognize next_dialog_id type: {}, please fix it".format(self.dialogData[self.part][lastId]["next_dialog_id"]["type"]))
                            #修改下一个对白配置文件中的"last_dialog_id"的参数
                            if nextId is not None:
                                if "last_dialog_id" in self.dialogData[self.part][nextId] and self.dialogData[self.part][nextId]["last_dialog_id"] is not None:
                                    self.dialogData[self.part][nextId]["last_dialog_id"] = lastId
                            else:
                                self.dialogData[self.part][lastId]["next_dialog_id"] = None
                            needDeleteId = self.dialogId
                            self.__update_scene(lastId)
                            del self.dialogData[self.part][needDeleteId]
                        else:
                            print("no last_dialog_id")
                    elif buttonHovered == "next":
                        nextId = self.__get_next_id(surface)
                        if nextId is not None:
                            self.__update_scene(nextId)
                        else:
                            print("no next_dialog_id")
                    elif buttonHovered == "add":
                        nextId=1
                        while nextId in self.dialogData[self.part]:
                            nextId+=1
                        self.__add_dialog(nextId)
                    elif buttonHovered == "save":
                        self.__save()
                    elif buttonHovered == "reload":
                        self.__loadDialogData(self.part)
                    else:
                        leftClick = True
                #鼠标中键 -- 切换场景
                elif event.button == 2:
                    self.dialogId += 1
                    if self.dialogId == len(self.parts):
                        self.dialogId = 0
                    self.__update_scene("head")
                #鼠标右键
                elif event.button == 3:
                    #移除角色立绘
                    if self._npcManager.npcGetClick is not None:
                        self.dialogData[self.part][self.dialogId]["characters_img"].remove(self._npcManager.npcGetClick)
                        self._npcManager.update(self.dialogData[self.part][self.dialogId]["characters_img"])
                        self._npcManager.npcGetClick = None
                #鼠标滚轮
                elif event.button == 4:
                    if self.UIContainerRight_kind == "npc":
                        self.npc_local_y += 10
                    elif self.UIContainerRight_kind == "background":
                        self.background_image_local_y += 10
                elif event.button == 5:
                    if self.UIContainerRight_kind == "npc":
                        self.npc_local_y -= 10
                    elif self.UIContainerRight_kind == "background":
                        self.background_image_local_y -= 10
        #画上右侧的菜单选项
        self.UIContainerRightButton.display(surface,(self.UIContainerRight.x,0))
        self.UIContainerRight.draw(surface)
        if self.UIContainerRight.x < display.get_width():
            #检测按钮
            if isHover(self.button_select_background,local_x=self.UIContainerRight.x) and leftClick:
                self.UIContainerRight_kind = "background"
            if isHover(self.button_select_npc,local_x=self.UIContainerRight.x) and leftClick:
                self.UIContainerRight_kind = "npc"
            #画出按钮
            self.button_select_background.display(surface,(self.UIContainerRight.x,0))
            self.button_select_npc.display(surface,(self.UIContainerRight.x,0))
            #画出对应的种类可选的背景图片或者立绘
            if self.UIContainerRight_kind == "background":
                imgName = self.dialogData[self.part][self.dialogId]["background_img"]
                if imgName is not None:
                    imgTmp = resizeImg(self.all_background_image[imgName],(self.UIContainerRight.get_width()*0.8,None))
                    pos = (self.UIContainerRight.x+self.UIContainerRight.get_width()*0.1,self.background_image_local_y)
                    surface.blit(imgTmp,pos)
                    surface.blit(resizeImg(self.background_deselect,imgTmp.get_size()),pos)
                    if leftClick and isHover(imgTmp,pos):
                        self.dialogData[self.part][self.dialogId]["background_img"] = None
                        self._update_background_image(None)
                        leftClick = False
                        i = 0
                    else:
                        i = 1
                else:
                    i = 0
                for imgName in self.all_background_image:
                    if imgName != self.dialogData[self.part][self.dialogId]["background_img"]:
                        imgTmp = resizeImg(self.all_background_image[imgName],(self.UIContainerRight.get_width()*0.8,None))
                        pos = (
                            self.UIContainerRight.x+self.UIContainerRight.get_width()*0.1,
                            self.background_image_local_y+imgTmp.get_height()*1.5*i
                            )
                        surface.blit(imgTmp,pos)
                        i+=1
                        if leftClick and isHover(imgTmp,pos):
                            self.dialogData[self.part][self.dialogId]["background_img"] = imgName
                            self._update_background_image(imgName)
                            leftClick = False
            elif self.UIContainerRight_kind == "npc":
                npc_local_y_temp = self.npc_local_y
                for key,npcImage in self._npcManager.npcImageDict.items():
                    if npc_local_y_temp >= display.get_height():
                        break
                    else:
                        npcImage["normal"].set_width_with_size_locked(int(self.UIContainerRight.get_width()*0.8))
                        if npc_local_y_temp > -npcImage["normal"].get_height():
                            npcImage["normal"].set_pos(self.UIContainerRight.x,npc_local_y_temp)
                            npcImage["normal"].draw(surface)
                            if npcImage["normal"].is_hover() and leftClick:
                                if self.dialogData[self.part][self.dialogId]["characters_img"] is None:
                                    self.dialogData[self.part][self.dialogId]["characters_img"] = []
                                if len(self.dialogData[self.part][self.dialogId]["characters_img"]) < 2:
                                    self.dialogData[self.part][self.dialogId]["characters_img"].append(key)
                                    self._npcManager.update(self.dialogData[self.part][self.dialogId]["characters_img"])
                        npc_local_y_temp += npcImage["normal"].get_height()*1.1
