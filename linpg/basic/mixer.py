from .videos import *

# 频道 type alias
SoundChannel = pygame.mixer.Channel


# linpg引擎保留的频道
class LINPG_RESERVED_CHANNELS:
    # 根据设置参数改变声道数量
    __MIXER_CHANNEL_NUM: Final[int] = max(int(Setting.get("NumberOfChannels")), 8) + 3
    # 背景音乐
    __BACKGROUND_MUSIC_CHANNEL_ID: Final[int] = __MIXER_CHANNEL_NUM - 3
    BACKGROUND_MUSIC_CHANNEL: Optional[SoundChannel] = None
    # 音效
    __SOUND_EFFECTS_CHANNEL_ID: Final[int] = __MIXER_CHANNEL_NUM - 2
    SOUND_EFFECTS_CHANNEL: Optional[SoundChannel] = None
    # 环境
    __ENVIRONMENTAL_SOUND_CHANNEL_ID: Final[int] = __MIXER_CHANNEL_NUM - 1
    ENVIRONMENTAL_SOUND_CHANNEL: Optional[SoundChannel] = None

    # 初始化对应频道
    @classmethod
    def init(cls) -> None:
        if pygame.mixer.get_init() is not None:
            pygame.mixer.set_num_channels(cls.__MIXER_CHANNEL_NUM)
            cls.BACKGROUND_MUSIC_CHANNEL = pygame.mixer.Channel(cls.__BACKGROUND_MUSIC_CHANNEL_ID)
            cls.SOUND_EFFECTS_CHANNEL = pygame.mixer.Channel(cls.__SOUND_EFFECTS_CHANNEL_ID)
            cls.ENVIRONMENTAL_SOUND_CHANNEL = pygame.mixer.Channel(cls.__ENVIRONMENTAL_SOUND_CHANNEL_ID)
        else:
            EXCEPTION.inform("Mixer has not been initialized correctly!")
            print("One possible cause could be no output device, anyway, please double check your output device(s)!")


# 初始化引擎保留频道
LINPG_RESERVED_CHANNELS.init()


# 声音类
class Sound(pygame.mixer.Sound):
    def __init__(self, _input: Any) -> None:
        self.__input: Any = _input
        self.__init: bool = False
        self.__volume: float = 1.0
        self.__try_init()

    # 尝试初始化
    def __try_init(self) -> None:
        if not self.__init and pygame.mixer.get_init() is not None:
            super().__init__(self.__input)
            self.set_volume(self.__volume)
            self.__init = True

    def play(self, loops: int = 0, max_time: int = 0, fade_ms: int = 0) -> Optional[SoundChannel]:  # type: ignore[override]
        self.__try_init()
        if self.__init is True:
            return super().play(loops, max_time, fade_ms)
        return None

    def set_volume(self, value: float) -> None:
        if self.__init is True:
            super().set_volume(value)
        else:
            self.__volume = value

    def get_volume(self) -> float:
        if self.__init is True:
            return super().get_volume()
        else:
            return self.__volume

    def stop(self) -> None:
        if self.__init is True:
            super().stop()

    def fadeout(self, time: int) -> None:
        if self.__init is True:
            super().fadeout(time)


# 音效管理模块-列表
class SoundsManager:
    def __init__(self, channel_id: int):
        self.__channel_id: int = channel_id
        self.__index: int = 0
        self.__sounds: list[Sound] = []

    @property
    def channel_id(self) -> int:
        return self.__channel_id

    def get_channel_id(self) -> int:
        return self.__channel_id

    # 添加音乐
    def add(self, path: str) -> None:
        self.__sounds.append(Sounds.load(path))

    # 清空列表释放内存
    def clear(self) -> None:
        self.__sounds.clear()

    # 播放音乐
    def play(self, sound_id: int = -1) -> None:
        if len(self.__sounds) > 0 and pygame.mixer.get_init() is not None and not pygame.mixer.Channel(self.__channel_id).get_busy():
            self.__index = Numbers.get_random_int(0, len(self.__sounds) - 1) if sound_id < 0 else sound_id
            pygame.mixer.Channel(self.__channel_id).play(self.__sounds[self.__index])

    # 停止播放
    def stop(self) -> None:
        if pygame.mixer.get_init() is not None:
            pygame.mixer.Channel(self.__channel_id).stop()

    # 获取音量
    @property
    def volume(self) -> float:
        return self.get_volume()

    def get_volume(self) -> float:
        return self.__sounds[0].get_volume()

    # 设置音量
    def set_volume(self, volume: number) -> None:
        for _sound in self.__sounds:
            _sound.set_volume(volume)


# 音效管理
class Sounds:
    # 是否成功初始化
    @staticmethod
    def get_init() -> bool:
        return pygame.mixer.get_init() is not None

    # 加载音效
    @staticmethod
    def load(path: str, volume: Optional[float] = None) -> Sound:
        soundTmp: Sound = Sound(path)
        if volume is not None:
            soundTmp.set_volume(volume)
        return soundTmp

    # 从一个视频中加载音效
    @classmethod
    def load_from_video(cls, path: str, volume: Optional[float] = None, cache_key: Optional[str] = None) -> Sound:
        # 如果给定了cache_key，则先尝试从缓存中读取音乐文件
        if cache_key is not None and len(cache_key) > 0 and Cache.match(cache_key, path) is True:
            try:
                return cls.load(Cache.get_cache_path(cache_key), volume)
            except Exception:
                pass
        # 如果读取失败或者没有缓存key或者match失败，则应根据给定的路径生成音乐文件并返回
        path_of_sound: str = Videos.split_audio(path)
        sound_audio: Sound = cls.load(path_of_sound, volume)
        # 如果给了缓存key，则应该生成缓存联系并保留缓存文件
        if cache_key is not None and len(cache_key) > 0:
            Cache.new(cache_key, path, path_of_sound)
        # 如果没有缓存key，则删除缓存文件
        else:
            os.remove(path_of_sound)
        return sound_audio

    # 从一个文件夹中加载音效
    @classmethod
    def load_from_directory(cls, folder_path: str) -> tuple[Sound, ...]:
        if not os.path.isdir(folder_path):
            EXCEPTION.fatal("The path is not a valid directory!")
        return tuple(cls.load(_path) for _path in glob(os.path.join(folder_path, "*")))

    # 播放音效
    @classmethod
    def play(cls, sound: Sound, channel_id: int) -> None:
        if cls.get_init() is True:
            pygame.mixer.Channel(channel_id).play(sound)

    # 停止播放
    @classmethod
    def stop(cls) -> None:
        if cls.get_init() is True:
            pygame.mixer.stop()

    # 淡出音效
    @classmethod
    def fade_out(cls, time: int) -> None:
        if cls.get_init() is True:
            pygame.mixer.fadeout(time)

    # 寻找一个可用的频道
    @classmethod
    def find_channel(cls, force: bool = False) -> Optional[SoundChannel]:
        return pygame.mixer.find_channel(force) if cls.get_init() is True else None

    # 获取频道的数量
    @staticmethod
    def get_num_channels() -> int:
        return pygame.mixer.get_num_channels() - 3

    # 获取对应id的频道
    @classmethod
    def get_channel(cls, channel_id: int) -> SoundChannel:
        if channel_id < cls.get_num_channels():
            return pygame.mixer.Channel(channel_id)
        else:
            EXCEPTION.fatal(f'The channel_id "{channel_id}" is out of bound of {cls.get_num_channels()}')


# 音乐管理
class Music:
    # 加载背景音乐（但不播放）
    @staticmethod
    def load(path: str) -> None:
        pygame.mixer.music.load(path)

    # 从一个视频中加载音乐
    @staticmethod
    def load_from_video(path: str) -> str:
        Music.unload()
        path_of_music: str = Videos.split_audio(path, "mp3")
        Music.load(path_of_music)
        return path_of_music

    # 卸载背景音乐
    @staticmethod
    def unload() -> None:
        if Sounds.get_init() is True:
            pygame.mixer.music.unload()

    # 重新开始播放背景音乐
    @staticmethod
    def restart() -> None:
        pygame.mixer.music.rewind()

    # 播放背景音乐
    @staticmethod
    def play(loops: int = 0, start: float = 0.0, fade_ms: int = 0) -> None:
        pygame.mixer.music.play(loops, start, fade_ms)

    # 停止播放
    @staticmethod
    def stop() -> None:
        if Sounds.get_init() is True:
            pygame.mixer.music.stop()

    # 淡出背景音乐
    @staticmethod
    def fade_out(time: int) -> None:
        pygame.mixer.music.fadeout(time)

    # 获取背景音乐播放的位置
    @staticmethod
    def get_pos() -> int:
        return pygame.mixer.music.get_pos()

    # 设置背景音乐播放的位置
    @staticmethod
    def set_pos(time: float) -> None:
        pygame.mixer.music.set_pos(time)

    # 获取背景音乐的音量
    @staticmethod
    def get_volume() -> float:
        return pygame.mixer.music.get_volume()

    # 调整背景音乐的音量
    @staticmethod
    def set_volume(volume: float) -> None:
        pygame.mixer.music.set_volume(volume)

    # 是否忙碌
    @staticmethod
    def get_busy() -> bool:
        return pygame.mixer.music.get_busy()


# 音量管理
class Volume:
    __sound_unit: Final[int] = 100

    @classmethod
    def get_global_value(cls) -> int:
        return Numbers.keep_int_in_range(round(Setting.get("Sound", "global_value")), 0, cls.__sound_unit)

    @classmethod
    def get_background_music(cls) -> int:
        return round(
            Numbers.keep_number_in_range(round(Setting.get("Sound", "background_music"), 2), 0, cls.__sound_unit) * cls.get_global_value() / cls.__sound_unit
        )

    @classmethod
    def get_effects(cls) -> int:
        return round(Numbers.keep_number_in_range(round(Setting.get("Sound", "effects"), 2), 0, cls.__sound_unit) * cls.get_global_value() / cls.__sound_unit)

    @classmethod
    def get_environment(cls) -> int:
        return round(
            Numbers.keep_number_in_range(round(Setting.get("Sound", "environment"), 2), 0, cls.__sound_unit) * cls.get_global_value() / cls.__sound_unit
        )


# 多媒体全局管理
class Media:
    # 是否有任何音乐在播放
    @staticmethod
    def get_busy() -> bool:
        return pygame.mixer.get_busy()

    # 暂停正在播放的音乐
    @staticmethod
    def pause() -> None:
        pygame.mixer.pause()

    # 继续播放暂停的音乐
    @staticmethod
    def unpause() -> None:
        pygame.mixer.unpause()

    # 卸载所有音乐
    @staticmethod
    def unload() -> None:
        Sounds.stop()
        Music.unload()

    # 淡出所有音乐
    @staticmethod
    def fade_out(time: int) -> None:
        Sounds.fade_out(time)
        Music.fade_out(time)
