from abc import ABC, ABCMeta, abstractmethod

from ..basic.configurations import Configurations
from ..basic.languages import Languages
from .coordinates import *


# 系统模块接口
class AbstractSystem(ABC):
    def __init__(self) -> None:
        # 判定用于判定是否还在播放的参数
        self.__is_playing: bool = True
        self.__current_language: str = Languages.get_current_language()

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
        return self.__current_language != Languages.get_current_language()

    # 更新语言
    def update_language(self) -> None:
        self.__current_language = Languages.get_current_language()


# 拥有背景音乐的系统模块接口
class SystemWithBackgroundMusic(AbstractSystem):
    def __init__(self) -> None:
        super().__init__()
        self.__audio: Sound | None = None
        self.__bgm_path: str | None = None
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
    def set_bgm(self, path: str | None, forced: bool = False) -> None:
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
                self.__audio = Sounds.load(self.__bgm_path, self.__bgm_volume)
        else:
            Exceptions.fatal(f"Path '{path}' does not exist!")

    # 设置bgm音量
    def set_bgm_volume(self, volume: number) -> None:
        if 1 >= volume >= 0:
            self.__bgm_volume = volume
            if self.__audio is not None:
                self.__audio.set_volume(self.__bgm_volume)
        else:
            Exceptions.fatal(f"Volume '{volume}' is out of the range! (must between 0 and 1)")

    # 播放bgm
    def play_bgm(self) -> None:
        if (
            self.__audio is not None
            and LINPG_RESERVED_CHANNELS.BACKGROUND_MUSIC_CHANNEL is not None
            and not LINPG_RESERVED_CHANNELS.BACKGROUND_MUSIC_CHANNEL.get_busy()
        ):
            LINPG_RESERVED_CHANNELS.BACKGROUND_MUSIC_CHANNEL.play(self.__audio)

    # 停止播放
    @staticmethod
    def stop_bgm() -> None:
        if LINPG_RESERVED_CHANNELS.BACKGROUND_MUSIC_CHANNEL is not None:
            LINPG_RESERVED_CHANNELS.BACKGROUND_MUSIC_CHANNEL.stop()

    # 把内容画到surface上（子类必须实现）
    @abstractmethod
    def draw(self, _surface: ImageSurface) -> None:
        Exceptions.fatal("draw()", 1)

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
        self._project_name: str | None = None
        # 是否已经初始化
        self.__initialized: bool = False

    # 是否初始化
    def is_initialized(self) -> bool:
        return self.__initialized

    # 初始化关键参数
    def _initialize(self, chapterType: str, chapterId: int, projectName: str | None) -> None:
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
    @abstractmethod
    def _get_data_need_to_save(self) -> dict:
        Exceptions.fatal("_get_data_need_to_save()", 1)

    # 默认加载数据的路径（子类需实现）
    @abstractmethod
    def get_data_file_path(self) -> str:
        Exceptions.fatal("get_data_file_path()", 1)

    # 加载进度（子类需实现）
    @abstractmethod
    def load_progress(self, _data: dict) -> None:
        Exceptions.fatal("load_progress()", 1)

    # 从默认的路径加载数据
    def load(self) -> None:
        self.load_progress(Configurations.load_file(self.get_data_file_path()))

    # 将数据保存到加载的路径
    def _save(self) -> None:
        Configurations.save(self.get_data_file_path(), self._get_data_need_to_save())
