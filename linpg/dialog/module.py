# cython: language_level=3
from .character import *

#视觉小说系统接口
class AbstractDialogSystem(AbstractGameSystem):
    def __init__(self):
        super().__init__()
        #加载对话的背景图片模块
        self._npc_manager = CharacterImageManager()
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
                if self.__background_image_name != "<transparent>":
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
                    self.__background_image_surface = None
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
