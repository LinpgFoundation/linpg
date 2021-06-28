# cython: language_level=3
from .character import *

#视觉小说系统接口
class AbstractDialogSystem(AbstractGameSystem):
    def __init__(self):
        super().__init__()
        #存储视觉小说数据的参数
        self._dialog_data:dict = {}
        #加载对话的背景图片模块
        self._npc_manager = CharacterImageManager()
        #黑色Void帘幕
        self._black_bg = get_single_color_surface("black")
        #加载对话框系统
        self._dialog_txt_system = DialogBox(int(display.get_width()*0.015))
        #选项栏
        self._option_box_surface = StaticImage(os.path.join(DIALOG_UI_PATH, "option.png"), 0, 0)
        #选项栏-选中
        try:
            self._option_box_selected_surface = StaticImage(os.path.join(DIALOG_UI_PATH, "option_selected.png"), 0, 0)
        except Exception:
            throw_exception(
                "warning",
                "Cannot find or load 'option_selected.png' in '{}' file, 'option.png' will be used instead.".format(DIALOG_UI_PATH)
            )
            self._option_box_selected_surface = self._option_box_surface.copy()
        #UI按钮
        self._buttons_mananger = None
        #暂停菜单
        self.pause_menu = None
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
        #编辑器模式模式
        self.dev_mode:bool = False
        #是否开启自动保存
        self.auto_save:bool = False
    #获取对话文件所在的具体路径
    def get_dialog_file_location(self, lang:str="") -> str:
        if len(lang) == 0: lang = get_setting("Language")
        return os.path.join(
            self._dialog_folder_path, self._chapter_type, "chapter{0}_dialogs_{1}.yaml".format(self._chapter_id, lang)
            ) if self._project_name is None else os.path.join(
                self._dialog_folder_path, self._chapter_type, self._project_name, "chapter{0}_dialogs_{1}.yaml".format(self._chapter_id, lang)
                )
    #获取对话文件的主语言
    def get_default_lang(self) -> str:
        return load_config(os.path.join(self._dialog_folder_path,self._chapter_type,"info.yaml"),"default_lang") if self._project_name is None\
            else load_config(os.path.join(self._dialog_folder_path,self._chapter_type,self._project_name,"info.yaml"),"default_lang")
    #返回需要保存数据
    def _get_data_need_to_save(self) -> dict: return merge_dict(
        self.data_of_parent_game_system, {"dialog_id": self._dialog_id, "dialog_options": self._dialog_options, "type": self._part}
        )
    @property
    def dialog_content(self) -> str: return self._dialog_data[self._part]
    @property
    def current_dialog_content(self) -> dict: return self.get_current_dialog_content()
    #获取当前对话的信息
    def get_current_dialog_content(self, safe_mode:bool=False) -> dict:
        currentDialogContent:dict = self._dialog_data[self._part][self._dialog_id]
        #检测是否缺少关键key
        if safe_mode is True:
            for key in ("characters_img", "background_img", "narrator", "content"):
                try:
                    assert key in currentDialogContent
                except AssertionError:
                    print(currentDialogContent)
                    throw_exception(
                        "error", 'Cannot find critical key "{0}" in part "{1}" with id "{2}".'.format(key, self._part, self._dialog_id)
                        )
        return currentDialogContent
    #初始化关键参数
    def _initialize(
        self, chapterType:str, chapterId:int, part:str, projectName:str, dialogId:Union[str,int]="head", dialog_options:dict={}
        ) -> None:
        super()._initialize(chapterType,chapterId,projectName)
        #对白id
        self._dialog_id = dialogId
        #玩家做出的选项
        self._dialog_options = dialog_options
        #播放的部分
        self._part = part
    #载入数据
    def _load_content(self) -> None:
        #获取该项目的默认语言
        default_lang_of_dialog:str = self.get_default_lang()
        #读取目标对话文件的数据
        if os.path.exists(self.get_dialog_file_location()):
            try:
                dialogDataDict:dict = load_config(self.get_dialog_file_location(), "dialogs", self._part)
                assert isinstance(dialogDataDict, dict)
                #如果该dialog文件是另一个语言dialog文件的子类
                if default_lang_of_dialog != get_setting("Language"):
                    self._dialog_data[self._part] = load_config(self.get_dialog_file_location(default_lang_of_dialog),"dialogs", self._part)
                    try:
                        assert isinstance(self._dialog_data[self._part], dict)
                        for dialog_id in dialogDataDict:
                            if dialog_id in self._dialog_data[self._part]:
                                for key in dialogDataDict[dialog_id]:
                                    self._dialog_data[self._part][dialog_id][key] = dialogDataDict[dialog_id][key]
                            else:
                                self._dialog_data[self._part][dialog_id] = dialogDataDict[dialog_id]
                    except AssertionError:
                        threading(
                            "error",
                            'Cannot load part "{}" from default language dialog! Worst case scenario, it needs to be empty!'
                            .format(self._part)
                            )
                #如果该dialog文件是主语言
                else:
                    self._dialog_data[self._part] = dialogDataDict
            except AssertionError:
                threading("error", 'Cannot load part "{0}" from "{1}"!'.format(self._part, self.get_dialog_file_location()))
        else:
            self._dialog_data[self._part] = load_config(self.get_dialog_file_location(default_lang_of_dialog), "dialogs", self._part)
        #确认dialog数据合法
        if len(self.dialog_content) == 0:
            throw_exception("error", 'The selected dialog dict "{}" has no content inside.'.format(self._part))
        elif "head" not in self.dialog_content:
            throw_exception("error", 'You need to set up a "head" for the selected dialog "{}".'.format(self._part))
        #将数据载入刚初始化的模块中
        self._update_scene(self._dialog_id)
        self._dialog_txt_system.reset()
    #更新背景图片
    def _update_background_image(self, image_name:str) -> None:
        if self.__background_image_name != image_name:
            #更新背景的名称
            self.__background_image_name = image_name
            #如果背景是视频，则应该停止，以防止内存泄漏
            if isinstance(self.__background_image_surface, VedioSurface):
                self.__background_image_surface.stop()
            #更新背景的图片数据
            if self.__background_image_name is not None:
                if self.__background_image_name != "<transparent>":
                    #尝试加载图片式的背景
                    img_path:str = os.path.join(self._background_image_folder_path, self.__background_image_name)
                    if os.path.exists(img_path):
                        self.__background_image_surface = StaticImage(img_path, 0, 0)
                    #如果在背景图片的文件夹里找不到对应的图片，则查看是否是视频文件
                    elif os.path.exists(os.path.join(self._dynamic_background_folder_path,self.__background_image_name)):
                        self.__background_image_surface = VedioSurface(
                            os.path.join(self._dynamic_background_folder_path,self.__background_image_name),
                            display.get_width(),
                            display.get_height()
                            )
                        self.__background_image_surface.start()
                    else:
                        throw_exception("error","Cannot find a background image or video file called '{}'.".format(self.__background_image_name))
                elif self.dev_mode is True:
                    self.__background_image_surface = StaticImage(get_texture_missing_surface(display.get_size()), 0, 0)
                else:
                    self.__background_image_surface = None
            else:
                self.__background_image_surface = self._black_bg.copy()
    #更新场景
    def _update_scene(self, theNextDialogId:Union[str,int]) -> None:
        #更新dialogId
        self._dialog_id = theNextDialogId
        #获取当前对话的内容
        currentDialogContent:dict = self.get_current_dialog_content(True)
        #更新立绘和背景
        self._npc_manager.update(currentDialogContent["characters_img"])
        self._update_background_image(currentDialogContent["background_img"])
        #更新对话框
        self._dialog_txt_system.update(currentDialogContent["narrator"], currentDialogContent["content"])
        #更新背景音乐
        if not self.dev_mode:
            if currentDialogContent["background_music"] is not None:
                self.set_bgm(os.path.join(self._background_music_folder_path,currentDialogContent["background_music"]))
            else:
                self.set_bgm(None)
    #更新语言
    def updated_language(self, surface:ImageSurface) -> None:
        super().updated_language()
        if self.pause_menu is not None: self.pause_menu.initialize(surface)
        if self._buttons_mananger is not None: self._buttons_mananger.initialize()
        self._load_content()
    #更新音量
    def _update_sound_volume(self) -> None:
        self.set_bgm_volume(get_setting("Sound","background_music")/100)
        self._dialog_txt_system.set_sound_volume(get_setting("Sound","sound_effects"))
    #停止播放
    def stop(self) -> None:
        #如果背景是多线程的VedioSurface，则应该退出占用
        if isinstance(self.__background_image_surface,VedioSurface): self.__background_image_surface.stop()
        #设置停止播放
        super().stop()
    #将背景图片画到surface上
    def display_background_image(self, surface:ImageSurface) -> None:
        if self.__background_image_surface is not None:
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
        self._dialog_txt_system.draw(surface)