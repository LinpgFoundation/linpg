from .window import *

# 尝试导入opencv库
_OPENCV_INITIALIZED: bool = False
try:
    import cv2

    _OPENCV_INITIALIZED = True
except ImportError:
    pass

# 视频模块专属的错误检测器
def _video_validator(path: str) -> None:
    # 如果opencv没有成功地导入
    if not _OPENCV_INITIALIZED:
        EXCEPTION.fatal("You cannot use any video module unless you intall opencv!")
    # 确保路径存在
    elif not os.path.exists(path):
        EXCEPTION.fatal('Cannot find file on path: "{}"'.format(path))


# 获取视频封面
def get_preview_of_video(path: str, size: tuple[int, int] = NoSize) -> ImageSurface:
    _video_validator(path)
    video_stream = cv2.VideoCapture(path)
    video_stream.set(cv2.CAP_PROP_POS_FRAMES, int(video_stream.get(cv2.CAP_PROP_FRAME_COUNT) * 0.1))
    current_frame = cv2.cvtColor(video_stream.read()[1], cv2.COLOR_BGR2RGB)
    video_stream.release()
    del video_stream
    if size is not NoSize and (current_frame.shape[0] != size[0] or current_frame.shape[1] != size[1]):
        current_frame = cv2.resize(current_frame, size)
    return make_surface_from_array(current_frame)


# 视频抽象类
class AbstractVideo:
    def __init__(self, path: str, buffer_num: int, play_range: tuple[int, int] = (0, -1)):
        _video_validator(path)
        self._path: str = path
        # 确保路径存在
        if not os.path.exists(self._path):
            EXCEPTION.fatal('Cannot find file on path: "{}"'.format(self._path))
        """视频流"""
        self.__video_stream: cv2.VideoCapture = None
        self._frame_rate: int = 0
        self._frame_buffer_num: int = int(buffer_num)
        """参数"""
        # 确保play_range参数合法
        if len(play_range) < 2:
            EXCEPTION.fatal("The length of play_range parameter must >= 2.")
        self._starting_point: int = int(play_range[0])
        self._ending_point: int = int(play_range[1])
        self.__stopped: bool = False
        self.__started: bool = False
        self.__frame_index_to_set: int = -1

    # 初始化
    def _init(self) -> None:
        # 加载视频流
        self.__video_stream = cv2.VideoCapture(self._path)
        self.__video_stream.set(cv2.CAP_PROP_BUFFERSIZE, self._frame_buffer_num)
        # 如果设置了起点，则为视频设置开始播放的位置
        if self._starting_point > 0:
            self.set_frame_index(self._starting_point)
        # 获取秒帧数
        self._frame_rate = round(self.__video_stream.get(cv2.CAP_PROP_FPS))
        # 改变用于辨识视频是否开始播放的flag
        self.__started = True

    def set_starting_point(self, index: int):
        self._starting_point = int(index)

    # 每秒帧数
    @property
    def fps(self) -> int:
        return self._frame_rate

    @property
    def frame_rate(self) -> int:
        return self._frame_rate

    def get_frame_rate(self) -> int:
        return self._frame_rate

    # 总帧数
    @property
    def frame_num(self) -> int:
        return self.get_frame_num()

    def get_frame_num(self) -> int:
        return self.__video_stream.get(cv2.CAP_PROP_FRAME_COUNT) if self.__video_stream is not None else 0

    # 当前帧坐标
    @property
    def frame_index(self) -> int:
        return self.get_frame_index()

    def get_frame_index(self) -> int:
        return int(self.__video_stream.get(cv2.CAP_PROP_POS_FRAMES)) if self.__video_stream is not None else 0

    def set_frame_index(self, num: int) -> None:
        if num > self.get_frame_num():
            EXCEPTION.fatal('Frame index "{1}" is out of range "{2}"'.format(num, self.get_frame_num()))
        elif num < 0:
            EXCEPTION.fatal("You cannot set negative frame index.")
        else:
            self.__frame_index_to_set = int(num)

    # 已经播放的百分比
    def get_percentage_played(self) -> float:
        return self.get_frame_index() / max(self.get_frame_num(), 1)

    # 停止
    def stop(self) -> None:
        self.__stopped = True
        if self.__video_stream is not None:
            self.__video_stream.release()
            self.__video_stream = None

    # 是否已经开始
    @property
    def started(self) -> bool:
        return self.__started

    # 重新开始
    def restart(self) -> None:
        self.__stopped = False
        self._init()

    # 播放范围
    @property
    def play_range(self) -> tuple[int, int]:
        return self._starting_point, self._ending_point

    # 是否还在播放
    def is_playing(self) -> bool:
        return self.__started is True and self.__stopped is not True

    # 把画面画到surface上
    def draw(self, surface: ImageSurface) -> None:
        if self.__started is False:
            self._init()
        if not self.__stopped:
            if self.__frame_index_to_set >= 0:
                self.__video_stream.set(cv2.CAP_PROP_POS_FRAMES, self.__frame_index_to_set)
                self.__frame_index_to_set = -1
            # 处理当前Frame
            if (current_frame := self.__video_stream.read()[1]) is not None:
                current_frame = cv2.cvtColor(current_frame, cv2.COLOR_BGR2RGB)
                if current_frame.shape[0] != surface.get_width() or current_frame.shape[1] != surface.get_height():
                    current_frame = cv2.resize(current_frame, surface.get_size())
                pygame.surfarray.blit_array(surface, current_frame.swapaxes(0, 1))


# 类似Wallpaper Engine的视频背景，但音乐不与画面同步
class VideoSurface(AbstractVideo):
    def __init__(
        self,
        path: str,
        loop: bool = True,
        with_audio: bool = True,
        play_range: tuple[int, int] = (0, -1),
        buffer_num: int = 10,
    ) -> None:
        super().__init__(path, buffer_num, play_range)
        self.__loop: bool = loop
        self.__looped_times: int = 0
        self.__audio = Sound.load_from_video(path) if with_audio is True else None
        self.__audio_channel = None

    # 返回一个复制
    def copy(self) -> object:
        with_audio = True if self.__audio is not None else False
        new_t = VideoSurface(self._path, self.__loop, with_audio, self.play_range)
        if with_audio is True:
            new_t.set_volume(self.get_volume())
        return new_t

    # 音量
    @property
    def volume(self) -> float:
        return self.__audio.get_volume()

    def get_volume(self) -> float:
        return self.__audio.get_volume()

    def set_volume(self, value: float) -> None:
        if self.__audio is not None:
            self.__audio.set_volume(value)

    def stop(self) -> None:
        super().stop()
        self.__audio_channel.stop()

    def _init(self) -> None:
        super()._init()
        self.__audio_channel = Sound.find_channel()

    # 把画面画到surface上
    def draw(self, surface: ImageSurface) -> None:
        super().draw(surface)
        if self.is_playing():
            # 播放背景音乐
            if not self.__audio_channel.get_busy() and self.__audio is not None:
                self.__audio_channel.play(self.__audio)
            # 检测循环
            if self.get_frame_index() < self.get_frame_num():
                # 如果有设置末端且当前已经超出末端
                if self._ending_point >= 0 and self.get_frame_index() >= self._ending_point:
                    self.__looped_times += 1
                    if not self.__loop:
                        self.stop()
                    else:
                        self.set_frame_index(self._starting_point)
            else:
                # 如果不需要再次循环
                if not self.__loop:
                    self.stop()
                # 如果需要再次循环，则从self._starting_point重新开始
                else:
                    self.set_frame_index(self._starting_point)


# 视频播放器，强制视频和音乐同步
class VideoPlayer(AbstractVideo):
    def __init__(self, path: str, buffer_num: int = 6):
        super().__init__(path, buffer_num=buffer_num)
        self.__clock = pygame.time.Clock()
        self.__audio_path: str = ""

    # 返回一个复制
    def copy(self) -> object:
        return VideoPlayer(self._path, self._frame_buffer_num)

    # 设置帧坐标
    def set_frame_index(self, num: int) -> None:
        super().set_frame_index(num)
        Music.restart()
        Music.set_pos(self.get_frame_index() / self._frame_rate)

    def stop(self) -> None:
        super().stop()
        Music.unload()
        os.remove(self.__audio_path)

    def _init(self) -> None:
        super()._init()
        self.__audio_path = Music.load_from_video(self._path)
        Music.play()

    # 提前初始化
    def pre_init(self) -> None:
        self._init()

    # 把画面画到surface上
    def draw(self, surface: ImageSurface) -> None:
        super().draw(surface)
        if self.is_playing():
            if (
                self.get_frame_index() <= self.get_frame_num()
                and (current_frame_index_based_on_music := round(Music.get_pos() / 1000 * self._frame_rate))
                <= self.get_frame_num()
            ):
                frame_difference: int = int(current_frame_index_based_on_music - self.get_frame_index())
                # 如果播放速度太慢
                if frame_difference >= self._frame_buffer_num:
                    self.set_frame_index(current_frame_index_based_on_music)
                # 如果播放速度太快
                elif frame_difference < 0:
                    self.__clock.tick(self._frame_rate)
            else:
                self.stop()
