from .script import *


# 视觉小说系统接口
class AbstractDialogSystem(AbstractGameSystem, metaclass=ABCMeta):
    def __init__(self) -> None:
        super().__init__()
        self._content: DialogContentManager = DialogContentManager()
        # 黑色Void帘幕
        self._black_bg = StaticImage(Surfaces.colored(Display.get_size(), Colors.BLACK), 0, 0, Display.get_width(), Display.get_height())
        # 对话文件路径
        self._dialog_folder_path: str = "Data"
        # 背景图片
        self.__background_image_name: Optional[str] = None
        self.__background_image_surface: StaticImage | VideoSurface = self._black_bg.copy()
        # 是否开启自动保存
        self.auto_save: bool = False
        # 是否静音
        self._is_muted: bool = False
        # 选项菜单
        self._dialog_options_container: GameObjectsListContainer = GameObjectsListContainer("<NULL>", 0, 0, 0, 0)
        self._dialog_options_container.set_visible(False)
        # 更新背景音乐音量
        self.set_bgm_volume(Volume.get_background_music() / 100)
        # 文字大小
        self._FONT_SIZE: int = Display.get_width() * 3 // 200
        # 初始化滤镜系统
        CharacterImageManager.init()

    # 获取对话框模块（子类需实现）
    def _get_dialog_box(self) -> AbstractDialogBox:
        return EXCEPTION.fatal("_dialogBox()", 1)

    # 获取对话文件所在的文件夹目录
    def get_dialog_folder_location(self) -> str:
        return (
            os.path.join(self._dialog_folder_path, self._chapter_type)
            if self._project_name is None
            else os.path.join(self._dialog_folder_path, self._chapter_type, self._project_name)
        )

    # 获取对话文件所在的具体路径
    def get_dialog_file_location(self, lang: str = "") -> str:
        if len(lang) == 0:
            lang = Setting.get_language()
        return os.path.join(self.get_dialog_folder_location(), "chapter{0}_dialogs_{1}.{2}".format(self._chapter_id, lang, Config.get_file_type()))

    # 获取对话文件的主语言
    def get_default_lang(self) -> str:
        return str(
            Config.load(os.path.join(self._dialog_folder_path, self._chapter_type, "info.{}".format(Config.get_file_type())), "default_lang")
            if self._project_name is None
            else Config.load(
                os.path.join(self._dialog_folder_path, self._chapter_type, self._project_name, "info.{}".format(Config.get_file_type())), "default_lang"
            )
        )

    # 生产一个新的推荐id
    def generate_a_new_recommended_key(self, index: int = 1) -> str:
        while True:
            newId: str = ("id_0" if index <= 9 else "id_") + str(index)
            if newId in self._content.get_section():
                index += 1
            else:
                return newId

    # 返回需要保存数据
    def _get_data_need_to_save(self) -> dict:
        return self.get_data_of_parent_game_system() | {"dialog_id": self._content.get_id(), "type": self._content.get_part()}

    # 读取存档
    def load_progress(self, _data: dict) -> None:
        self.new(_data["chapter_type"], _data["chapter_id"], _data["type"], _data.get("project_name"), _data.get("dialog_id", "head"))

    # 新读取章节
    def new(self, chapterType: str, chapterId: int, part: str, projectName: Optional[str] = None, dialogId: str = "head") -> None:
        # 初始化关键参数
        self._initialize(chapterType, chapterId, projectName)
        # 对白id
        self._content.set_id(dialogId)
        # 播放的部分
        self._content.set_part(part)
        # 转换所有文件夹内的linpg自定义的raw脚本
        for script_file in glob(os.path.join(self.get_dialog_folder_location(), "*.linpg.script")):
            ScriptConverter().compile(script_file, self.get_dialog_folder_location())
        # 根据已有参数载入数据
        self._load_content()

    # 载入数据
    def _load_content(self) -> None:
        # 读取目标对话文件的数据
        if os.path.exists(self.get_dialog_file_location()):
            # 获取目标对话数据
            dialogData_t: dict = dict(Config.load(self.get_dialog_file_location(), "dialogs", self._content.get_part()))
            # 如果该dialog文件是另一个语言dialog文件的子类
            if (default_lang_of_dialog := self.get_default_lang()) != Setting.get_language():
                self._content.set_section(dict(Config.load(self.get_dialog_file_location(default_lang_of_dialog), "dialogs", self._content.get_part())))
                for key, values in dialogData_t.items():
                    self._content.get_dialog(_id=key).update(values)
            else:
                self._content.set_section(dialogData_t)
        else:
            self._content.set_section(dict(Config.load(self.get_dialog_file_location(self.get_default_lang()), "dialogs", self._content.get_part())))
        # 确认dialog数据合法
        if len(self._content.get_section()) == 0:
            EXCEPTION.fatal('The selected dialog dict "{}" has no content inside.'.format(self._content.get_part()))
        elif "head" not in self._content.get_section():
            EXCEPTION.fatal('You need to set up a "head" for the selected dialog "{}".'.format(self._content.get_part()))
        # 将数据载入刚初始化的模块中
        self._update_scene(self._content.get_id())

    # 更新背景图片
    def _update_background_image(self, image_name: Optional[str]) -> None:
        if self.__background_image_name != image_name:
            # 更新背景的名称
            self.__background_image_name = image_name
            # 如果背景是视频，则应该停止，以防止内存泄漏
            if isinstance(self.__background_image_surface, VideoSurface):
                self.__background_image_surface.stop()
            # 更新背景的图片数据
            if self.__background_image_name is not None:
                # 尝试加载图片式的背景
                if os.path.exists((img_path := Specification.get_directory("background_image", self.__background_image_name))):
                    self.__background_image_surface = StaticImage(img_path, 0, 0)
                    self.__background_image_surface.disable_cropping()
                # 如果在背景图片的文件夹里找不到对应的图片，则查看是否是视频文件
                elif os.path.exists(_path := Specification.get_directory("movie", self.__background_image_name)):
                    self.__background_image_surface = VideoSurface(_path, with_audio=False)
                else:
                    EXCEPTION.fatal("Cannot find a background image or video file called '{}'.".format(self.__background_image_name))
            else:
                self.__background_image_surface = self._black_bg.copy()

    # 更新场景
    def _update_scene(self, dialog_id: str) -> None:
        # 更新dialogId
        self._content.set_id(dialog_id)
        # 更新立绘和背景
        CharacterImageManager.update(self._content.current.character_images)
        self._update_background_image(self._content.current.background_image)
        # 更新对话框
        self._get_dialog_box().update(self._content.current.narrator, self._content.current.contents)
        # 更新背景音乐
        if self._content.current.background_music is not None:
            self.set_bgm(Specification.get_directory("music", self._content.current.background_music))
        else:
            self.unload_bgm()
        # 隐藏选项菜单
        self._dialog_options_container.clear()
        self._dialog_options_container.set_visible(False)

    # 更新语言
    def update_language(self) -> None:
        super().update_language()
        self._load_content()

    # 停止播放
    def stop(self) -> None:
        # 如果背景是多线程的VideoSurface，则应该退出占用
        if isinstance(self.__background_image_surface, VideoSurface):
            self.__background_image_surface.stop()
        # 释放立绘渲染系统占用的内存
        CharacterImageManager.unload()
        # 设置停止播放
        super().stop()

    # 将背景图片画到surface上
    def display_background_image(self, _surface: ImageSurface) -> None:
        if self.__background_image_surface is not None:
            if isinstance(self.__background_image_surface, StaticImage):
                self.__background_image_surface.set_size(_surface.get_width(), _surface.get_height())
            self.__background_image_surface.draw(_surface)

    def _get_dialog_options_container_ready(self) -> None:
        self._dialog_options_container.clear()
        _next_targets: Optional[str | list] = self._content.current.next.get("target")
        if isinstance(_next_targets, list):
            optionBox_y_base: int = Display.get_height() * 3 // 16 - len(_next_targets) * self._FONT_SIZE
            for i in range(len(_next_targets)):
                optionButton: Button = Button.load("<&ui>option.png", (0, 0), (0, 0))
                optionButton.set_hover_img(Images.quickly_load("<&ui>option_selected.png"))
                optionButton.set_auto_resize(True)
                optionButton.set_text(ButtonComponent.text(str(_next_targets[i]["text"]), self._FONT_SIZE, Colors.WHITE))
                optionButton.set_pos((Display.get_width() - optionButton.get_width()) / 2, (i + 1) * 4 * self._FONT_SIZE + optionBox_y_base)
                self._dialog_options_container.append(optionButton)
            self._dialog_options_container.set_visible(True)

    # 把基础内容画到surface上
    def draw(self, _surface: ImageSurface) -> None:
        # 检测章节是否初始化
        if self._chapter_id is None:
            raise EXCEPTION.fatal("The dialog has not been initialized!")
        # 展示背景图片和npc立绘
        self.display_background_image(_surface)
        CharacterImageManager.draw(_surface)
        self._get_dialog_box().draw(_surface)
        # 如果不处于静音状态
        if not self._is_muted:
            # 播放背景音乐
            self.play_bgm()
