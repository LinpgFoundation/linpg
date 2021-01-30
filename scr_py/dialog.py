# cython: language_level=3
from ..scr_core.function import *
from ..scr_pyd.movie import cutscene,VedioFrame,VedioPlayer

#视觉小说系统接口
class DialogSystemInterface(SystemObject):
    def __init__(self):
        SystemObject.__init__(self)
        #加载对话的背景图片模块
        self.backgroundContent = DialogBackground()
        #获取屏幕的尺寸
        self.window_x,self.window_y = display.get_size()
        #加载npc立绘系统并初始化
        self.npc_img_dic = NpcImageSystem()
        #黑色Void帘幕
        self.black_bg = get_SingleColorSurface("black")
        #选项栏
        self.optionBox = loadImg("Assets/image/UI/option.png")
    #初始化关键参数
    def _initialize(self,chapterType,chapterId,part,collection_name,dialogId="head",dialog_options={}):
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

#视觉小说系统模块
class DialogSystem(DialogSystemInterface):
    def __init__(self):
        DialogSystemInterface.__init__(self)
        #选项栏-选中
        self.optionBoxSelected = loadImg("Assets/image/UI/option_selected.png")
        #UI按钮
        self.ButtonsMananger = DialogButtons()
        #加载对话框系统
        self.dialogTxtSystem = DialogContent(self.window_x*0.015)
        #更新音效
        self.__update_sound_volume()
        #是否要显示历史对白页面
        self.showHistory = False
        self.historySurface = None
        self.historySurface_local_y = 0
        #展示历史界面-返回按钮
        buttonTemp = loadImg("Assets/image/UI/back.png",(self.window_x*0.03,self.window_y*0.04))
        self.history_back = Button(addDarkness(buttonTemp,100),self.window_x*0.04,self.window_y*0.04)
        self.history_back.setHoverImg(buttonTemp)
        #是否开启自动保存
        self.auto_save = False
        #暂停菜单
        self.pause_menu = PauseMenu()
    #保存数据
    def save_process(self):
        raise Exception('LinpgEngine-Error: "You have to overwrite save_process() before continue!"')
    #读取章节
    def load(self,save_path):
        saveData = loadConfig(save_path)
        if saveData["type"] == "dialog_before_battle" or saveData["type"] == "dialog_after_battle":
            """章节信息"""
            self._initialize(saveData["chapterType"],saveData["chapterId"],saveData["type"],saveData["collection_name"],saveData["id"],saveData["dialog_options"])
            self.__process_data()
        else:
            raise Exception('LinpgEngine-Error: Cannot load the data from the "save.yaml" file because the file type does not match')
    #新建章节
    def new(self,chapterType,chapterId,part,collection_name=None):
        """章节信息"""
        self._initialize(chapterType,chapterId,part,collection_name)
        self.__process_data()
    #加载章节信息
    def __process_data(self):
        dialogData = loadConfig("Data/{0}/chapter{1}_dialogs_{2}.yaml".format(self.chapterType,self.chapterId,get_setting("Language"))) if self.collection_name == None\
            else loadConfig("Data/{0}/{1}/chapter{2}_dialogs_{3}.yaml".format(self.chapterType,self.collection_name,self.chapterId,get_setting("Language")))
        #如果该dialog文件是另一个语言dialog文件的子类
        if "default_lang" in dialogData and dialogData["default_lang"] != None:
            self.dialogContent = loadConfig("Data/{0}/chapter{1}_dialogs_{2}.yaml".format(self.chapterType,self.chapterId,dialogData["default_lang"]),self.part) if self.collection_name == None\
                else loadConfig("Data/{0}/{1}/chapter{2}_dialogs_{3}.yaml".format(self.chapterType,self.collection_name,self.chapterId,dialogData["default_lang"]),self.part)
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
    def __update_scene(self,theNextDialogId):
        #更新背景
        self.backgroundContent.update(self.dialogContent[theNextDialogId]["background_img"],self.dialogContent[theNextDialogId]["background_music"])
        #重设立绘系统
        self.npc_img_dic.process(self.dialogContent[theNextDialogId]["characters_img"])
        #切换dialogId
        self.dialogId = theNextDialogId
        self.dialogTxtSystem.update(self.dialogContent[self.dialogId]["content"],self.dialogContent[self.dialogId]["narrator"])
        #是否保存
        if self.auto_save:
            self.save_process()
    #更新音量
    def __update_sound_volume(self):
        self.backgroundContent.set_sound_volume(get_setting("Sound","background_music"))
        self.dialogTxtSystem.set_sound_volume(get_setting("Sound","sound_effects"))
    def display(self,screen):
        #检测章节是否初始化
        if self.chapterId == None:
            raise Exception('LinpgEngine-Error: The dialog has not been initialized!')
        self.window_x,self.window_y = screen.get_size()
        #背景
        self.backgroundContent.display(screen)
        self.npc_img_dic.display(screen)
        #按钮
        buttonEvent = self.ButtonsMananger.display(screen,self.dialogTxtSystem.isHidden)
        #显示对话框和对应文字
        dialogPlayResult = self.dialogTxtSystem.display(screen)
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
                        return True
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
                    self.historySurface_local_y += self.window_y*0.1
                elif event.button == 5:
                    self.historySurface = None
                    self.historySurface_local_y -= self.window_y*0.1
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
                        return True
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
            optionBox_y_base = (self.window_y*3/4-(len(self.dialogContent[self.dialogId]["next_dialog_id"]["target"]))*2*self.window_x*0.03)/4
            optionBox_height = int(self.window_x*0.05)
            nextDialogId = None
            i=0
            for i in range(len(self.dialogContent[self.dialogId]["next_dialog_id"]["target"])):
                option_txt = self.dialogTxtSystem.fontRender(self.dialogContent[self.dialogId]["next_dialog_id"]["target"][i]["txt"],(255, 255, 255))
                optionBox_width = int(option_txt.get_width()+self.window_x*0.05) 
                optionBox_x = (self.window_x-optionBox_width)/2
                optionBox_y = (i+1)*2*self.window_x*0.03+optionBox_y_base
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
                self.historySurface = pygame.Surface((self.window_x,self.window_y),flags=pygame.SRCALPHA).convert_alpha()
                pygame.draw.rect(self.historySurface,(0,0,0),(0,0,self.window_x,self.window_y))
                self.historySurface.set_alpha(150)
                dialogIdTemp = "head"
                local_y = self.historySurface_local_y
                while dialogIdTemp != None:
                    if self.dialogContent[dialogIdTemp]["narrator"] != None:
                        narratorTemp = self.dialogTxtSystem.fontRender(self.dialogContent[dialogIdTemp]["narrator"]+': ["',(255, 255, 255))
                        self.historySurface.blit(narratorTemp,(self.window_x*0.15-narratorTemp.get_width(),self.window_y*0.1+local_y))
                    for i in range(len(self.dialogContent[dialogIdTemp]["content"])):
                        txt = self.dialogContent[dialogIdTemp]["content"][i]
                        txt += '"]' if i == len(self.dialogContent[dialogIdTemp]["content"])-1 and self.dialogContent[dialogIdTemp]["narrator"] != None else ""
                        self.historySurface.blit(self.dialogTxtSystem.fontRender(txt,(255, 255, 255)),(self.window_x*0.15,self.window_y*0.1+local_y))
                        local_y+=self.dialogTxtSystem.FONTSIZE*1.5
                    if dialogIdTemp != self.dialogId:
                        if self.dialogContent[dialogIdTemp]["next_dialog_id"]["type"] == "default" or self.dialogContent[dialogIdTemp]["next_dialog_id"]["type"] == "changeScene":
                            dialogIdTemp = self.dialogContent[dialogIdTemp]["next_dialog_id"]["target"]
                        elif self.dialogContent[dialogIdTemp]["next_dialog_id"]["type"] == "option":
                            narratorTemp = self.dialogTxtSystem.fontRender(self.ButtonsMananger.choiceTxt+" - ",(0,191,255))
                            self.historySurface.blit(narratorTemp,(self.window_x*0.15-narratorTemp.get_width(),self.window_y*0.1+local_y))
                            self.historySurface.blit(self.dialogTxtSystem.fontRender(str(self.dialog_options[dialogIdTemp]["target"]),(0,191,255)),(self.window_x*0.15,self.window_y*0.1+local_y))
                            local_y+=self.dialogTxtSystem.FONTSIZE*1.5
                            dialogIdTemp = self.dialog_options[dialogIdTemp]["target"]
                        else:
                            dialogIdTemp = None
                    else:
                        dialogIdTemp = None
            screen.blit(self.historySurface,(0,0))
            self.history_back.display(screen)
            isHover(self.history_back)
        elif self.dialogTxtSystem.forceUpdate() or leftClick:
            if self.dialogContent[self.dialogId]["next_dialog_id"] == None or self.dialogContent[self.dialogId]["next_dialog_id"]["target"] == None:
                self.fadeOut(screen)
                return True
            elif self.dialogContent[self.dialogId]["next_dialog_id"]["type"] == "default":
                self.__update_scene(self.dialogContent[self.dialogId]["next_dialog_id"]["target"])
            #如果是需要播放过程动画
            elif self.dialogContent[self.dialogId]["next_dialog_id"]["type"] == "cutscene":
                self.fadeOut(screen)
                cutscene(screen,"Assets\movie\{}".format(self.dialogContent[self.dialogId]["next_dialog_id"]["target"]))
                return True
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
        return False
    def ready(self):
        self.backgroundContent.update(self.dialogContent[self.dialogId]["background_img"],self.dialogContent[self.dialogId]["background_music"])
    #淡出
    def fadeOut(self,screen):
        pygame.mixer.music.fadeout(1000)
        pygame.mixer.fadeout(1000)
        for i in range(0,255,5):
            self.black_bg.set_alpha(i)
            self.black_bg.draw(screen)
            pygame.display.flip()
    #淡入
    def fadeIn(self,screen):
        for i in range(255,0,-5):
            self.backgroundContent.display(screen)
            self.black_bg.set_alpha(i)
            self.black_bg.draw(screen)
            pygame.display.flip()
        #重设black_bg的alpha值以便下一次使用
        self.black_bg.set_alpha(255)

#对话制作器
class DialogSystemDev(DialogSystemInterface):
    def __init__(self,chapterType,chapterId,part,collection_name=None):
        DialogSystemInterface.__init__(self)
        self._initialize(chapterType,chapterId,part,collection_name)
        #设定初始化
        self.lang = get_setting("Language")
        self.fileLocation = "Data/{0}/chapter{1}_dialogs_{2}.yaml".format(self.chapterType,self.chapterId,self.lang) if self.chapterType == "main_chapter"\
            else "Data/{0}/{1}/chapter{2}_dialogs_{3}.yaml".format(self.chapterType,self.collection_name,self.chapterId,self.lang)
        #文字
        self.FONTSIZE = self.window_x*0.015
        self.FONT = createFont(self.FONTSIZE)
        #对话框
        self.dialoguebox = loadImage("Assets/image/UI/dialoguebox.png",(self.window_x*0.13,self.window_y*0.65),self.window_x*0.74,self.window_y/4)
        self.narrator = SingleLineInputBox(self.window_x*0.2,self.dialoguebox.y+self.FONTSIZE,self.FONTSIZE,"white")
        self.content = MultipleLinesInputBox(self.window_x*0.2,self.window_y*0.73,self.FONTSIZE,"white")
        #将npc立绘系统设置为开发者模式
        self.npc_img_dic.devMode()
        #将背景的音量调至0
        self.backgroundContent.set_sound_volume(0)
        #从配置文件中加载数据
        self.__loadDialogData()
        #背景选择界面
        widthTmp = int(self.window_x*0.2)
        self.UIContainerRight = loadDynamicImage("Assets/image/UI/container.png",(self.window_x*0.8+widthTmp,0),(self.window_x*0.8,0),(widthTmp/10,0),widthTmp,self.window_y)
        self.UIContainerRightButton = loadImage("Assets/image/UI/container_button.png",(-self.window_x*0.03,self.window_y*0.4),int(self.window_x*0.04),int(self.window_y*0.2))
        self.UIContainerRight.rotate(90)
        self.UIContainerRightButton.rotate(90)
        self.background_deselect = loadImg("Assets/image/UI/deselect.png")
        self.UIContainerRight_kind = "background"
        #UI按钮
        CONFIG = get_lang("DialogCreator")
        button_width = self.window_x*0.05
        button_y = self.window_y*0.03
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
            "save": ButtonWithDes("Assets/image/UI/save.png",button_width*7.25,button_y,button_width,button_width,CONFIG["save"])
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
        self.background_image_local_y = self.window_y*0.1
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
    def __get_last_id(self):
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
    def __get_next_id(self,screen):
        if "next_dialog_id" in self.dialogData[self.part][self.dialogId]:
            theNext = self.dialogData[self.part][self.dialogId]["next_dialog_id"]
            if theNext != None:
                if theNext["type"] == "default" or theNext["type"] == "changeScene":
                    return theNext["target"]
                elif theNext["type"] == "option":
                    optionBox_y_base = (self.window_y*3/4-(len(theNext["target"]))*2*self.window_x*0.03)/4
                    for i in range(len(theNext["target"])):
                        option_txt = self.FONT.render(theNext["target"][i]["txt"],get_fontMode(),(255, 255, 255))
                        optionBox_scaled = resizeImg(self.optionBox,(option_txt.get_width()+self.window_x*0.05,self.window_x*0.05))
                        optionBox_x = (self.window_x-optionBox_scaled.get_width())/2
                        optionBox_y = (i+1)*2*self.window_x*0.03+optionBox_y_base
                        displayWithInCenter(option_txt,optionBox_scaled,optionBox_x,optionBox_y,screen)
                    while True:
                        leftClick = False
                        for event in pygame.event.get():
                            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.JOYBUTTONDOWN:
                                leftClick = True
                                break
                        for i in range(len(theNext["target"])):
                            option_txt = self.FONT.render(theNext["target"][i]["txt"],get_fontMode(),(255, 255, 255))
                            optionBox_scaled = resizeImg(self.optionBox,(option_txt.get_width()+self.window_x*0.05,self.window_x*0.05))
                            optionBox_x = (self.window_x-optionBox_scaled.get_width())/2
                            optionBox_y = (i+1)*2*self.window_x*0.03+optionBox_y_base
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
                    return True
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
        if self.UIContainerRight.x<self.window_x:
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
                        pos = (self.UIContainerRight.x+self.UIContainerRight.get_width()*0.1,self.background_image_local_y+imgTmp.get_height()*1.5*i)
                        screen.blit(imgTmp,pos)
                        i+=1
                        if leftClick and isHover(imgTmp,pos):
                            self.dialogData[self.part][self.dialogId]["background_img"] = imgName
                            self.backgroundContent.update(imgName,None)
                            leftClick = False
            elif self.UIContainerRight_kind == "npc":
                npc_local_y_temp = self.npc_local_y
                for key,npcImage in self.npc_img_dic.imgDic.items():
                    if npc_local_y_temp >= self.window_y:
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
        return False

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
                self.imgDic[nameTemp]["communication"] = pygame.Surface((int(self.img_width/1.9), int(self.img_width/1.8)), flags=pygame.SRCALPHA)
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
                if self.__NPC_IMAGE_DATABASE.ifSameKind(self.npcLastRound[0],self.npcThisRound[1]) and self.__NPC_IMAGE_DATABASE.ifSameKind(self.npcLastRound[1],self.npcThisRound[0]):
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
            screen.blit(resizeImg(self.dialoguebox,(screen.get_width()*0.74,self.dialoguebox_height)),(screen.get_width()*0.13,self.dialoguebox_y))
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
                screen.blit(self.FONT.render(self.content[self.displayedLine][:self.textIndex],get_fontMode(),(255, 255, 255)),(x,y+self.FONTSIZE*1.5*self.displayedLine))
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
                    self.backgroundImgSurface = loadImage(os.path.join("Assets/image/dialog_background",self.backgroundImgName),(0,0),display.get_width(),display.get_height())
                #如果在背景图片的文件夹里找不到对应的图片，则查看是否是视频文件
                elif os.path.exists("Assets/movie/"+self.backgroundImgName):
                    try:
                        self.backgroundImgSurface = VedioFrame("Assets/movie/"+self.backgroundImgName,display.get_width(),display.get_height(),True)
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
                    screen.blit(rotatedIcon,(self.autoButtonHovered.description+self.autoIconHovered.get_width()/2-rotatedIcon.get_width()/2,\
                        self.autoButtonHovered.y+self.icon_y+self.autoIconHovered.get_height()/2-rotatedIcon.get_height()/2))
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
                    screen.blit(rotatedIcon,(self.autoButtonHovered.description+self.autoIconHovered.get_width()/2-rotatedIcon.get_width()/2,\
                        self.autoButtonHovered.y+self.icon_y+self.autoIconHovered.get_height()/2-rotatedIcon.get_height()/2))
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
    def __init__(self):
        self.__DATA = loadConfig("Data/npcImageDatabase.yaml","Data")
    def get_kind(self,fileName):
        for key in self.__DATA:
            if fileName in self.__DATA[key]:
                return key
        return None
    def ifSameKind(self,fileName1,fileName2):
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