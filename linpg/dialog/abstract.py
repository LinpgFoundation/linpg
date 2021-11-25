from .character import *

# 视觉小说系统接口
class AbstractDialogSystem(AbstractGameSystem):
    def __init__(self):
        super().__init__()
        # 存储视觉小说数据的参数
        self._dialog_data: dict = {}
        # 当前对话的id
        self._dialog_id: str = "head"
        # 加载对话的背景图片模块
        self._npc_manager = CharacterImageManager()
        # 黑色Void帘幕
        black_surface_t = new_surface(Display.get_size())
        black_surface_t.fill(Color.BLACK)
        self._black_bg = StaticImage(black_surface_t, 0, 0, black_surface_t.get_width(), black_surface_t.get_height())
        # 加载对话框系统
        self._dialog_txt_system = DialogBox(int(Display.get_width() * 0.015))
        # UI按钮
        self._buttons_mananger = None
        # 对话文件路径
        self._dialog_folder_path: str = "Data"
        # 背景图片路径
        self._background_image_folder_path: str = "Assets/image/dialog_background"
        # 背景图片
        self.__background_image_name = None
        self.__background_image_surface = self._black_bg.copy()
        # 是否开启自动保存
        self.auto_save: bool = False
        # 是否静音
        self._is_muted: bool = False
        # 指向当前对话的数据的指针
        self._current_dialog_content: dict = {}
        # 初始化音量
        self._update_sound_volume()
        # 选项菜单
        self._dialog_options_container = GameObjectsListContainer(None, 0, 0, 0, 0)
        self._dialog_options_container.set_visible(False)

    # 获取对话文件所在的具体路径
    def get_dialog_file_location(self, lang: str = "") -> str:
        if len(lang) == 0:
            lang = Setting.language
        return (
            os.path.join(
                self._dialog_folder_path, self._chapter_type, "chapter{0}_dialogs_{1}.yaml".format(self._chapter_id, lang)
            )
            if self._project_name is None
            else os.path.join(
                self._dialog_folder_path,
                self._chapter_type,
                self._project_name,
                "chapter{0}_dialogs_{1}.yaml".format(self._chapter_id, lang),
            )
        )

    # 获取对话文件的主语言
    def get_default_lang(self) -> str:
        return (
            Config.load(os.path.join(self._dialog_folder_path, self._chapter_type, "info.yaml"), "default_lang")
            if self._project_name is None
            else Config.load(
                os.path.join(self._dialog_folder_path, self._chapter_type, self._project_name, "info.yaml"), "default_lang"
            )
        )

    # 获取下一个dialog node的类型
    def get_next_dialog_type(self) -> str:
        return (
            self._current_dialog_content["next_dialog_id"]["type"]
            if self._current_dialog_content["next_dialog_id"] is not None
            else None
        )

    # 生产一个新的推荐id
    def generate_a_new_recommended_key(self, index: int = 1) -> str:
        while True:
            if index <= 9:
                if (newId := "id_00" + str(index)) not in self.dialog_content:
                    return newId
            elif index <= 99:
                if (newId := "id_0" + str(index)) not in self.dialog_content:
                    return newId
            else:
                if (newId := "id_" + str(index)) not in self.dialog_content:
                    return newId
            index += 1

    # 返回需要保存数据
    def _get_data_need_to_save(self) -> dict:
        return {
            **self.get_data_of_parent_game_system(),
            **{"dialog_id": self._dialog_id, "dialog_options": self._dialog_options, "type": self._part},
        }

    @property
    def dialog_content(self) -> dict:
        return self._dialog_data[self._part]

    # 获取当前对话的信息
    def __get_current_dialog_content(self, safe_mode: bool = False) -> dict:
        currentDialogContent: dict = self.dialog_content[self._dialog_id]
        # 检测是否缺少关键key
        if safe_mode is True:
            for key in ("characters_img", "background_img", "narrator", "content"):
                if key not in currentDialogContent:
                    EXCEPTION.fatal(
                        'Cannot find critical key "{0}" in part "{1}" with id "{2}".'.format(
                            key, self._part, self._dialog_id
                        )
                    )
        return currentDialogContent

    # 检测当前对话是否带有合法的下一个对话对象的id
    def does_current_dialog_have_next_dialog(self) -> bool:
        return (
            "next_dialog_id" in self._current_dialog_content
            and self._current_dialog_content["next_dialog_id"] is not None
            and len(self._current_dialog_content["next_dialog_id"]) > 0
        )

    # 初始化关键参数
    def _initialize(
        self,
        chapterType: str,
        chapterId: int,
        part: str,
        projectName: str,
        dialogId: str = "head",
        dialog_options: dict = {},
    ) -> None:
        super()._initialize(chapterType, chapterId, projectName)
        # 对白id
        self._dialog_id = dialogId
        # 玩家做出的选项
        self._dialog_options = dialog_options
        # 播放的部分
        self._part = part

    # 载入数据
    def _load_content(self) -> None:
        # 读取目标对话文件的数据
        if os.path.exists(self.get_dialog_file_location()):
            # 获取目标对话数据
            dialogData_t: dict = dict(Config.load(self.get_dialog_file_location(), "dialogs", self._part))
            # 如果该dialog文件是另一个语言dialog文件的子类
            if (default_lang_of_dialog := self.get_default_lang()) != Setting.language:
                self._dialog_data[self._part] = dict(
                    Config.load(self.get_dialog_file_location(default_lang_of_dialog), "dialogs", self._part)
                )
                for key, values in dialogData_t.items():
                    self._dialog_data[self._part][key].update(values)
            else:
                self._dialog_data[self._part] = dialogData_t
        else:
            self._dialog_data[self._part] = dict(
                Config.load(self.get_dialog_file_location(self.get_default_lang()), "dialogs", self._part)
            )
        # 确认dialog数据合法
        if len(self.dialog_content) == 0:
            EXCEPTION.fatal('The selected dialog dict "{}" has no content inside.'.format(self._part))
        elif "head" not in self.dialog_content:
            EXCEPTION.fatal('You need to set up a "head" for the selected dialog "{}".'.format(self._part))
        # 将数据载入刚初始化的模块中
        self._update_scene(self._dialog_id)
        self._dialog_txt_system.reset()

    # 更新背景图片
    def _update_background_image(self, image_name: str) -> None:
        if self.__background_image_name != image_name:
            # 更新背景的名称
            self.__background_image_name = image_name
            # 如果背景是视频，则应该停止，以防止内存泄漏
            if isinstance(self.__background_image_surface, VideoSurface):
                self.__background_image_surface.stop()
            # 更新背景的图片数据
            if self.__background_image_name is not None:
                if self.__background_image_name != "<transparent>":
                    # 尝试加载图片式的背景
                    if os.path.exists(
                        (img_path := os.path.join(self._background_image_folder_path, self.__background_image_name))
                    ):
                        self.__background_image_surface = StaticImage(img_path, 0, 0)
                    # 如果在背景图片的文件夹里找不到对应的图片，则查看是否是视频文件
                    elif os.path.exists(os.path.join(ASSET.PATH_DICT["movie"], self.__background_image_name)):
                        self.__background_image_surface = VideoSurface(
                            os.path.join(ASSET.PATH_DICT["movie"], self.__background_image_name),
                            with_audio=False,
                        )
                    else:
                        EXCEPTION.fatal(
                            "Cannot find a background image or video file called '{}'.".format(self.__background_image_name)
                        )
                elif self._npc_manager.dev_mode is True:
                    self.__background_image_surface = StaticImage(get_texture_missing_surface(Display.get_size()), 0, 0)
                else:
                    self.__background_image_surface = None
            else:
                self.__background_image_surface = self._black_bg.copy()

    # 更新场景
    def _update_scene(self, dialog_id: str) -> None:
        # 更新dialogId
        self._dialog_id = dialog_id
        # 更新当前对话数据的指针
        self._current_dialog_content = self.__get_current_dialog_content(True)
        # 更新立绘和背景
        self._npc_manager.update(self._current_dialog_content["characters_img"])
        self._update_background_image(self._current_dialog_content["background_img"])
        # 更新对话框
        self._dialog_txt_system.update(self._current_dialog_content["narrator"], self._current_dialog_content["content"])
        # 更新背景音乐
        if (current_bgm := self._current_dialog_content["background_music"]) is not None:
            self.set_bgm(os.path.join(ASSET.PATH_DICT["music"], current_bgm))
        else:
            self.unload_bgm()
        # 隐藏选项菜单
        self._dialog_options_container.clear()
        self._dialog_options_container.set_visible(False)

    # 更新语言
    def updated_language(self) -> None:
        super().updated_language()
        if self._buttons_mananger is not None:
            self._buttons_mananger.initialize()
        self._load_content()

    # 更新音量
    def _update_sound_volume(self) -> None:
        self.set_bgm_volume(Media.volume.background_music / 100)
        self._dialog_txt_system.set_sound_volume(Media.volume.effects / 100)

    # 停止播放
    def stop(self) -> None:
        # 如果背景是多线程的VideoSurface，则应该退出占用
        if isinstance(self.__background_image_surface, VideoSurface):
            self.__background_image_surface.stop()
        # 设置停止播放
        super().stop()

    # 将背景图片画到surface上
    def display_background_image(self, surface: ImageSurface) -> None:
        if self.__background_image_surface is not None:
            if isinstance(self.__background_image_surface, Rect):
                self.__background_image_surface.set_size(surface.get_width(), surface.get_height())
            self.__background_image_surface.draw(surface)

    # 把基础内容画到surface上
    def draw(self, surface: ImageSurface) -> None:
        # 检测章节是否初始化
        if self._chapter_id is None:
            raise EXCEPTION.fatal("The dialog has not been initialized!")
        # 更新当前对话数据的指针
        self._current_dialog_content = self.__get_current_dialog_content()
        # 展示背景图片和npc立绘
        self.display_background_image(surface)
        self._npc_manager.draw(surface)
        self._dialog_txt_system.draw(surface)
        # 如果不处于静音状态
        if not self._is_muted:
            # 播放背景音乐
            self.play_bgm()
