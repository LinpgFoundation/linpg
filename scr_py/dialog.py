# cython: language_level=3
from .dialogModule import *

#视觉小说系统模块
class DialogSystem(DialogSystemInterface):
    def __init__(self) -> None:
        DialogSystemInterface.__init__(self)
        #选项栏-选中
        self.optionBoxSelected = loadImg("Assets/image/UI/option_selected.png")
        #UI按钮
        self.ButtonsMananger = DialogButtons()
        #加载对话框系统
        self.dialogTxtSystem = DialogContent(display.get_width()*0.015)
        #更新音效
        self.__update_sound_volume()
        #是否要显示历史对白页面
        self.showHistory = False
        self.historySurface = None
        self.historySurface_local_y = 0
        #展示历史界面-返回按钮
        buttonTemp = loadImg("Assets/image/UI/back.png",(display.get_width()*0.03,display.get_height()*0.04))
        self.history_back = Button(addDarkness(buttonTemp,100),display.get_width()*0.04,display.get_height()*0.04)
        self.history_back.setHoverImg(buttonTemp)
        #是否开启自动保存
        self.auto_save = False
        #暂停菜单
        self.pause_menu = PauseMenu()
    #保存数据-子类必须实现
    def save_process(self): raise Exception('LinpgEngine-Error: "You have to overwrite save_process() before continue!"')
    #读取章节
    def load(self,save_path:str) -> None:
        saveData = loadConfig(save_path)
        if saveData["type"] == "dialog_before_battle" or saveData["type"] == "dialog_after_battle":
            """章节信息"""
            self._initialize(
                saveData["chapterType"],
                saveData["chapterId"],
                saveData["type"],
                saveData["collection_name"],
                saveData["id"],
                saveData["dialog_options"]
                )
            self.__process_data()
        else:
            raise Exception('LinpgEngine-Error: Cannot load the data from the "save.yaml" file because the file type does not match')
    #新建章节
    def new(self,chapterType:str,chapterId:int,part:str,collection_name:str=None) -> None:
        """章节信息"""
        self._initialize(chapterType,chapterId,part,collection_name)
        self.__process_data()
    #加载章节信息
    def __process_data(self) -> None:
        dialogData = loadConfig(
            "Data/{0}/chapter{1}_dialogs_{2}.yaml".format(self.chapterType,self.chapterId,get_setting("Language"))
            ) if self.collection_name == None else loadConfig("Data/{0}/{1}/chapter{2}_dialogs_{3}.yaml".format(
                self.chapterType,self.collection_name,self.chapterId,get_setting("Language")))
        #如果该dialog文件是另一个语言dialog文件的子类
        if "default_lang" in dialogData and dialogData["default_lang"] != None:
            self.dialogContent = loadConfig("Data/{0}/chapter{1}_dialogs_{2}.yaml".format(
                self.chapterType,self.chapterId,dialogData["default_lang"]),
                self.part) if self.collection_name == None else loadConfig("Data/{0}/{1}/chapter{2}_dialogs_{3}.yaml".format(
                    self.chapterType,self.collection_name,self.chapterId,dialogData["default_lang"]),self.part)
            for key,currentDialog in dialogData[self.part].items():
                if key in self.dialogContent:
                    for key2,dataNeedReplace in currentDialog.items():
                        self.dialogContent[key][key2] = dataNeedReplace
                else:
                    self.dialogContent[key] = currentDialog
        else:
            self.dialogContent = dialogData[self.part]
            if len(self.dialogContent)==0:
                raise Exception('LinpgEngine-Error: The dialog has no content!')
        self.npc_img_dic.process(self.dialogContent[self.dialogId]["characters_img"])
        #如果dialog Id 不存在
        if self.dialogId not in self.dialogContent:
            raise Exception('LinpgEngine-Error: The dialog id {} does not exist!'.format(self.dialogId))
        else:
            self.dialogTxtSystem.update(self.dialogContent[self.dialogId]["content"],self.dialogContent[self.dialogId]["narrator"])
        #更新背景音乐
        self.backgroundContent.update(self.dialogContent[self.dialogId]["background_img"],None)
    #更新场景
    def __update_scene(self,theNextDialogId:str) -> None:
        #更新背景
        self.backgroundContent.update(
            self.dialogContent[theNextDialogId]["background_img"],
            self.dialogContent[theNextDialogId]["background_music"]
            )
        #重设立绘系统
        self.npc_img_dic.process(self.dialogContent[theNextDialogId]["characters_img"])
        #切换dialogId
        self.dialogId = theNextDialogId
        self.dialogTxtSystem.update(self.dialogContent[self.dialogId]["content"],self.dialogContent[self.dialogId]["narrator"])
        #是否保存
        if self.auto_save:
            self.save_process()
    #更新音量
    def __update_sound_volume(self) -> None:
        self.backgroundContent.set_sound_volume(get_setting("Sound","background_music"))
        self.dialogTxtSystem.set_sound_volume(get_setting("Sound","sound_effects"))
    def ready(self) -> None:
        self.backgroundContent.update(
            self.dialogContent[self.dialogId]["background_img"],
            self.dialogContent[self.dialogId]["background_music"]
            )
    #淡入
    def fadeIn(self,screen) -> None:
        for i in range(255,0,-5):
            self.backgroundContent.display(screen)
            self.black_bg.set_alpha(i)
            self.black_bg.draw(screen)
            pygame.display.flip()
        #重设black_bg的alpha值以便下一次使用
        self.black_bg.set_alpha(255)
    #淡出
    def fadeOut(self,screen) -> None:
        pygame.mixer.music.fadeout(1000)
        pygame.mixer.fadeout(1000)
        for i in range(0,255,5):
            self.black_bg.set_alpha(i)
            self.black_bg.draw(screen)
            pygame.display.flip()
    def display(self,screen) -> None:
        #检测章节是否初始化
        if self.chapterId == None: raise Exception('LinpgEngine-Error: The dialog has not been initialized!')
        #背景
        self.backgroundContent.display(screen)
        self.npc_img_dic.display(screen)
        #按钮
        buttonEvent = self.ButtonsMananger.display(screen,self.dialogTxtSystem.isHidden)
        #显示对话框和对应文字
        self.dialogTxtSystem.display(screen)
        dialogPlayResult = self.dialogTxtSystem.is_all_played()
        #更新event
        self._update_event()
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
                        self.fadeOut(screen)
                        self._isPlaying = False
                    elif buttonEvent == "auto" and not self.showHistory:
                        self.ButtonsMananger.autoModeSwitch()
                        self.dialogTxtSystem.autoMode = self.ButtonsMananger.autoMode
                    elif buttonEvent == "history" and not self.showHistory:
                        self.showHistory = True
                    elif isHover(self.history_back) and self.showHistory:
                        self.showHistory = False
                        self.historySurface = None
                    #如果所有行都没有播出，则播出所有行
                    elif not dialogPlayResult:
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
                    if self.dialogContent[self.dialogId]["last_dialog_id"] != None:
                        self.__update_scene(self.dialogContent[self.dialogId]["last_dialog_id"])
                        dialogPlayResult = False
                    else:
                        pass
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                process_saved_text = ImageSurface(self.dialogTxtSystem.FONT.render(get_lang("ProcessSaved"),get_fontMode(),(255, 255, 255)),0,0)
                process_saved_text.set_alpha(0)
                while True:
                    self._update_event()
                    result = self.pause_menu.display(screen,self.events)
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
                        self.fadeOut(screen)
                        self._isPlaying = False
                        break
                    #如果播放玩菜单后发现有东西需要更新
                    if setting.display(screen,self.events):
                        self.__update_sound_volume()
                    process_saved_text.drawOnTheCenterOf(screen)
                    process_saved_text.fade_out(5)
                    display.flip()
                del process_saved_text
                self.pause_menu.screenshot = None
        #显示选项
        if dialogPlayResult and self.dialogContent[self.dialogId]["next_dialog_id"] != None and self.dialogContent[self.dialogId]["next_dialog_id"]["type"] == "option":
            optionBox_y_base = (display.get_height()*3/4-(len(self.dialogContent[self.dialogId]["next_dialog_id"]["target"]))*2*display.get_width()*0.03)/4
            optionBox_height = int(display.get_width()*0.05)
            nextDialogId = None
            i=0
            for i in range(len(self.dialogContent[self.dialogId]["next_dialog_id"]["target"])):
                option_txt = self.dialogTxtSystem.fontRender(self.dialogContent[self.dialogId]["next_dialog_id"]["target"][i]["txt"],(255, 255, 255))
                optionBox_width = int(option_txt.get_width()+display.get_width()*0.05) 
                optionBox_x = (display.get_width()-optionBox_width)/2
                optionBox_y = (i+1)*2*display.get_width()*0.03+optionBox_y_base
                mouse_x,mouse_y = pygame.mouse.get_pos()
                if optionBox_x<mouse_x<optionBox_x+optionBox_width and optionBox_y<mouse_y<optionBox_y+optionBox_height:
                    optionBox_scaled = resizeImg(self.optionBoxSelected,(optionBox_width,optionBox_height))
                    if leftClick and not self.showHistory:
                        #保存选取的选项
                        nextDialogId = self.dialogContent[self.dialogId]["next_dialog_id"]["target"][i]["id"]
                else:
                    optionBox_scaled = resizeImg(self.optionBox,(optionBox_width,optionBox_height))
                displayWithInCenter(option_txt,optionBox_scaled,optionBox_x,optionBox_y,screen)
            if nextDialogId != None:
                self.dialog_options[self.dialogId] = {"id":i,"target":nextDialogId}
                #更新场景
                self.__update_scene(nextDialogId)
                leftClick = False
        #展示历史
        if self.showHistory:
            if self.historySurface == None:
                self.historySurface = pygame.Surface(display.get_size(),flags=pygame.SRCALPHA).convert_alpha()
                pygame.draw.rect(self.historySurface,(0,0,0),((0,0),display.get_size()))
                self.historySurface.set_alpha(150)
                dialogIdTemp = "head"
                local_y = self.historySurface_local_y
                while dialogIdTemp != None:
                    if self.dialogContent[dialogIdTemp]["narrator"] != None:
                        narratorTemp = self.dialogTxtSystem.fontRender(self.dialogContent[dialogIdTemp]["narrator"]+': ["',(255, 255, 255))
                        self.historySurface.blit(narratorTemp,(display.get_width()*0.15-narratorTemp.get_width(),display.get_height()*0.1+local_y))
                    for i in range(len(self.dialogContent[dialogIdTemp]["content"])):
                        txt = self.dialogContent[dialogIdTemp]["content"][i]
                        txt += '"]' if i == len(self.dialogContent[dialogIdTemp]["content"])-1 and self.dialogContent[dialogIdTemp]["narrator"] != None else ""
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
            screen.blit(self.historySurface,(0,0))
            self.history_back.display(screen)
            isHover(self.history_back)
        elif self.dialogTxtSystem.needUpdate() or leftClick:
            if self.dialogContent[self.dialogId]["next_dialog_id"] == None or self.dialogContent[self.dialogId]["next_dialog_id"]["target"] == None:
                self.fadeOut(screen)
                self._isPlaying = False
            elif self.dialogContent[self.dialogId]["next_dialog_id"]["type"] == "default":
                self.__update_scene(self.dialogContent[self.dialogId]["next_dialog_id"]["target"])
            #如果是需要播放过程动画
            elif self.dialogContent[self.dialogId]["next_dialog_id"]["type"] == "cutscene":
                self.fadeOut(screen)
                cutscene(screen,"Assets\movie\{}".format(self.dialogContent[self.dialogId]["next_dialog_id"]["target"]))
                self._isPlaying = False
            #如果是切换场景
            elif self.dialogContent[self.dialogId]["next_dialog_id"]["type"] == "changeScene":
                self.fadeOut(screen)
                pygame.time.wait(2000)
                #重设立绘系统
                theNextDialogId = self.dialogContent[self.dialogId]["next_dialog_id"]["target"]
                self.npc_img_dic.process(self.dialogContent[theNextDialogId]["characters_img"])
                self.dialogId = theNextDialogId
                self.dialogTxtSystem.resetDialogueboxData()
                self.dialogTxtSystem.update(self.dialogContent[self.dialogId]["content"],self.dialogContent[self.dialogId]["narrator"])
                self.backgroundContent.update(self.dialogContent[self.dialogId]["background_img"],None)
                self.fadeIn(screen)
                #更新背景（音乐）
                self.ready()
        controller.display(screen)

#对话制作器
class DialogSystemDev(DialogSystemInterface):
    def __init__(self,chapterType,chapterId,part,collection_name=None):
        DialogSystemInterface.__init__(self)
        self._initialize(chapterType,chapterId,part,collection_name)
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
        self.npc_img_dic.devMode()
        #将背景的音量调至0
        self.backgroundContent.set_sound_volume(0)
        #从配置文件中加载数据
        self.__loadDialogData()
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
            "back": ButtonWithDes("Assets/image/UI/back.png",button_width,button_y,button_width,button_width,CONFIG["back"]),
            "delete": ButtonWithDes("Assets/image/UI/delete.png",button_width*2.25,button_y,button_width,button_width,CONFIG["delete"]),
            "previous": ButtonWithDes("Assets/image/UI/previous.png",button_width*3.5,button_y,button_width,button_width,CONFIG["previous"]),
            "next": ButtonWithDes("Assets/image/UI/dialog_skip.png",button_width*4.75,button_y,button_width,button_width,CONFIG["next"]),
            "add": ButtonWithDes("Assets/image/UI/add.png",button_width*4.75,button_y,button_width,button_width,CONFIG["add"]),
            "reload": ButtonWithDes("Assets/image/UI/reload.png",button_width*6,button_y,button_width,button_width,CONFIG["reload"]),
            "save": ButtonWithDes("Assets/image/UI/save.png",button_width*7.25,button_y,button_width,button_width,get_lang("General,save"))
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
        for imgPath in glob.glob("Assets/image/dialog_background/*"):
            self.all_background_image[os.path.basename(imgPath)] = loadImg(imgPath)
        self.background_image_local_y = display.get_height()*0.1
    #保存数据
    def __save(self):
        self.dialogData[self.part][self.dialogId]["narrator"] = self.narrator.get_text()
        self.dialogData[self.part][self.dialogId]["content"] = self.content.get_text()
        if self.isDefault:
            saveConfig(self.fileLocation,self.dialogData)
        else:
            #移除掉相似的内容
            for key,currentDialog in self.dialogData_default["dialog_before_battle"].items():
                if key in self.dialogData["dialog_before_battle"]:
                    for key2,dataNeedCompare in currentDialog.items():
                        if self.dialogData["dialog_before_battle"][key][key2] == dataNeedCompare:
                            del self.dialogData["dialog_before_battle"][key][key2]
                    if len(self.dialogData["dialog_before_battle"][key])==0:
                        del self.dialogData["dialog_before_battle"][key]
            for key,currentDialog in self.dialogData_default["dialog_after_battle"].items():
                if key in self.dialogData["dialog_after_battle"]:
                    for key2,dataNeedCompare in currentDialog.items():
                        if self.dialogData["dialog_after_battle"][key][key2] == dataNeedCompare:
                            del self.dialogData["dialog_after_battle"][key][key2]
                    if len(self.dialogData["dialog_after_battle"][key])==0:
                        del self.dialogData["dialog_after_battle"][key]
            saveConfig(self.fileLocation,self.dialogData)
            self.__loadDialogData()
    #读取章节信息
    def __loadDialogData(self):
        self.dialogData = loadConfig(self.fileLocation)
        #初始化文件的数据
        if "dialog_before_battle" not in self.dialogData:
            self.dialogData["dialog_before_battle"] = {}
        if "head" not in self.dialogData["dialog_before_battle"]:
            self.dialogData["dialog_before_battle"]["head"] = self.deafult_dialog_format
        if "dialog_after_battle" not in self.dialogData:
            self.dialogData["dialog_after_battle"] = {}
        if "head" not in self.dialogData["dialog_after_battle"]:
            self.dialogData["dialog_after_battle"]["head"] = self.deafult_dialog_format
        #如果不是默认主语言
        if "default_lang" in self.dialogData and self.dialogData["default_lang"] != None:
            self.isDefault = False
            self.dialogData_default = loadConfig("Data/{0}/chapter{1}_dialogs_{2}.yaml".format(self.chapterType,self.chapterId,self.dialogData["default_lang"])) if self.chapterType == "main_chapter"\
                else loadConfig("Data/{0}/{1}/chapter{2}_dialogs_{3}.yaml".format(self.chapterType,self.collection_name,self.chapterId,self.dialogData["default_lang"]))
            for key,currentDialog in self.dialogData_default["dialog_before_battle"].items():
                if key in self.dialogData["dialog_before_battle"]:
                    for key2,dataNeedReplace in currentDialog.items():
                        if key2 not in self.dialogData["dialog_before_battle"][key]:
                            self.dialogData["dialog_before_battle"][key][key2] = dataNeedReplace
                else:
                    self.dialogData["dialog_before_battle"][key] = currentDialog
            for key,currentDialog in self.dialogData_default["dialog_after_battle"].items():
                if key in self.dialogData["dialog_after_battle"]:
                    for key2,dataNeedReplace in currentDialog.items():
                        if key2 not in self.dialogData["dialog_after_battle"][key]:
                            self.dialogData["dialog_after_battle"][key][key2] = dataNeedReplace
                else:
                    self.dialogData["dialog_after_battle"][key] = currentDialog
        else:
            self.isDefault = True
        self.__update_scene(self.dialogId)
    #更新场景
    def __update_scene(self,theNextDialogId):
        #重设立绘系统
        self.npc_img_dic.process(self.dialogData[self.part][theNextDialogId]["characters_img"])
        self.backgroundContent.update(self.dialogData[self.part][theNextDialogId]["background_img"],None)
        self.dialogId = theNextDialogId
        self.__update_dialogbox()
    #更新对话框
    def __update_dialogbox(self):
        self.narrator.set_text(self.dialogData[self.part][self.dialogId]["narrator"])
        self.content.set_text(self.dialogData[self.part][self.dialogId]["content"])
    #获取下一个对话的ID
    def __get_last_id(self) -> str:
        if self.dialogId == "head":
            return None
        elif "last_dialog_id" in self.dialogData[self.part][self.dialogId] and self.dialogData[self.part][self.dialogId]["last_dialog_id"] != None:
            return self.dialogData[self.part][self.dialogId]["last_dialog_id"]
        else:
            for key,dialogData in self.dialogData[self.part].items():
                if dialogData["next_dialog_id"] != None:
                    if dialogData["next_dialog_id"]["type"] == "default" and dialogData["next_dialog_id"]["target"] == self.dialogId:
                        return key
                    elif dialogData["next_dialog_id"]["type"] == "changeScene" and dialogData["next_dialog_id"]["target"] == self.dialogId:
                        return key
                    elif dialogData["next_dialog_id"]["type"] == "option":
                        for optionChoice in dialogData["next_dialog_id"]["target"]:
                            if optionChoice["id"] == self.dialogId:
                                return key
            return None
    #获取上一个对话的ID
    def __get_next_id(self,screen) -> str:
        if "next_dialog_id" in self.dialogData[self.part][self.dialogId]:
            theNext = self.dialogData[self.part][self.dialogId]["next_dialog_id"]
            if theNext != None:
                if theNext["type"] == "default" or theNext["type"] == "changeScene":
                    return theNext["target"]
                elif theNext["type"] == "option":
                    optionBox_y_base = (display.get_height()*3/4-(len(theNext["target"]))*2*display.get_width()*0.03)/4
                    for i in range(len(theNext["target"])):
                        option_txt = self.FONT.render(theNext["target"][i]["txt"],get_fontMode(),(255, 255, 255))
                        optionBox_scaled = resizeImg(self.optionBox,
                        (option_txt.get_width()+display.get_width()*0.05,display.get_width()*0.05)
                        )
                        optionBox_x = (display.get_width()-optionBox_scaled.get_width())/2
                        optionBox_y = (i+1)*2*display.get_width()*0.03+optionBox_y_base
                        displayWithInCenter(option_txt,optionBox_scaled,optionBox_x,optionBox_y,screen)
                    while True:
                        leftClick = False
                        for event in pygame.event.get():
                            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.JOYBUTTONDOWN:
                                leftClick = True
                                break
                        for i in range(len(theNext["target"])):
                            option_txt = self.FONT.render(theNext["target"][i]["txt"],get_fontMode(),(255, 255, 255))
                            optionBox_scaled = resizeImg(self.optionBox,
                            (option_txt.get_width()+display.get_width()*0.05,display.get_width()*0.05)
                            )
                            optionBox_x = (display.get_width()-optionBox_scaled.get_width())/2
                            optionBox_y = (i+1)*2*display.get_width()*0.03+optionBox_y_base
                            if isHover(optionBox_scaled,(optionBox_x,optionBox_y)) and leftClick:
                                return theNext["target"][i]["id"]
                        display.flip()
                else:
                    return None
            else:
                return None
        else:
            return None
    def display(self,screen):
        if self.dialogData[self.part][self.dialogId]["background_img"] == None:
            self.black_bg.draw(screen)
        else:
            self.backgroundContent.display(screen)
        #画上NPC立绘
        self.npc_img_dic.display(screen)
        if self.npc_img_dic.npc_get_click != None:
            screen.blit(self.removeNpcButton,pygame.mouse.get_pos())
        #画上对话框
        self.dialoguebox.draw(screen)
        self._update_event()
        self.narrator.display(screen,self.events)
        if self.narrator.needSave:
            self.dialogData[self.part][self.dialogId]["narrator"] = self.narrator.get_text()
        self.content.display(screen,self.events)
        if self.content.needSave:
            self.dialogData[self.part][self.dialogId]["content"] = self.content.get_text()
        #初始化数值
        buttonHovered = None
        theNextDialogId = self.dialogData[self.part][self.dialogId]["next_dialog_id"]
        #展示按钮
        for button in self.buttonsUI:
            if button == "next" and theNextDialogId == None or button == "next" and len(theNextDialogId)<2:
                if isHover(self.buttonsUI["add"]):
                    buttonHovered = "add"
                self.buttonsUI["add"].display(screen)
            elif button != "add":
                if isHover(self.buttonsUI[button]):
                    buttonHovered = button
                self.buttonsUI[button].display(screen)
        if buttonHovered != None:
            self.buttonsUI[buttonHovered].displayDes(screen)
        leftClick = False
        for event in self.events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 or event.type == pygame.JOYBUTTONDOWN and controller.joystick.get_button(0) == 1:
                if isHover(self.UIContainerRightButton,None,self.UIContainerRight.x):
                    self.UIContainerRight.switch()
                    self.UIContainerRightButton.flip(True,False)
                #退出
                elif buttonHovered == "back":
                    self._isPlaying = False
                elif buttonHovered == "previous":
                    lastId = self.__get_last_id()
                    if lastId != None:
                        self.__update_scene(lastId)
                    else:
                        print("no last_dialog_id")
                elif buttonHovered == "delete":
                    lastId = self.__get_last_id()
                    nextId = self.__get_next_id(screen)
                    if lastId != None:
                        if self.dialogData[self.part][lastId]["next_dialog_id"]["type"] == "default" or self.dialogData[self.part][lastId]["next_dialog_id"]["type"] == "changeScene":
                            self.dialogData[self.part][lastId]["next_dialog_id"]["target"] = nextId
                        elif self.dialogData[self.part][lastId]["next_dialog_id"]["type"] == "option":
                            for optionChoice in self.dialogData[self.part][lastId]["next_dialog_id"]["target"]:
                                if optionChoice["id"] == self.dialogId:
                                    optionChoice["id"] = nextId
                                    break
                        else:
                            #如果当前next_dialog_id的类型不支持的话，报错
                            Exception('LinpgEngine-Error: Cannot recognize next_dialog_id type: {}, please fix it'.format(self.dialogData[self.part][lastId]["next_dialog_id"]["type"]))
                        #修改下一个对白配置文件中的"last_dialog_id"的参数
                        if "last_dialog_id" in self.dialogData[self.part][nextId] and self.dialogData[self.part][nextId]["last_dialog_id"] != None:
                            self.dialogData[self.part][nextId]["last_dialog_id"] = lastId
                        needDeleteId = self.dialogId
                        self.__update_scene(lastId)
                        del self.dialogData[self.part][needDeleteId]
                    else:
                        print("no last_dialog_id")
                elif buttonHovered == "next":
                    nextId = self.__get_next_id(screen)
                    if nextId != None:
                        self.__update_scene(nextId)
                    else:
                        print("no next_dialog_id")
                elif buttonHovered == "add":
                    nextId=1
                    while nextId in self.dialogData[self.part]:
                        nextId+=1
                    self.dialogData[self.part][nextId] = {
                        "background_img": None,
                        "background_music": None,
                        "characters_img": [],
                        "content": [self.please_enter_content],
                        "last_dialog_id": self.dialogId,
                        "narrator": self.please_enter_name,
                        "next_dialog_id": None
                    }
                    self.dialogData[self.part][self.dialogId]["next_dialog_id"] = {"target":nextId,"type":"default"}
                    self.__update_scene(nextId)
                elif buttonHovered == "save":
                    self.__save()
                elif buttonHovered == "reload":
                    self.__loadDialogData()
                else:
                    leftClick = True
            #鼠标中键 -- 切换场景
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
                if self.part == "dialog_after_battle":
                    self.part = "dialog_before_battle"
                elif self.part == "dialog_before_battle":
                    self.part = "dialog_after_battle"
                self.__update_scene("head")
            #鼠标右键
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                #移除角色立绘
                if self.npc_img_dic.npc_get_click != None:
                    self.dialogData[self.part][self.dialogId]["characters_img"].remove(self.npc_img_dic.npc_get_click)
                    self.npc_img_dic.process(self.dialogData[self.part][self.dialogId]["characters_img"])
                    self.npc_img_dic.npc_get_click = None
            #鼠标滚轮
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 4:
                if self.UIContainerRight_kind == "npc":
                    self.npc_local_y += 10
                elif self.UIContainerRight_kind == "background":
                    self.background_image_local_y += 10
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 5:
                if self.UIContainerRight_kind == "npc":
                    self.npc_local_y -= 10
                elif self.UIContainerRight_kind == "background":
                    self.background_image_local_y -= 10
        #画上右侧的菜单选项
        self.UIContainerRightButton.display(screen,self.UIContainerRight.x)
        self.UIContainerRight.draw(screen)
        if self.UIContainerRight.x<display.get_width():
            #检测按钮
            if isHover(self.button_select_background,None,self.UIContainerRight.x) and leftClick:
                self.UIContainerRight_kind = "background"
            if isHover(self.button_select_npc,None,self.UIContainerRight.x) and leftClick:
                self.UIContainerRight_kind = "npc"
            #画出按钮
            self.button_select_background.display(screen,self.UIContainerRight.x)
            self.button_select_npc.display(screen,self.UIContainerRight.x)
            #画出对应的种类可选的背景图片或者立绘
            if self.UIContainerRight_kind == "background":
                imgName = self.dialogData[self.part][self.dialogId]["background_img"]
                if imgName != None:
                    imgTmp = resizeImg(self.all_background_image[imgName],(self.UIContainerRight.get_width()*0.8,None))
                    pos = (self.UIContainerRight.x+self.UIContainerRight.get_width()*0.1,self.background_image_local_y)
                    screen.blit(imgTmp,pos)
                    screen.blit(resizeImg(self.background_deselect,imgTmp.get_size()),pos)
                    if leftClick and isHover(imgTmp,pos):
                        self.dialogData[self.part][self.dialogId]["background_img"] = None
                        self.backgroundContent.update(None,None)
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
                        screen.blit(imgTmp,pos)
                        i+=1
                        if leftClick and isHover(imgTmp,pos):
                            self.dialogData[self.part][self.dialogId]["background_img"] = imgName
                            self.backgroundContent.update(imgName,None)
                            leftClick = False
            elif self.UIContainerRight_kind == "npc":
                npc_local_y_temp = self.npc_local_y
                for key,npcImage in self.npc_img_dic.imgDic.items():
                    if npc_local_y_temp >= display.get_height():
                        break
                    else:
                        imgTemp = resizeImg(npcImage["normal"],(self.UIContainerRight.get_width()*0.8,None))
                        if npc_local_y_temp > -imgTemp.get_height():
                            screen.blit(imgTemp,(self.UIContainerRight.x,npc_local_y_temp))
                            if isHover(imgTemp,(self.UIContainerRight.x,npc_local_y_temp)) and leftClick:
                                if self.dialogData[self.part][self.dialogId]["characters_img"] == None:
                                    self.dialogData[self.part][self.dialogId]["characters_img"] = []
                                if len(self.dialogData[self.part][self.dialogId]["characters_img"]) < 2:
                                    self.dialogData[self.part][self.dialogId]["characters_img"].append(key)
                                    self.npc_img_dic.process(self.dialogData[self.part][self.dialogId]["characters_img"])
                        npc_local_y_temp += imgTemp.get_height()*1.1
