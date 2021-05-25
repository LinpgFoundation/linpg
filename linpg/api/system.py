# cython: language_level=3
import threading
from tkinter.constants import TRUE
from .mixer import *

#使用多线程保存数据
class SaveDataThread(threading.Thread):
    def __init__(self, path:str, data:dict):
        super().__init__()
        self.path:str = path
        self.data:dict = data
    def run(self) -> None:
        save_config(self.path,self.data)
        del self.data,self.path

#系统模块接口
class AbstractSystem:
    def __init__(self):
        #判定用于判定是否还在播放的参数
        self.__is_playing:bool = True
        self._language_when_initialize:str = get_current_language()
    #是否正在播放
    @property
    def isPlaying(self) -> bool: return self.__is_playing
    def is_playing(self) -> bool: return self.__is_playing
    def stop(self) -> None: self.__is_playing = False
    def _continue(self) -> None: self.__is_playing = True
    #是否本体语言和当前一致
    def language_need_update(self) -> bool: return self._language_when_initialize != get_current_language()
    #更新语言
    def updated_language(self) -> None: self._language_when_initialize = get_current_language()

#拥有背景音乐的系统模块接口
class SystemWithBackgroundMusic(AbstractSystem):
    def __init__(self) -> None:
        super().__init__()
        self.__bgm_path = None
        self.__bgm_volume:float = 1.0
        self.__if_stop_playing_bgm:bool = False
    #获取bgm名称（非路径）
    @property
    def bgm(self) -> Union[str,None]: self.get_bgm()
    def get_bgm(self) -> Union[str,None]: return os.path.basename(self.__bgm_path) if self.__bgm_path is not None else None
    #设置bgm路径
    def set_bgm(self, path:Union[str,None], forced:bool=False) -> None:
        if path is None:
            self.__bgm_path = None
            pygame.mixer.music.unload()
        #如果路径存在
        elif os.path.exists(path):
            #只有在音乐路径不一致或者强制更新的情况下才会更新路径（同时卸载现有音乐）
            if self.__bgm_path != path or forced is True:
                self.__bgm_path = path
                pygame.mixer.music.unload()
            else:
                #同一首曲子，不更新任何内容
                pass
        else:
            throw_exception("error","Path '{}' does not exist!".format(path))
    #获取bgm音量
    @property
    def bgm_volume(self) -> float: return self.__bgm_volume
    def get_bgm_volume(self) -> float: return self.__bgm_volume
    #设置bgm音量
    def set_bgm_volume(self,volume:Union[float,int]) -> None:
        if 1 >= volume >= 0:
            if self.__bgm_path is not None and pygame.mixer.music.get_busy():
                pygame.mixer.music.set_volume(volume)
            self.__bgm_volume = volume
        else:
            throw_exception("error","Volume '{}' is out of the range! (must between 0 and 1)".format(volume))
    #播放bgm
    def play_bgm(self, times:int=1) -> None:
        if self.__bgm_path is not None and not pygame.mixer.music.get_busy() and not self.__if_stop_playing_bgm:
            pygame.mixer.music.load(self.__bgm_path)
            pygame.mixer.music.set_volume(self.__bgm_volume)
            pygame.mixer.music.play(times)
    #停止播放bgm
    def stop_playing_bgm(self) -> None:
        self.__if_stop_playing_bgm = True
        pygame.mixer.music.stop()
    #继续播放bgm
    def continue_playing_bgm(self) -> None:
        self.__if_stop_playing_bgm = False
    #卸载bgm，释放内存
    def unload_bgm(self) -> None:
        self.__bgm_path = None
        pygame.mixer.music.unload()

#游戏模块接口
class AbstractGameSystem(SystemWithBackgroundMusic):
    def __init__(self):
        super().__init__()
        #参数
        self._chapter_type:str = ""
        self._chapter_id:int = 0
        self._project_name = None
        #储存进度存档的文件夹的路径
        self.folder_for_save_file:str = "Save"
        #存档文件的名称
        self.name_for_save_file:str = "save.yaml"
        #是否已经初始化
        self.__initialized:bool = False
    #正在读取的文件
    @property
    def file_path(self) -> str: return os.path.join(self.folder_for_save_file,self.name_for_save_file)
    #是否初始化
    @property
    def isInitialized(self) -> bool: return self.__initialized
    def is_initialized(self) -> bool: return self.__initialized
    #初始化关键参数
    def _initialize(self, chapterType:str, chapterId:int, projectName:str) -> None:
        #类型
        self._chapter_type = chapterType
        #章节id
        self._chapter_id = chapterId
        #合集名称-用于dlc和创意工坊
        self._project_name = projectName
        #初始化完成
        self.__initialized = True
    #获取本模块的信息
    @property
    def data_of_parent_game_system(self) -> dict: return self.get_data_of_parent_game_system()
    def get_data_of_parent_game_system(self) -> dict: return {
        "chapter_type": self._chapter_type,
        "chapter_id": self._chapter_id,
        "project_name": self._project_name
        }
    #获取需要保存的数据 - 子类必须实现
    def _get_data_need_to_save(self) -> dict: throw_exception("error","The child class does not implement _get_data_need_to_save() function!")
    #保存进度
    def save_progress(self) -> None:
        #确保储存进度存档的文件夹存在
        if not os.path.exists(self.folder_for_save_file): os.makedirs(self.folder_for_save_file)
        #存档数据
        save_thread = SaveDataThread(self.file_path,self._get_data_need_to_save())
        save_thread.start()
        save_thread.join()
        del save_thread
