from .render import *


# 视觉小说系统接口
class AbstractVisualNovelPlayer(AbstractGameSystem, metaclass=ABCMeta):
    def __init__(self) -> None:
        super().__init__()
        self._content: DialoguesManager = DialoguesManager()
        # 黑色Void帘幕
        self._black_bg = StaticImage(
            Surfaces.colored(Display.get_size(), Colors.BLACK), 0, 0, Display.get_width(), Display.get_height()
        )
        # 对话文件路径
        self._dialog_folder_path: str = "Data"
        # 背景图片
        self.__background_image_name: str = ""
        self.__background_image_surface: StaticImage = self._black_bg.copy()
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
        VisualNovelCharacterImageManager.reset()

    # 获取对话框模块（子类需实现）
    @abstractmethod
    def _get_dialog_box(self) -> AbstractDialogBox:
        return Exceptions.fatal("_dialogBox()", 1)

    # 获取对话文件所在的文件夹目录
    def get_dialog_folder_location(self) -> str:
        return (
            os.path.join(self._dialog_folder_path, self._chapter_type)
            if self._project_name is None
            else os.path.join(self._dialog_folder_path, self._chapter_type, self._project_name)
        )

    # 获取对话文件所在的具体路径
    def get_dialog_file_location(self, lang: str) -> str:
        return os.path.join(self.get_dialog_folder_location(), f"chapter{self._chapter_id}_dialogs_{lang}.json")

    # 获取对话文件所在的具体路径
    def get_data_file_path(self) -> str:
        return self.get_dialog_file_location(Settings.get_language())

    # 获取对话文件的主语言
    def get_default_lang(self) -> str:
        # 读取项目信息
        _data: dict = Configurations.load_file(
            os.path.join(self._dialog_folder_path, self._chapter_type, "info.json")
            if self._project_name is None
            else os.path.join(self._dialog_folder_path, self._chapter_type, self._project_name, "info.json")
        )
        # 自3.7起使用default_language，出于兼容目的尝试读取default_lang（3.6前的key）
        return str(_data.get("default_language", _data.get("default_lang", "English")))

    # 返回需要保存数据
    def _get_data_need_to_save(self) -> dict:
        return self.get_data_of_parent_game_system() | {
            "dialog_id": self._content.get_current_dialogue_id(),
            "section": self._content.get_section(),
            "type": "dialog",
            "linpg": Version.get_current_version(),
        }

    # 读取存档
    def load_progress(self, _data: dict) -> None:
        self.new(
            _data["chapter_type"],
            _data["chapter_id"],
            _data["section"],
            _data.get("project_name"),
            _data.get("dialog_id", "head"),
        )

    # 新读取章节
    def new(
        self, chapterType: str, chapterId: int, section: str, projectName: str | None = None, dialogId: str = "head"
    ) -> None:
        # 初始化关键参数
        self._initialize(chapterType, chapterId, projectName)
        # load the dialogue content data
        self._load_content()
        # select the section
        self._content.set_section(section)
        # select the base on given dialogue id
        self._content.set_current_dialogue_id(dialogId)
        # 将数据载入刚初始化的模块中
        self._update_scene(self._content.get_current_dialogue_id())

    # 载入数据
    def _load_content(self) -> None:
        # 如果玩家所选择的语种有对应的翻译，则优先读取，否则使用开发者的默认语种
        content_data: dict = Configurations.load_file(
            self.get_data_file_path()
            if os.path.exists(self.get_data_file_path())
            else self.get_dialog_file_location(self.get_default_lang())
        )
        # try fetch "dialogs" for backward compatibility
        self._content.update(content_data.get("dialogues", content_data.get("dialogs")))

    # 更新背景图片
    def _update_background_image(self, image_name: str) -> None:
        if self.__background_image_name != image_name:
            # 更新背景的名称
            self.__background_image_name = image_name
            # 更新背景的图片数据
            if len(self.__background_image_name) > 0:
                # 尝试加载图片式的背景
                if os.path.exists((img_path := Specifications.get_directory("background_image", self.__background_image_name))):
                    self.__background_image_surface = StaticImage(img_path, 0, 0)
                    self.__background_image_surface.disable_cropping()
                else:
                    Exceptions.fatal(f"Cannot find a background image or video file called '{self.__background_image_name}'.")
            else:
                self.__background_image_surface = self._black_bg.copy()

    # 更新场景
    def _update_scene(self, dialog_id: str) -> None:
        # 更新dialogId
        self._content.set_current_dialogue_id(dialog_id)
        # 更新立绘和背景
        VisualNovelCharacterImageManager.update(self._content.current.character_images)
        self._update_background_image(self._content.current.background_image)
        # 更新对话框
        self._get_dialog_box().update(self._content.current.narrator, self._content.current.contents)
        # 更新背景音乐
        if len(self._content.current.background_music) > 0:
            self.set_bgm(Specifications.get_directory("music", self._content.current.background_music))
        else:
            self.unload_bgm()
        # 隐藏选项菜单
        self._dialog_options_container.clear()
        self._dialog_options_container.set_visible(False)

    # 更新语言
    def update_language(self) -> None:
        super().update_language()
        # 保存原来的数据
        currentSect: str = self._content.get_section()
        currentId: str = self._content.get_current_dialogue_id()
        # reload data
        self._load_content()
        # select the section
        if self._content.contains_section(currentSect):
            self._content.set_section(currentSect)
            # select the base on given dialogue id
            if self._content.contains_dialogue(currentSect, currentId):
                self._content.set_current_dialogue_id(currentId)
        # update the scene
        self._update_scene(self._content.get_current_dialogue_id())

    # 停止播放
    def stop(self) -> None:
        # 释放立绘渲染系统占用的内存
        VisualNovelCharacterImageManager.reset()
        # 设置停止播放
        super().stop()

    # 将背景图片画到surface上
    def display_background_image(self, _surface: ImageSurface) -> None:
        if self.__background_image_surface is not None:
            if isinstance(self.__background_image_surface, StaticImage):
                self.__background_image_surface.set_width_with_original_image_size_locked(_surface.get_width())
                self.__background_image_surface.set_left(0)
                self.__background_image_surface.set_centery(_surface.get_height() // 2)
            self.__background_image_surface.draw(_surface)

    def _get_dialog_options_container_ready(self) -> None:
        self._dialog_options_container.clear()
        if self._content.current.next.has_multi_targets():
            optionBox_y_base: int = (
                Display.get_height() * 3 // 16 - len(self._content.current.next.get_targets()) * self._FONT_SIZE
            )
            for i, _target in enumerate(self._content.current.next.get_targets()):
                optionButton: Button = Button.load("<&ui>option.png", (0, 0), (0, 0))
                optionButton.set_hover_img(Images.quickly_load("<&ui>option_selected.png"))
                optionButton.set_auto_resize(True)
                optionButton.set_text(ButtonComponent.text(str(_target["text"]), self._FONT_SIZE, Colors.WHITE))
                optionButton.set_pos(
                    (Display.get_width() - optionButton.get_width()) / 2, (i + 1) * 4 * self._FONT_SIZE + optionBox_y_base
                )
                self._dialog_options_container.append(optionButton)
            self._dialog_options_container.set_visible(True)

    # 把基础内容画到surface上
    def draw(self, _surface: ImageSurface) -> None:
        # 检测章节是否初始化
        if self._chapter_id is None:
            Exceptions.fatal("The dialog has not been initialized!")
        # 展示背景图片和npc立绘
        self.display_background_image(_surface)
        VisualNovelCharacterImageManager.draw(_surface)
        self._get_dialog_box().draw(_surface)
        # 如果不处于静音状态
        if not self._is_muted:
            # 播放背景音乐
            self.play_bgm()
