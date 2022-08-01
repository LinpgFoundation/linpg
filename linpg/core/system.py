import threading
from abc import ABCMeta

from ..basic import *


# 使用多线程保存数据
class SaveDataThread(threading.Thread):
    def __init__(self, path: str, data: dict):
        super().__init__()
        self.path: str = str(path)
        self.data: dict = dict(data)
        self.result: bool = False

    # 返回一个线程的复制
    def copy(self) -> "SaveDataThread":
        return SaveDataThread(self.path, self.data)

    def run(self) -> None:
        Config.save(self.path, self.data)
        self.result = True


# 系统模块接口
class AbstractSystem(ABC):
    def __init__(self) -> None:
        # 判定用于判定是否还在播放的参数
        self.__is_playing: bool = True
        self.__current_language: str = Lang.get_current_language()

    # 是否正在播放
    def is_playing(self) -> bool:
        return self.__is_playing

    # 停止播放
    def stop(self) -> None:
        self.__is_playing = False

    def _continue(self) -> None:
        self.__is_playing = True

    # 是否本体语言和当前一致
    def language_need_update(self) -> bool:
        return self.__current_language != Lang.get_current_language()

    # 更新语言
    def update_language(self) -> None:
        self.__current_language = Lang.get_current_language()


# 拥有背景音乐的系统模块接口
class SystemWithBackgroundMusic(AbstractSystem):
    def __init__(self) -> None:
        super().__init__()
        self.__audio: Optional[PG_Sound] = None
        self.__bgm_path: Optional[str] = None
        self.__bgm_volume: float = 1.0

    # 系统退出时，需卸载bgm
    def stop(self) -> None:
        super().stop()
        self.unload_bgm()

    # 卸载bgm
    def unload_bgm(self) -> None:
        self.stop_bgm()
        self.__bgm_path = None
        self.__audio = None

    # 设置bgm
    def set_bgm(self, path: Optional[str], forced: bool = False) -> None:
        # 如果path是None,则
        if path is None:
            if self.__bgm_path is not None:
                self.unload_bgm()
        # 如果路径存在
        elif os.path.exists(path):
            # 只有在音乐路径不一致或者强制更新的情况下才会更新路径（同时卸载现有音乐）
            if self.__bgm_path != path or forced is True:
                self.unload_bgm()
                self.__bgm_path = path
                self.__audio = Sound.load(self.__bgm_path, self.__bgm_volume)
        else:
            EXCEPTION.fatal("Path '{}' does not exist!".format(path))

    # 设置bgm音量
    def set_bgm_volume(self, volume: number) -> None:
        if 1 >= volume >= 0:
            self.__bgm_volume = volume
            if self.__audio is not None:
                self.__audio.set_volume(self.__bgm_volume)
        else:
            EXCEPTION.fatal("Volume '{}' is out of the range! (must between 0 and 1)".format(volume))

    # 播放bgm
    def play_bgm(self) -> None:
        if self.__audio is not None and LINPG_RESERVED_BACKGROUND_MUSIC_CHANNEL is not None and not LINPG_RESERVED_BACKGROUND_MUSIC_CHANNEL.get_busy():
            LINPG_RESERVED_BACKGROUND_MUSIC_CHANNEL.play(self.__audio)

    # 停止播放
    @staticmethod
    def stop_bgm() -> None:
        if LINPG_RESERVED_BACKGROUND_MUSIC_CHANNEL is not None:
            LINPG_RESERVED_BACKGROUND_MUSIC_CHANNEL.stop()

    # 把内容画到surface上（子类必须实现）
    def draw(self, _surface: ImageSurface) -> None:
        EXCEPTION.fatal("draw()", 1)

    # 直接画到屏幕上
    def draw_on_screen(self) -> None:
        self.draw(Display.get_window())


# 游戏模块接口
class AbstractGameSystem(SystemWithBackgroundMusic, metaclass=ABCMeta):
    def __init__(self) -> None:
        super().__init__()
        # 参数
        self._chapter_type: str = ""
        self._chapter_id: int = 0
        self._project_name: Optional[str] = None
        # 储存进度存档的文件夹的路径
        self.folder_for_save_file: str = Specification.get_directory("save")
        # 存档文件的名称
        self.name_for_save_file: str = "save.{}".format(Config.get_file_type())
        # 是否已经初始化
        self.__initialized: bool = False

    # 正在读取的文件
    @property
    def file_path(self) -> str:
        return os.path.join(self.folder_for_save_file, self.name_for_save_file)

    # 是否初始化
    def is_initialized(self) -> bool:
        return self.__initialized

    # 初始化关键参数
    def _initialize(self, chapterType: str, chapterId: int, projectName: Optional[str]) -> None:
        # 类型
        self._chapter_type = chapterType
        # 章节id
        self._chapter_id = chapterId
        # 合集名称-用于dlc和创意工坊
        self._project_name = projectName
        # 初始化完成
        self.__initialized = True

    # 获取本模块的信息
    def get_data_of_parent_game_system(self) -> dict:
        return {"chapter_type": self._chapter_type, "chapter_id": self._chapter_id, "project_name": self._project_name}

    # 获取需要保存的数据（子类必须实现）
    def _get_data_need_to_save(self) -> dict:
        EXCEPTION.fatal("_get_data_need_to_save()", 1)

    # 保存进度
    def save_progress(self) -> None:
        # 确保储存进度存档的文件夹存在
        if not os.path.exists(self.folder_for_save_file):
            os.makedirs(self.folder_for_save_file)
        # 存档数据
        save_thread = SaveDataThread(self.file_path, self._get_data_need_to_save())
        save_thread.start()
        save_thread.join()
        del save_thread
