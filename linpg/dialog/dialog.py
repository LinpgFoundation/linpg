# cython: language_level=3
from .dialogModule import *

#视觉小说系统模块
class DialogSystem(AbstractDialogSystem):
    def __init__(self) -> None:
        super().__init__()
        #UI按钮
        self._buttons_mananger = DialogButtons()
        #加载对话框系统
        self._dialog_txt_system = DialogContent(int(display.get_width()*0.015))
        #更新音效
        self.__update_sound_volume()
        #是否要显示历史对白页面
        self._is_showing_history:bool = False
        self._history_surface = None
        self._history_surface_local_y = 0
        #展示历史界面-返回按钮
        buttonTemp = loadImg(os.path.join(DIALOG_UI_PATH,"back.png"),(display.get_width()*0.03,display.get_height()*0.04))
        self.history_back = Button(addDarkness(buttonTemp,100),display.get_width()*0.04,display.get_height()*0.04)
        self.history_back.set_hover_img(buttonTemp)
        #暂停菜单
        self.pause_menu = PauseMenu()
    #返回需要保存数据
    def _get_data_need_to_save(self) -> dict: return dicMerge(
        self.data_of_parent_game_system, {"dialog_id": self._dialog_id, "dialog_options": self.dialog_options, "type": self.part}
        )
    #读取章节
    def load(self, save_path:str) -> None:
        saveData = loadConfig(save_path)
        """章节信息"""
        self._initialize(
            saveData["chapter_type"],
            saveData["chapter_id"],
            saveData["project_name"],
            saveData["dialog_id"],
            saveData["dialog_options"]
            )
        self.part = saveData["type"]
        self.__process_data()
    #新建章节
    def new(self, chapterType:str, chapterId:int, part:str, project_name:str=None) -> None:
        """章节信息"""
        self._initialize(chapterType,chapterId,project_name)
        self.part = part
        self.__process_data()
    #加载章节信息
    def __process_data(self) -> None:
        #读取目标对话文件的数据
        currentDialogData = loadConfig(self.get_dialog_file_location(get_setting("Language")),"dialogs")[self.part]
        default_lang_of_dialog:str = self.get_default_lang()
        #如果该dialog文件是另一个语言dialog文件的子类
        if default_lang_of_dialog != get_setting("Language"):
            self.dialogContent = loadConfig(self.get_dialog_file_location(default_lang_of_dialog),"dialogs")[self.part]
            for key,currentDialog in currentDialogData.items():
                if key in self.dialogContent:
                    for key2,dataNeedReplace in currentDialog.items():
                        self.dialogContent[key][key2] = dataNeedReplace
                else:
                    self.dialogContent[key] = currentDialog
        #如果该dialog文件是主语言
        else:
            self.dialogContent = currentDialogData
            if len(self.dialogContent) == 0: throwException("error","The dialog file has no content! You need to at least set up a head.")
        #将数据载入刚初始化的模块中
        self.__update_scene(self._dialog_id)
        self._dialog_txt_system.resetDialogueboxData()
    #更新场景
    def __update_scene(self, theNextDialogId:Union[str,int]) -> None:
        #如果dialog Id 不存在
        if theNextDialogId in self.dialogContent:
            #更新背景音乐
            if self.dialogContent[theNextDialogId]["background_music"] is not None:
                self.set_bgm(os.path.join(self._background_music_folder_path,self.dialogContent[theNextDialogId]["background_music"]))
            else:
                self.set_bgm(None)
            #更新背景和立绘
            self._npc_manager.update(self.dialogContent[theNextDialogId]["characters_img"])
            self._update_background_image(self.dialogContent[theNextDialogId]["background_img"])
            #更新对话框文字
            self._dialog_txt_system.update(self.dialogContent[theNextDialogId]["content"],self.dialogContent[theNextDialogId]["narrator"])
            #切换dialogId
            self._dialog_id = theNextDialogId
            #自动保存
            if self.auto_save: self.save_progress()
        else:
            throwException("error","The dialog id {} does not exist!".format(theNextDialogId))
    #更新音量
    def __update_sound_volume(self) -> None:
        self.set_bgm_volume(get_setting("Sound","background_music")/100)
        self._dialog_txt_system.set_sound_volume(get_setting("Sound","sound_effects"))
    #淡入
    def fadeIn(self, surface:pygame.Surface) -> None:
        for i in range(255,0,-5):
            self.display_background_image(surface)
            self._black_bg.set_alpha(i)
            self._black_bg.draw(surface)
            display.flip()
        #重设black_bg的alpha值以便下一次使用
        self._black_bg.set_alpha(255)
    #淡出
    def fadeOut(self, surface:pygame.Surface) -> None:
        pygame.mixer.music.fadeout(1000)
        pygame.mixer.fadeout(1000)
        for i in range(0,255,5):
            self._black_bg.set_alpha(i)
            self._black_bg.draw(surface)
            display.flip()
    def draw(self, surface:pygame.Surface) -> None:
        super().draw(surface)
        #显示对话框和对应文字
        self._dialog_txt_system.draw(surface)
        #背景音乐
        self.play_bgm(-1)
        #按钮
        buttonEvent = self._buttons_mananger.draw(surface,self._dialog_txt_system.isHidden)
        #按键判定
        leftClick = False
        for event in controller.events:
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.JOYBUTTONDOWN:
                if event.button == 1 or controller.joystick.get_button(0) == 1:
                    if buttonEvent == "hide" and not self._is_showing_history:
                        self._dialog_txt_system.hideSwitch()
                    #如果接来下没有文档了或者玩家按到了跳过按钮
                    elif buttonEvent == "skip" and not self._is_showing_history:
                        #淡出
                        self.fadeOut(surface)
                        self.stop()
                    elif buttonEvent == "auto" and not self._is_showing_history:
                        self._buttons_mananger.autoModeSwitch()
                        self._dialog_txt_system.autoMode = self._buttons_mananger.autoMode
                    elif self.history_back.is_hover() and self._is_showing_history is True:
                        self._is_showing_history = False
                        self._history_surface = None
                    elif buttonEvent == "history" and not self._is_showing_history:
                        self._is_showing_history = True
                    #如果所有行都没有播出，则播出所有行
                    elif not self._dialog_txt_system.is_all_played():
                        self._dialog_txt_system.play_all()
                    else:
                        leftClick = True
                elif event.button == 4 and self._history_surface_local_y<0:
                    self._history_surface = None
                    self._history_surface_local_y += display.get_height()*0.1
                elif event.button == 5:
                    self._history_surface = None
                    self._history_surface_local_y -= display.get_height()*0.1
                #返回上一个对话场景（在被允许的情况下）
                elif event.button == 3 or controller.joystick.get_button(1) == 1:
                    if self.dialogContent[self._dialog_id]["last_dialog_id"] is not None:
                        self.__update_scene(self.dialogContent[self._dialog_id]["last_dialog_id"])
                    else:
                        pass
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                progress_saved_text = ImageSurface(
                    self._dialog_txt_system.FONT.render(get_lang("Global","progress_has_been_saved"),get_fontMode(),(255, 255, 255)),0,0
                    )
                progress_saved_text.set_alpha(0)
                self.pause_menu.hidden = False
                display.flip()
                while not self.pause_menu.hidden:
                    display.flip()
                    self.pause_menu.draw(surface)
                    result = self.pause_menu.get_button_clicked()
                    if result == "break":
                        get_option_menu().hidden = True
                        self.pause_menu.hidden = True
                    elif result == "save":
                        self.save_progress()
                        progress_saved_text.set_alpha(255)
                    elif result == "option_menu":
                        get_option_menu().hidden = False
                    elif result == "back_to_mainMenu":
                        get_option_menu().hidden = True
                        self.fadeOut(surface)
                        self.pause_menu.hidden = True
                        self.stop()
                    #展示设置UI
                    get_option_menu().draw(surface)
                    #更新音量
                    if get_option_menu().need_update is True:
                        self.__update_sound_volume()
                        get_option_menu().need_update = False
                    progress_saved_text.drawOnTheCenterOf(surface)
                    progress_saved_text.fade_out(5)
                del progress_saved_text
                self.pause_menu.screenshot = None
        #显示选项
        if self._dialog_txt_system.is_all_played() and self.dialogContent[self._dialog_id]["next_dialog_id"] is not None and self.dialogContent[self._dialog_id]["next_dialog_id"]["type"] == "option":
            optionBox_y_base = (display.get_height()*3/4-(len(self.dialogContent[self._dialog_id]["next_dialog_id"]["target"]))*2*display.get_width()*0.03)/4
            optionBox_height = int(display.get_width()*0.05)
            nextDialogId = None
            i=0
            for i in range(len(self.dialogContent[self._dialog_id]["next_dialog_id"]["target"])):
                option_txt = self._dialog_txt_system.fontRender(self.dialogContent[self._dialog_id]["next_dialog_id"]["target"][i]["txt"],findColorRGBA("white"))
                optionBox_width = int(option_txt.get_width()+display.get_width()*0.05) 
                optionBox_x = (display.get_width()-optionBox_width)/2
                optionBox_y = (i+1)*2*display.get_width()*0.03+optionBox_y_base
                mouse_x,mouse_y = controller.get_mouse_pos()
                if 0 < mouse_x-optionBox_x < optionBox_width and 0 < mouse_y-optionBox_y < optionBox_height:
                    self._option_box_selected_surface.set_size(optionBox_width,optionBox_height)
                    self._option_box_selected_surface.set_pos(optionBox_x,optionBox_y)
                    self._option_box_selected_surface.draw(surface)
                    displayInCenter(option_txt,self._option_box_selected_surface,self._option_box_selected_surface.x,self._option_box_selected_surface.y,surface)
                    #保存选取的选项
                    if leftClick and not self._is_showing_history: nextDialogId = self.dialogContent[self._dialog_id]["next_dialog_id"]["target"][i]["id"]
                else:
                    self._option_box_surface.set_size(optionBox_width,optionBox_height)
                    self._option_box_surface.set_pos(optionBox_x,optionBox_y)
                    self._option_box_surface.draw(surface)
                    displayInCenter(option_txt,self._option_box_surface,self._option_box_surface.x,self._option_box_surface.y,surface)
            if nextDialogId is not None:
                self.dialog_options[self._dialog_id] = {"id":i,"target":nextDialogId}
                #更新场景
                self.__update_scene(nextDialogId)
                leftClick = False
        #展示历史
        if self._is_showing_history:
            if self._history_surface is None:
                self._history_surface = pygame.Surface(display.get_size(),flags=pygame.SRCALPHA).convert_alpha()
                pygame.draw.rect(self._history_surface,(0,0,0),((0,0),display.get_size()))
                self._history_surface.set_alpha(150)
                dialogIdTemp = "head"
                local_y = self._history_surface_local_y
                while dialogIdTemp is not None:
                    if self.dialogContent[dialogIdTemp]["narrator"] is not None:
                        narratorTemp = self._dialog_txt_system.fontRender(self.dialogContent[dialogIdTemp]["narrator"]+': ["',(255, 255, 255))
                        self._history_surface.blit(narratorTemp,(display.get_width()*0.15-narratorTemp.get_width(),display.get_height()*0.1+local_y))
                    for i in range(len(self.dialogContent[dialogIdTemp]["content"])):
                        txt = self.dialogContent[dialogIdTemp]["content"][i]
                        txt += '"]' if i == len(self.dialogContent[dialogIdTemp]["content"])-1 and self.dialogContent[dialogIdTemp]["narrator"] is not None else ""
                        self._history_surface.blit(self._dialog_txt_system.fontRender(txt,(255, 255, 255)),(display.get_width()*0.15,display.get_height()*0.1+local_y))
                        local_y+=self._dialog_txt_system.FONTSIZE*1.5
                    if dialogIdTemp != self._dialog_id:
                        if self.dialogContent[dialogIdTemp]["next_dialog_id"]["type"] == "default" or self.dialogContent[dialogIdTemp]["next_dialog_id"]["type"] == "changeScene":
                            dialogIdTemp = self.dialogContent[dialogIdTemp]["next_dialog_id"]["target"]
                        elif self.dialogContent[dialogIdTemp]["next_dialog_id"]["type"] == "option":
                            narratorTemp = self._dialog_txt_system.fontRender(self._buttons_mananger.choiceTxt+" - ",(0,191,255))
                            self._history_surface.blit(narratorTemp,(display.get_width()*0.15-narratorTemp.get_width(),display.get_height()*0.1+local_y))
                            self._history_surface.blit(self._dialog_txt_system.fontRender(str(self.dialog_options[dialogIdTemp]["target"]),(0,191,255)),(display.get_width()*0.15,display.get_height()*0.1+local_y))
                            local_y+=self._dialog_txt_system.FONTSIZE*1.5
                            dialogIdTemp = self.dialog_options[dialogIdTemp]["target"]
                        else:
                            dialogIdTemp = None
                    else:
                        dialogIdTemp = None
            surface.blit(self._history_surface,(0,0))
            self.history_back.draw(surface)
            self.history_back.is_hover()
        elif self._dialog_txt_system.needUpdate() or leftClick:
            if self.dialogContent[self._dialog_id]["next_dialog_id"] is None or self.dialogContent[self._dialog_id]["next_dialog_id"]["target"] is None:
                self.fadeOut(surface)
                self.stop()
            elif self.dialogContent[self._dialog_id]["next_dialog_id"]["type"] == "default":
                self.__update_scene(self.dialogContent[self._dialog_id]["next_dialog_id"]["target"])
            #如果是需要播放过程动画
            elif self.dialogContent[self._dialog_id]["next_dialog_id"]["type"] == "cutscene":
                self.fadeOut(surface)
                self.stop()
                cutscene(surface,os.path.join(self._dynamic_background_folder_path,self.dialogContent[self._dialog_id]["next_dialog_id"]["target"]))
            #如果是切换场景
            elif self.dialogContent[self._dialog_id]["next_dialog_id"]["type"] == "changeScene":
                self.fadeOut(surface)
                pygame.time.wait(2000)
                #更新场景
                self.__update_scene(self.dialogContent[self._dialog_id]["next_dialog_id"]["target"])
                self._dialog_txt_system.resetDialogueboxData()
                self.fadeIn(surface)

#对话制作器
class DialogEditor(AbstractDialogSystem):
    def __init__(self, chapterType:str, chapterId:int, part:str=None, project_name:str=None):
        #初始化
        super().__init__()
        self._initialize(chapterType,chapterId,project_name)
        self.folder_for_save_file,self.name_for_save_file = os.path.split(self.get_dialog_file_location(get_setting("Language")))
        #文字
        self.FONTSIZE:int = int(display.get_width()*0.015)
        self.FONT = createFont(self.FONTSIZE)
        #对话框
        self._dialogue_box_image = loadImage(os.path.join(DIALOG_UI_PATH,"dialoguebox.png"),(display.get_width()*0.13,display.get_height()*0.65),display.get_width()*0.74,display.get_height()/4)
        self.narrator = SingleLineInputBox(display.get_width()*0.2,self._dialogue_box_image.y+self.FONTSIZE,self.FONTSIZE,"white")
        self.content = MultipleLinesInputBox(display.get_width()*0.2,display.get_height()*0.73,self.FONTSIZE,"white")
        #将npc立绘系统设置为开发者模式
        self._npc_manager.dev_mode = True
        #加载容器
        container_width = int(display.get_width()*0.2)
        self.UIContainerRightImage = loadImg(os.path.join(DIALOG_UI_PATH,"container.png"),(container_width,display.get_height()))
        #背景容器
        self.UIContainerRight_bg = SurfaceContainerWithScrollbar(
            None, int(container_width*0.075), int(display.get_height()*0.1), int(container_width*0.85), int(display.get_height()*0.85), "vertical"
            )
        self.UIContainerRight_bg.set_scroll_bar_pos("right")
        #加载背景图片
        self.background_deselect = loadImg(os.path.join(DIALOG_UI_PATH,"deselect.png"))
        self.UIContainerRight_bg.set("current_select",None)
        for imgPath in glob(os.path.join(self._background_image_folder_path,"*")):
            self.UIContainerRight_bg.set(os.path.basename(imgPath),loadImg(imgPath,(container_width*0.8,None)))
        self.UIContainerRight_bg.distance_between_item = int(display.get_height()*0.02)
        self.__current_select_bg_name = None
        self.__current_select_bg_copy = None
        #npc立绘容器
        self.UIContainerRight_npc = SurfaceContainerWithScrollbar(
            None, int(container_width*0.075), int(display.get_height()*0.1), int(container_width*0.85), int(display.get_height()*0.85), "vertical"
            )
        self.UIContainerRight_npc.set_scroll_bar_pos("right")
        #加载npc立绘
        for imgPath in glob(os.path.join(self._npc_manager.image_folder_path,"*")):
            self.UIContainerRight_npc.set(os.path.basename(imgPath),loadImg(imgPath,(container_width*0.8,None)))
        self.UIContainerRight_npc.hidden = True
        self.UIContainerRight_npc.distance_between_item = 0
        #从配置文件中加载数据
        self.__loadDialogData(part)
        #容器按钮
        button_width = int(display.get_width()*0.04)
        self.UIContainerRightButton = loadDynamicImage(
            os.path.join(DIALOG_UI_PATH,"container_button.png"),
            (display.get_width()-button_width,display.get_height()*0.4),
            (display.get_width()-button_width-container_width,display.get_height()*0.4),
            (container_width/10,0),button_width,int(display.get_height()*0.2)
            )
        self.UIContainerRightButton.rotate(90)
        #UI按钮
        CONFIG = get_lang("DialogCreator")
        button_y = int(display.get_height()*0.03)
        #控制容器转换的按钮
        self.button_select_background = ButtonWithFadeInOut(
            os.path.join(DIALOG_UI_PATH,"menu.png"),CONFIG["background"],"black",100,0,button_y*2,button_width/2
            )
        self.button_select_npc = ButtonWithFadeInOut(
            os.path.join(DIALOG_UI_PATH,"menu.png"),CONFIG["npc"],"black",100,0,button_y*2,button_width/2
            )
        panding:int = int((container_width-self.button_select_background.get_width()-self.button_select_npc.get_width())/3)
        self.button_select_background.set_left(panding)
        self.button_select_npc.set_left(self.button_select_background.get_right()+panding)
        #页面右上方的一排按钮
        self.buttonsUI = {
            "save": ButtonWithDes(os.path.join(DIALOG_UI_PATH,"save.png"),button_width*7.25,button_y,button_width,button_width,get_lang("Global","save")),
            "reload": ButtonWithDes(os.path.join(DIALOG_UI_PATH,"reload.png"),button_width*6,button_y,button_width,button_width,CONFIG["reload"]),
            "add": ButtonWithDes(os.path.join(DIALOG_UI_PATH,"add.png"),button_width*4.75,button_y,button_width,button_width,CONFIG["add"]),
            "next": ButtonWithDes(os.path.join(DIALOG_UI_PATH,"dialog_skip.png"),button_width*4.75,button_y,button_width,button_width,CONFIG["next"]),
            "previous": ButtonWithDes(os.path.join(DIALOG_UI_PATH,"previous.png"),button_width*3.5,button_y,button_width,button_width,CONFIG["previous"]),
            "delete": ButtonWithDes(os.path.join(DIALOG_UI_PATH,"delete.png"),button_width*2.25,button_y,button_width,button_width,CONFIG["delete"]),
            "back": ButtonWithDes(os.path.join(DIALOG_UI_PATH,"back.png"),button_width,button_y,button_width,button_width,CONFIG["back"])
        }
        self.please_enter_content = CONFIG["please_enter_content"]
        self.please_enter_name = CONFIG["please_enter_name"]
        self.removeNpcButton = fontRender(CONFIG["removeNpc"],"black",self.FONTSIZE)
        surfaceTmp = pygame.Surface((self.removeNpcButton.get_width()*1.2,self.FONTSIZE*1.2),flags=pygame.SRCALPHA).convert()
        pygame.draw.rect(surfaceTmp,(255,255,255),(0,0, surfaceTmp.get_width(),surfaceTmp.get_height()))
        surfaceTmp.blit(self.removeNpcButton,(self.removeNpcButton.get_width()*0.1,0))
        self.removeNpcButton = surfaceTmp
        self.smart_add_mode = False
        #未保存离开时的警告
        self.__no_save_warning = LeaveWithoutSavingWarning(
            os.path.join(DIALOG_UI_PATH,"container.png"),0,0,display.get_width()/2,display.get_height()/4
            )
        self.__no_save_warning.set_center(display.get_width()/2,display.get_height()/2)
    @property
    def part(self) -> str: return self.parts[self.partId]
    #返回需要保存数据
    def _get_data_need_to_save(self) -> dict:
        original_data:dict = loadConfig(self.get_dialog_file_location(get_setting("Language")))
        original_data["dialogs"] = self.__slipt_the_stuff_need_save()
        return original_data
    #更新背景选项栏
    def _update_background_image(self, image_name:str) -> None:
        super()._update_background_image(image_name)
        if image_name is not None:
            if self.__current_select_bg_name is not None:
                self.UIContainerRight_bg.set("current_select",self.__current_select_bg_copy)
                self.UIContainerRight_bg.swap("current_select",self.__current_select_bg_name)
            self.UIContainerRight_bg.swap("current_select",image_name)
            self.__current_select_bg_name = image_name
            current_select_bg = self.UIContainerRight_bg.get("current_select")
            self.__current_select_bg_copy = current_select_bg.copy()
            current_select_bg.blit(resizeImg(self.background_deselect,current_select_bg.get_size()),(0,0))
        else:
            self.UIContainerRight_bg.set(self.__current_select_bg_name,self.__current_select_bg_copy)
            self.UIContainerRight_bg.set("current_select",None)
            self.__current_select_bg_name = None
            self.__current_select_bg_copy = None
    #读取章节信息
    def __loadDialogData(self, part:str) -> None:
        self.dialogData = loadConfig(self.get_dialog_file_location(get_setting("Language")),"dialogs")
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
            default_lang_of_dialog:str = self.get_default_lang()
            #如果不是默认主语言
            if default_lang_of_dialog != get_setting("Language"):
                self.isDefault = False
                #读取原始数据
                self.dialogData_default = loadConfig(self.get_dialog_file_location(default_lang_of_dialog),"dialogs")
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
        self.__update_scene(self._dialog_id)
    #分离需要保存的数据
    def __slipt_the_stuff_need_save(self) -> dict:
        data_need_save:dict = deepcopy(self.dialogData)
        data_need_save[self.part][self._dialog_id]["narrator"] = self.narrator.get_text()
        data_need_save[self.part][self._dialog_id]["content"] = self.content.get_text()
        if not self.isDefault:
            #移除掉相似的内容
            for part in self.dialogData_default:
                for dialogId,defaultDialogData in self.dialogData_default[part].items():
                    if dialogId in data_need_save[part]:
                        for dataType in defaultDialogData:
                            if data_need_save[part][dialogId][dataType] == defaultDialogData[dataType]:
                                del data_need_save[part][dialogId][dataType]
                        if len(data_need_save[part][dialogId]) == 0: del data_need_save[part][dialogId]
        return data_need_save
    #检查是否有任何改动
    def __no_changes_were_made(self) -> bool:
        return loadConfig(self.get_dialog_file_location(get_setting("Language")),"dialogs") == self.__slipt_the_stuff_need_save()
    #更新场景
    def __update_scene(self, theNextDialogId:Union[str,int]) -> None:
        if theNextDialogId in self.dialogData[self.part]:
            self._dialog_id = theNextDialogId
            #更新立绘和背景
            self._npc_manager.update(self.dialogData[self.part][self._dialog_id]["characters_img"])
            self._update_background_image(self.dialogData[self.part][self._dialog_id]["background_img"])
            #更新对话框
            self.narrator.set_text(self.dialogData[self.part][self._dialog_id]["narrator"])
            self.content.set_text(self.dialogData[self.part][self._dialog_id]["content"])
        elif self.smart_add_mode:
            self.__add_dialog(theNextDialogId)
        else:
            throwException("error","Cannot find the dialog with id '{}' in the data dictionary.".format(theNextDialogId))
    #添加新的对话
    def __add_dialog(self, dialogId:Union[str,int]) -> None:
        self.dialogData[self.part][dialogId] = {
            "background_img": self.dialogData[self.part][self._dialog_id]["background_img"],
            "background_music": self.dialogData[self.part][self._dialog_id]["background_music"],
            "characters_img": [],
            "content": [self.please_enter_content],
            "last_dialog_id": self._dialog_id,
            "narrator": self.please_enter_name,
            "next_dialog_id": None
        }
        self.dialogData[self.part][self._dialog_id]["next_dialog_id"] = {"target":dialogId,"type":"default"}
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
            self.save_progress()
    #获取上一个对话的ID
    def __get_last_id(self) -> Union[str,int,None]:
        if "last_dialog_id" in self.dialogData[self.part][self._dialog_id] and self.dialogData[self.part][self._dialog_id]["last_dialog_id"] is not None:
            return self.dialogData[self.part][self._dialog_id]["last_dialog_id"]
        elif self._dialog_id == "head":
            return None
        else:
            for key,dialogData in self.dialogData[self.part].items():
                if dialogData["next_dialog_id"] is not None:
                    if dialogData["next_dialog_id"]["type"] == "default" and dialogData["next_dialog_id"]["target"] == self._dialog_id:
                        return key
                    elif dialogData["next_dialog_id"]["type"] == "changeScene" and dialogData["next_dialog_id"]["target"] == self._dialog_id:
                        return key
                    elif dialogData["next_dialog_id"]["type"] == "option":
                        for optionChoice in dialogData["next_dialog_id"]["target"]:
                            if optionChoice["id"] == self._dialog_id:
                                return key
            return None
    #获取下一个对话的ID
    def __get_next_id(self, surface:pygame.Surface) -> Union[str,int,None]:
        if "next_dialog_id" in self.dialogData[self.part][self._dialog_id]:
            theNext:dict = self.dialogData[self.part][self._dialog_id]["next_dialog_id"]
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
                        leftClick = False
                        for event in controller.events:
                            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.JOYBUTTONDOWN:
                                leftClick = True
                                break
                        for i in range(len(theNext["target"])):
                            button = theNext["target"][i]
                            option_txt = self.FONT.render(button["txt"],get_fontMode(),findColorRGBA("white"))
                            option_button_width = int(option_txt.get_width()+surface.get_width()*0.05)
                            option_button_x = int((surface.get_width()-option_button_width)/2)
                            option_button_y = int((i+1)*2*surface.get_width()*0.03+optionBox_y_base)
                            mouse_x,mouse_y = controller.get_mouse_pos()
                            if 0 < mouse_x-option_button_x < option_button_width and 0 < mouse_y-option_button_y < option_button_height:
                                self._option_box_selected_surface.set_size(option_button_width,option_button_height)
                                self._option_box_selected_surface.set_pos(option_button_x,option_button_y)
                                self._option_box_selected_surface.draw(surface)
                                displayInCenter(option_txt,self._option_box_selected_surface,self._option_box_selected_surface.x,self._option_box_selected_surface.y,surface)
                                if leftClick: return button["id"]
                            else:
                                self._option_box_surface.set_size(option_button_width,option_button_height)
                                self._option_box_surface.set_pos(option_button_x,option_button_y)
                                self._option_box_surface.draw(surface)
                                displayInCenter(option_txt,self._option_box_surface,self._option_box_surface.x,self._option_box_surface.y,surface)
                        display.flip()
        return None
    def draw(self, surface:pygame.Surface) -> None:
        super().draw(surface)
        #画上对话框
        self._dialogue_box_image.draw(surface)
        if self._npc_manager.npc_get_click is not None: surface.blit(self.removeNpcButton,controller.get_mouse_pos())
        self.narrator.draw(surface)
        if self.narrator.needSave: self.dialogData[self.part][self._dialog_id]["narrator"] = self.narrator.get_text()
        self.content.draw(surface)
        if self.content.needSave:
            self.dialogData[self.part][self._dialog_id]["content"] = self.content.get_text()
        #初始化数值
        buttonHovered = None
        theNextDialogId = self.dialogData[self.part][self._dialog_id]["next_dialog_id"]
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
        leftClick:bool = False
        for event in controller.events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.UIContainerRightButton.is_hover():
                        self.UIContainerRightButton.switch()
                        self.UIContainerRightButton.flip(True,False)
                    #退出
                    elif buttonHovered == "back":
                        if self.__no_changes_were_made() is True:
                            self.stop()
                            break
                        else:
                            self.__no_save_warning.hidden = False
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
                                    if optionChoice["id"] == self._dialog_id:
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
                            needDeleteId = self._dialog_id
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
                        self.save_progress()
                    elif buttonHovered == "reload":
                        self.__loadDialogData(self.part)
                    else:
                        leftClick = True
                #鼠标中键 -- 切换场景
                elif event.button == 2:
                    self._dialog_id += 1
                    if self._dialog_id == len(self.parts):
                        self._dialog_id = 0
                    self.__update_scene("head")
                #鼠标右键
                elif event.button == 3:
                    #移除角色立绘
                    if self._npc_manager.npc_get_click is not None:
                        self.dialogData[self.part][self._dialog_id]["characters_img"].remove(self._npc_manager.npc_get_click)
                        self._npc_manager.update(self.dialogData[self.part][self._dialog_id]["characters_img"])
                        self._npc_manager.npc_get_click = None
        
        #画上右侧菜单的按钮
        self.UIContainerRightButton.draw(surface)
        #画上右侧菜单
        if self.UIContainerRightButton.right < display.get_width():
            surface.blit(self.UIContainerRightImage,(self.UIContainerRightButton.right,0))
            self.UIContainerRight_bg.display(surface,(self.UIContainerRightButton.right,0))
            self.UIContainerRight_npc.display(surface,(self.UIContainerRightButton.right,0))
            #self.UIContainerRight_bg.draw_outline(surface,(self.UIContainerRightButton.right,0))
            #self.UIContainerRight_npc.draw_outline(surface,(self.UIContainerRightButton.right,0))
            #检测按钮
            if isHover(self.button_select_background,local_x=self.UIContainerRightButton.right) and leftClick is True:
                self.UIContainerRight_bg.hidden = False
                self.UIContainerRight_npc.hidden = True
                leftClick = False
            if isHover(self.button_select_npc,local_x=self.UIContainerRightButton.right) and leftClick is True:
                self.UIContainerRight_bg.hidden = True
                self.UIContainerRight_npc.hidden = False
                leftClick = False
            #画出按钮
            self.button_select_background.display(surface,(self.UIContainerRightButton.right,0))
            self.button_select_npc.display(surface,(self.UIContainerRightButton.right,0))
            #检测是否有物品被选中需要更新
            if leftClick is True:
                if not self.UIContainerRight_bg.hidden:
                    imgName = self.UIContainerRight_bg.current_hovered_item
                    if imgName is not None:
                        if imgName != "current_select":
                            self.dialogData[self.part][self._dialog_id]["background_img"] = imgName
                            self._update_background_image(imgName)
                        else:
                            self.dialogData[self.part][self._dialog_id]["background_img"] = None
                            self._update_background_image(None)
                elif not self.UIContainerRight_npc.hidden:
                    imgName = self.UIContainerRight_npc.current_hovered_item
                    if imgName is not None:
                        if self.dialogData[self.part][self._dialog_id]["characters_img"] is None:
                            self.dialogData[self.part][self._dialog_id]["characters_img"] = []
                        if len(self.dialogData[self.part][self._dialog_id]["characters_img"]) < 2:
                            self.dialogData[self.part][self._dialog_id]["characters_img"].append(imgName)
                            self._npc_manager.update(self.dialogData[self.part][self._dialog_id]["characters_img"])
        
        #未保存离开时的警告
        self.__no_save_warning.draw(surface)
        if leftClick is True and self.__no_save_warning.button_hovered != "":
            #保存并离开
            if self.__no_save_warning.button_hovered == "save":
                self.save_progress()
                self.stop()
            #取消
            elif self.__no_save_warning.button_hovered == "cancel":
                self.__no_save_warning.hidden = True
            #不保存并离开
            elif self.__no_save_warning.button_hovered == "dont_save":
                self.stop()