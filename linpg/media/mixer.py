from glob import glob

from .display import *

# 频道 type alias
SoundChannel = pygame.mixer.Channel


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

    def play(self, loops: int = 0, max_time: int = 0, fade_ms: int = 0) -> SoundChannel | None:  # type: ignore[override]
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
        if len(self.__sounds) > 0 and Sounds.get_init() is True and not SoundChannel(self.__channel_id).get_busy():
            self.__index = Numbers.get_random_int(0, len(self.__sounds) - 1) if sound_id < 0 else sound_id
            SoundChannel(self.__channel_id).play(self.__sounds[self.__index])

    # 停止播放
    def stop(self) -> None:
        if Sounds.get_init() is True:
            SoundChannel(self.__channel_id).stop()

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
    def load(path: str, volume: float | None = None) -> Sound:
        soundTmp: Sound = Sound(path)
        if volume is not None:
            soundTmp.set_volume(volume)
        return soundTmp

    # 从一个文件夹中加载音效
    @classmethod
    def load_from_directory(cls, folder_path: str) -> tuple[Sound, ...]:
        if not os.path.isdir(folder_path):
            Exceptions.fatal("The path is not a valid directory!")
        return tuple(cls.load(_path) for _path in glob(os.path.join(folder_path, "*")))

    # 播放音效
    @classmethod
    def play(cls, sound: Sound, channel_id: int) -> None:
        if cls.get_init() is True:
            SoundChannel(channel_id).play(sound)

    # 停止播放
    @classmethod
    def stop(cls) -> None:
        if cls.get_init() is True:
            pygame.mixer.stop()

    # 是否有任何音乐在播放
    @classmethod
    def get_busy(cls) -> bool:
        return pygame.mixer.get_busy() if cls.get_init() is True else True

    # 暂停正在播放的音乐
    @classmethod
    def pause(cls) -> None:
        if cls.get_init() is True:
            pygame.mixer.pause()

    # 继续播放暂停的音乐
    @classmethod
    def unpause(cls) -> None:
        if cls.get_init() is True:
            pygame.mixer.unpause()

    # 淡出音效
    @classmethod
    def fade_out(cls, time: int) -> None:
        if cls.get_init() is True:
            pygame.mixer.fadeout(time)

    # 寻找一个可用的频道
    @classmethod
    def find_channel(cls, force: bool = False) -> SoundChannel | None:
        return pygame.mixer.find_channel(force) if cls.get_init() is True else None

    # 获取频道的数量
    @staticmethod
    def get_num_channels() -> int:
        return max(pygame.mixer.get_num_channels() - 3, 0)

    # 获取对应id的频道
    @classmethod
    def get_channel(cls, channel_id: int) -> SoundChannel:
        if channel_id < cls.get_num_channels():
            return SoundChannel(channel_id)
        else:
            Exceptions.fatal(f'The channel_id "{channel_id}" is out of bound of {cls.get_num_channels()}')


# 音乐管理
class Music:
    # 是否成功初始化
    @staticmethod
    def get_init() -> bool:
        return pygame.mixer.get_init() is not None

    # 加载背景音乐（但不播放）
    @staticmethod
    def load(path: str) -> None:
        pygame.mixer.music.load(path)

    # 卸载背景音乐
    @classmethod
    def unload(cls) -> None:
        if cls.get_init() is True:
            pygame.mixer.music.unload()

    # 重新开始播放背景音乐
    @classmethod
    def restart(cls) -> None:
        if cls.get_init() is True:
            pygame.mixer.music.rewind()

    # 播放背景音乐
    @classmethod
    def play(cls, loops: int = 0, start: float = 0.0, fade_ms: int = 0) -> None:
        if cls.get_init() is True:
            pygame.mixer.music.play(loops, start, fade_ms)

    # 暂停正在播放的音乐
    @classmethod
    def pause(cls) -> None:
        if cls.get_init() is True:
            pygame.mixer.music.pause()

    # 继续播放暂停的音乐
    @classmethod
    def unpause(cls) -> None:
        if cls.get_init() is True:
            pygame.mixer.music.unpause()

    # 停止播放
    @classmethod
    def stop(cls) -> None:
        if cls.get_init() is True:
            pygame.mixer.music.stop()

    # 淡出背景音乐
    @classmethod
    def fade_out(cls, time: int) -> None:
        if cls.get_init() is True:
            pygame.mixer.music.fadeout(time)

    # 获取背景音乐播放的位置
    @classmethod
    def get_pos(cls) -> int:
        return pygame.mixer.music.get_pos() if cls.get_init() is True else 0

    # 设置背景音乐播放的位置
    @classmethod
    def set_pos(cls, time: float) -> None:
        if cls.get_init():
            pygame.mixer.music.set_pos(time)

    # 获取背景音乐的音量
    @classmethod
    def get_volume(cls) -> float:
        return pygame.mixer.music.get_volume() if cls.get_init() is True else 0

    # 调整背景音乐的音量
    @classmethod
    def set_volume(cls, volume: float) -> None:
        if cls.get_init() is True:
            pygame.mixer.music.set_volume(volume)

    # 是否忙碌
    @classmethod
    def get_busy(cls) -> bool:
        return pygame.mixer.music.get_busy() if cls.get_init() is True else True


# 音量管理
class Volume:
    __sound_unit: Final[int] = 100

    @classmethod
    def get_global_value(cls) -> int:
        return Numbers.keep_int_in_range(round(Settings.get("Sound", "global_value")), 0, cls.__sound_unit)

    @classmethod
    def get_background_music(cls) -> int:
        return round(
            Numbers.keep_number_in_range(round(Settings.get("Sound", "background_music"), 2), 0, cls.__sound_unit)
            * cls.get_global_value()
            / cls.__sound_unit
        )

    @classmethod
    def get_effects(cls) -> int:
        return round(
            Numbers.keep_number_in_range(round(Settings.get("Sound", "effects"), 2), 0, cls.__sound_unit)
            * cls.get_global_value()
            / cls.__sound_unit
        )

    @classmethod
    def get_environment(cls) -> int:
        return round(
            Numbers.keep_number_in_range(round(Settings.get("Sound", "environment"), 2), 0, cls.__sound_unit)
            * cls.get_global_value()
            / cls.__sound_unit
        )


# 多媒体全局管理
class Media:
    # 是否有任何音乐在播放
    @staticmethod
    def get_busy() -> bool:
        return Sounds.get_busy() or Music.get_busy()

    # 暂停正在播放的音乐
    @staticmethod
    def pause() -> None:
        Sounds.pause()
        Music.pause()

    # 继续播放暂停的音乐
    @staticmethod
    def unpause() -> None:
        Sounds.unpause()
        Music.unpause()

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


# linpg引擎保留的频道
class LINPG_RESERVED_CHANNELS:
    # 根据设置参数改变声道数量
    __MIXER_CHANNEL_NUM: Final[int] = max(int(Settings.get("NumberOfChannels")), 8) + 3
    # 背景音乐
    __BACKGROUND_MUSIC_CHANNEL_ID: Final[int] = __MIXER_CHANNEL_NUM - 3
    BACKGROUND_MUSIC_CHANNEL: SoundChannel | None = None
    # 音效
    __SOUND_EFFECTS_CHANNEL_ID: Final[int] = __MIXER_CHANNEL_NUM - 2
    SOUND_EFFECTS_CHANNEL: SoundChannel | None = None
    # 环境
    __ENVIRONMENTAL_SOUND_CHANNEL_ID: Final[int] = __MIXER_CHANNEL_NUM - 1
    ENVIRONMENTAL_SOUND_CHANNEL: SoundChannel | None = None

    # 初始化对应频道
    @classmethod
    def init(cls) -> None:
        if Sounds.get_init() is True:
            pygame.mixer.set_num_channels(cls.__MIXER_CHANNEL_NUM)
            cls.BACKGROUND_MUSIC_CHANNEL = SoundChannel(cls.__BACKGROUND_MUSIC_CHANNEL_ID)
            cls.SOUND_EFFECTS_CHANNEL = SoundChannel(cls.__SOUND_EFFECTS_CHANNEL_ID)
            cls.ENVIRONMENTAL_SOUND_CHANNEL = SoundChannel(cls.__ENVIRONMENTAL_SOUND_CHANNEL_ID)
        else:
            Exceptions.inform("Mixer has not been initialized correctly!")
            print("One possible cause could be no output device, anyway, please double check your output device(s)!")


# 初始化引擎保留频道
LINPG_RESERVED_CHANNELS.init()
