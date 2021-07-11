# cython: language_level=3
import cv2
from ..ui import *

#类似Wallpaper Engine的视频背景，没有背景音乐
class VedioSurface(threading.Thread):
    def __init__(self, path: str, loop: bool = True, play_range: tuple[int] = (0, -1), buffer_num: int = 10):
        super().__init__()
        self._path:str = path
        #确保路径存在
        if not os.path.exists(self._path): EXCEPTION.fatal('Cannot find file on path: "{}"'.format(self._path))
        """视频流"""
        self._video_stream:cv2.VideoCapture = None
        self.__frame_rate:int = 0
        self._frame_buffer_num:int = int(buffer_num)
        """内部参数"""
        self._clock = get_clock()
        self._stopped:bool = False
        self.__started:bool = False
        """可自定义参数"""
        self.__loop:bool = loop
        self.__looped_times:int = 0
        #确保play_range参数合法
        if len(play_range) < 2: EXCEPTION.fatal('The length of play_range parameter must >= 2.')
        self.__starting_point:int = int(play_range[0])
        self.__ending_point:int = int(play_range[1])
    #初始化
    def _init(self) -> None:
        #加载视频流
        self._video_stream = cv2.VideoCapture(self._path)
        self._video_stream.set(cv2.CAP_PROP_BUFFERSIZE, self._frame_buffer_num)
        #如果设置了起点，则为视频设置开始播放的位置
        if self.__starting_point > 0: self.set_frame_index(self.__starting_point)
        #获取秒帧数
        self.__frame_rate = round(self._video_stream.get(cv2.CAP_PROP_FPS))
        #改变用于辨识视频是否开始播放的flag
        self.__started = True
    #每秒帧数
    @property
    def fps(self) -> int: return self.__frame_rate
    @property
    def frame_rate(self) -> int: return self.__frame_rate
    def get_frame_rate(self) -> int: return self.__frame_rate
    #总帧数
    @property
    def frame_num(self) -> int: return self.get_frame_num()
    def get_frame_num(self) -> int:
        return self._video_stream.get(cv2.CAP_PROP_FRAME_COUNT) if self._video_stream is not None else 0
    #当前帧坐标
    @property
    def frame_index(self) -> int: return self.get_frame_index()
    def get_frame_index(self) -> int:
        return int(self._video_stream.get(cv2.CAP_PROP_POS_FRAMES)) if self._video_stream is not None else 0
    def set_frame_index(self, num:int) -> None:
        while not self.__started: pass
        if num > self.get_frame_num(): EXCEPTION.fatal('Frame index "{1}" is out of range "{2}"'.format(num, self.get_frame_num()))
        self._video_stream.set(cv2.CAP_PROP_POS_FRAMES, num)
    #已经播放的百分比
    def get_percentage_played(self) -> float: return self.get_frame_index()/max(self.get_frame_num(), 1)
    #停止
    def stop(self) -> None:
        self._stopped = True
        self._video_stream = None
    #是否已经开始
    @property
    def started(self) -> bool: return self.__started
    #播放范围
    @property
    def play_range(self) -> tuple[int]: return (self.__starting_point, self.__ending_point)
    #返回一个复制
    def copy(self) -> object: return VedioSurface(self._path, self.__loop, self.play_range)
    #开始执行线程
    def run(self) -> None:
        self._init()
        #循环处理帧直至播放完或者跳出
        while self.get_frame_index() <= self.get_frame_num():
            #如果要中途停止
            if self._stopped is True:
                break
            else:
                if self.__ending_point >= 0 and self.get_frame_index() >= self.__ending_point:
                    self.__looped_times += 1
                    if not self.__loop:
                        self._stopped = True
                    else:
                        self.set_frame_index(self.__starting_point)
                elif self.get_frame_index() == self.get_frame_num():
                    #如果不需要再次循环或者需要中途跳出
                    if not self.__loop:
                        break
                    else:
                        self.set_frame_index(self.__starting_point)
        self._video_stream = None
    #把画面画到surface上
    def draw(self, surface:ImageSurface) -> None:
        if self.started is True and not self._stopped:
            #处理当前Frame
            current_frame = self._video_stream.read()[1]
            if current_frame is not None:
                current_frame = cv2.cvtColor(current_frame, cv2.COLOR_BGR2RGB)
                if current_frame.shape[0] != surface.get_width() or current_frame.shape[1] != surface.get_height():
                    current_frame = cv2.resize(current_frame, surface.get_size())
                draw_array(surface, current_frame.swapaxes(0,1))

#视频播放器，强制视频和音乐同步
class VedioPlayer(VedioSurface):
    def __init__(self, path: str, buffer_num: int = 6):
        super().__init__(path, False, buffer_num=buffer_num)
    #返回一个复制
    def copy(self) -> object: return VedioPlayer(self._path, self._frame_buffer_num)
    #设置帧坐标
    def set_frame_index(self, num:int) -> None:
        super().set_frame_index(num)
        pygame.mixer.music.rewind()
        Music.set_pos(self.get_frame_index()/self.get_frame_rate())
    #开始执行线程
    def run(self) -> None:
        music_path = Music.load_from_video(self._path)
        self._init()
        Music.play()
        #循环处理帧直至播放完或者跳出
        while self.get_frame_index() < self.get_frame_num():
            #如果要中途停止
            if self._stopped is True:
                break
        Music.unload()
        self._video_stream = None
        os.remove(music_path)
    #把画面画到surface上
    def draw(self, surface:ImageSurface) -> None:
        super().draw(surface)
        if self._video_stream is not None:
            current_frame_index_based_on_music: int = round(Music.get_pos()/1000*self.get_frame_rate())
            frame_difference:int = current_frame_index_based_on_music-self.get_frame_index()
            #如果播放速度太慢
            if frame_difference >= self._frame_buffer_num:
                self.set_frame_index(current_frame_index_based_on_music)
            #如果播放速度太快
            elif frame_difference < 0:
                self._clock.tick(self.get_frame_rate())

#过场动画
def cutscene(surface:ImageSurface, videoPath:str) -> None:
    #初始化部分参数
    surface_size:tuple = surface.get_size()
    is_skip:bool = False
    is_playing:bool = True
    #初始化跳过按钮的参数
    skip_button:object = StaticImage(
        r"Assets/image/UI/dialog_skip.png",
        int(surface.get_width()*0.92), int(surface.get_height()*0.05),
        int(surface.get_width()*0.055), int(surface.get_height()*0.06)
        )
    #生成黑色帘幕
    black_bg:ImageSurface = new_surface(surface_size).convert()
    black_bg.fill(Color.BLACK)
    black_bg.set_alpha(0)
    #进度条
    bar_height:int = 10
    white_progress_bar:object = ProgressBar(bar_height,surface_size[1]-bar_height*2,surface_size[0]-bar_height*2,bar_height,"white")
    #创建视频文件
    VIDEO:object = VedioPlayer(videoPath)
    VIDEO.start()
    #播放主循环
    while is_playing is True and VIDEO.is_alive() is True:
        VIDEO.draw(surface)
        skip_button.draw(surface)
        white_progress_bar.set_percentage(VIDEO.get_percentage_played())
        white_progress_bar.draw(surface)
        if skip_button.is_hover() and Controller.mouse.get_pressed(0) and not is_skip:
            is_skip = True
            Music.fade_out(5000)
        if is_skip is True:
            temp_alpha:int = black_bg.get_alpha()
            if temp_alpha < 255:
                black_bg.set_alpha(temp_alpha+5)
            else:
                is_playing = False
                VIDEO.stop()
            surface.blit(black_bg,(0,0))
        Display.flip()
