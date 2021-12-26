from .display import *

# 根据设置参数改变声道数量
MIXER_CHANNEL_NUM: int = max(int(Setting.get("NumberOfChannels")), 8) + 3
pygame.mixer.set_num_channels(MIXER_CHANNEL_NUM)

"""设置linpg引擎保留的"""
# 背景音乐
_RESERVED_BACKGROUND_MUSIC_CHANNEL_ID: int = MIXER_CHANNEL_NUM - 3
LINPG_RESERVED_BACKGROUND_MUSIC_CHANNEL = pygame.mixer.Channel(_RESERVED_BACKGROUND_MUSIC_CHANNEL_ID)
# 音效
_RESERVED_SOUND_EFFECTS_CHANNEL_ID: int = MIXER_CHANNEL_NUM - 2
LINPG_RESERVED_SOUND_EFFECTS_CHANNEL = pygame.mixer.Channel(_RESERVED_SOUND_EFFECTS_CHANNEL_ID)
# 环境
_RESERVED_ENVIRONMENTAL_SOUND_CHANNEL_ID: int = MIXER_CHANNEL_NUM - 1
LINPG_RESERVED_ENVIRONMENTAL_SOUND_CHANNEL = pygame.mixer.Channel(_RESERVED_ENVIRONMENTAL_SOUND_CHANNEL_ID)

# 音效管理模块接口
class AbstractSoundManager:
    def __init__(self, channel_id: int):
        self._channel_id: int = int(channel_id)

    @property
    def channel_id(self) -> int:
        return self._channel_id

    def get_channel_id(self) -> int:
        return self._channel_id


# 音效管理模块-列表
class SoundManagement(AbstractSoundManager):
    def __init__(self, channel_id: int):
        super().__init__(channel_id)
        self.sound_id: int = 0
        self.__sounds_list: list = []

    # 添加音乐
    def add(self, path: str) -> None:
        self.__sounds_list.append(Sound.load(path))

    # 播放音乐
    def play(self, sound_id: int = -1) -> None:
        if len(self.__sounds_list) > 0 and not pygame.mixer.Channel(self._channel_id).get_busy():
            self.sound_id = get_random_int(0, len(self.__sounds_list) - 1) if sound_id < 0 else sound_id
            pygame.mixer.Channel(self._channel_id).play(self.__sounds_list[self.sound_id])

    # 停止播放
    def stop(self) -> None:
        pygame.mixer.Channel(self._channel_id).stop()

    # 获取音量
    @property
    def volume(self) -> float:
        return self.get_volume()

    def get_volume(self) -> float:
        return self.__sounds_list[0].get_volume()

    # 设置音量
    def set_volume(self, volume: number) -> None:
        for i in range(len(self.__sounds_list)):
            self.__sounds_list[i].set_volume(volume)


# 获取视频的音频 （返回路径）
def _split_audio_from_video(input_path: str, audio_type="ogg") -> str:
    output_folder: str = os.path.dirname(input_path)
    # 产生不重名的output文件名称
    output_file_name_t: str = os.path.basename(input_path).replace(".", "_") + "{0}.{1}"
    output_file_name: str
    index: int = 0
    while True:
        output_file_name = output_file_name_t.format(index, audio_type)
        if not os.path.exists(output_file_name):
            break
        else:
            index += 1
    # 生成output路径
    output_path: str = os.path.join(output_folder, output_file_name)
    try:
        # 生成视频文件
        VideoConverter.convert_from_video_to_audio(input_path, output_path)
        # 如果一切正常，返回output路径
        return output_path
    # 如果不正常...
    except FileNotExists:
        EXCEPTION.fatal('Cannot find media file on path "{}".'.format(input_path))
    except ToolIsMissing:
        EXCEPTION.fatal(
            'To split audio from video, "ffmpeg.exe" needs to be placed under directory "{}" inside your project. FFmpeg is never a part of Linpg Engine.'.format(
                os.path.dirname(VideoConverter.get_tool_path())
            )
        )


# 音效管理
class Sound:
    # 加载音效
    @staticmethod
    def load(path: str, volume: float = 1.0) -> pygame.mixer.Sound:
        soundTmp: pygame.mixer.Sound = pygame.mixer.Sound(path)
        if volume != 1.0:
            soundTmp.set_volume(volume)
        return soundTmp

    # 从一个视频中加载音效
    @staticmethod
    def load_from_video(path: str, volume: float = 1.0) -> pygame.mixer.Sound:
        path_of_sound: str = _split_audio_from_video(path)
        sound_audio = Sound.load(path_of_sound, volume)
        os.remove(path_of_sound)
        return sound_audio

    # 播放音效
    @staticmethod
    def play(sound: pygame.mixer.Sound, channel_id: int) -> None:
        pygame.mixer.Channel(channel_id).play(sound)

    # 淡出音效
    @staticmethod
    def fade_out(time: float) -> None:
        pygame.mixer.fadeout(int(time))

    # 寻找一个可用的频道
    @staticmethod
    def find_channel(force: bool = False) -> pygame.mixer.Channel:
        return pygame.mixer.find_channel(force)

    # 获取频道的数量
    @staticmethod
    def get_num_channels() -> int:
        return int(pygame.mixer.get_num_channels() - 3)

    # 获取对应id的频道
    @staticmethod
    def get_channel(channel_id: int) -> pygame.mixer.Channel:
        if channel_id < Sound.get_num_channels():
            return pygame.mixer.Channel(channel_id)
        else:
            EXCEPTION.fatal('The channel_id "{0}" is out of bound of {1}'.format(channel_id, Sound.get_num_channels()))


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
        path_of_music: str = _split_audio_from_video(path, "mp3")
        Music.load(path_of_music)
        return path_of_music

    # 卸载背景音乐
    @staticmethod
    def unload() -> None:
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
        pygame.mixer.music.stop()

    # 淡出背景音乐
    @staticmethod
    def fade_out(time: number) -> None:
        pygame.mixer.music.fadeout(int(time))

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
class SoundVolumeManger:

    __sound_unit: int = 100

    @property
    def global_value(self) -> int:
        return keep_int_in_range(round(Setting.get("Sound", "global_value")), 0, self.__sound_unit)

    @property
    def background_music(self) -> int:
        return round(
            keep_number_in_range(round(Setting.get("Sound", "background_music"), 2), 0, self.__sound_unit)
            * self.global_value
            / self.__sound_unit
        )

    @property
    def effects(self) -> int:
        return round(
            keep_number_in_range(round(Setting.get("Sound", "effects"), 2), 0, self.__sound_unit)
            * self.global_value
            / self.__sound_unit
        )

    @property
    def environment(self) -> int:
        return round(
            keep_number_in_range(round(Setting.get("Sound", "environment"), 2), 0, self.__sound_unit)
            * self.global_value
            / self.__sound_unit
        )


# 多媒体全局管理
class MediaController:

    __volume: SoundVolumeManger = SoundVolumeManger()

    @property
    def volume(self) -> SoundVolumeManger:
        return self.__volume

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
        Music.unload()
        pygame.mixer.stop()

    # 淡出所有音乐
    @staticmethod
    def fade_out(time: float) -> None:
        Sound.fade_out(time)
        Music.fade_out(time)


Media: MediaController = MediaController()
