# cython: language_level=3
import cv2
from ..ui import *

class VedioSurface(threading.Thread):
    def __init__(self, path: str, loop: bool = True, play_range: tuple[int] = (0, -1)):
        super().__init__()
        self._path:str = path
        #确保路径存在
        if not os.path.exists(self._path): EXCEPTION.fatal('Cannot find file on path: "{}"'.format(self._path))
        """视频流"""
        self.__video_stream:cv2.VideoCapture = None
        self.__frame_rate:int = -1
        self.__frame_deque:deque = deque()
        """内部参数"""
        self._clock = get_clock()
        self.__stopped:bool = False
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
        self.__video_stream = cv2.VideoCapture(self._path)
        #如果设置了起点，则为视频设置开始播放的位置
        if self.__starting_point > 0: self.set_frame_index(self.__starting_point)
        #获取秒帧数
        self.__frame_rate = int(self.__video_stream.get(cv2.CAP_PROP_FPS))
        #初始化用于储存帧的deque
        self.__frame_deque = deque(maxlen=self.__frame_rate)
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
    def frame_num(self) -> int: return self.__video_stream.get(cv2.CAP_PROP_FRAME_COUNT)
    def get_frame_num(self) -> int: return self.__video_stream.get(cv2.CAP_PROP_FRAME_COUNT)
    #当前帧坐标
    @property
    def frame_index(self) -> int: return self.__video_stream.get(cv2.CAP_PROP_POS_FRAMES)
    def get_frame_index(self) -> int: return self.__video_stream.get(cv2.CAP_PROP_POS_FRAMES)
    def set_frame_index(self, num:int) -> None:
        self.__video_stream.set(cv2.CAP_PROP_POS_FRAMES, num)
        self.__frame_deque.clear()
    #已经播放的百分比
    @property
    def percentage(self) -> float: return self.frame_index/self.frame_num
    def get_percentage_played(self) -> float: return self.frame_index/self.frame_num
    #停止
    def stop(self) -> None: self.__stopped = True
    #是否已经开始
    @property
    def started(self) -> bool: return self.__started
    #播放范围
    def play_range(self) -> tuple[int]: return (self.__starting_point, self.__ending_point)
    #返回一个复制
    def copy(self) -> object: return VedioSurface(self._path, self.__loop, self.play_range)
    #是否用于存储frame的双向列表是空的
    def _is_frame_deque_not_empty(self) -> bool: return len(self.__frame_deque) > 0
    #处理当前帧的画面
    def _process(self):
        #获取帧
        frame = self.__video_stream.read()[1]
        self.__frame_deque.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).swapaxes(0,1))
    #开始执行线程
    def run(self) -> None:
        self._init()
        #循环处理帧直至播放完或者跳出
        while self.frame_index <= self.frame_num:
            #如果要中途停止
            if self.__stopped is True:
                #清空deque内储存的所有加载完的帧
                self.__frame_deque.clear()
                break
            else:
                #处理当前Frame
                self._process()
                if self.__ending_point >= 0 and self.frame_index >= self.__ending_point:
                    self.__looped_times += 1
                    if not self.__loop:
                        self.__stopped = True
                    else:
                        self.set_frame_index(self.__starting_point)
                elif self.frame_index == self.frame_num:
                    #如果不需要再次循环或者需要中途跳出
                    if not self.__loop:
                        break
                    else:
                        self.set_frame_index(self.__starting_point)
        #确保播放完剩余的帧
        while self._is_frame_deque_not_empty(): pass
    #把画面画到surface上
    def draw(self, surface:ImageSurface) -> None:
        #如果不为空，则画出
        if self._is_frame_deque_not_empty():
            current_frame = self.__frame_deque.popleft()
            if current_frame.shape[0] != surface.get_width() or current_frame.shape[1] != surface.get_height():
                current_frame = cv2.resize(current_frame, surface.get_size())
            draw_array(surface, current_frame)

#视频模块
class VedioPlayer(VedioSurface):
    def __init__(self, path: str, volume: float = 1.0):
        super().__init__(path, False)

        """音效"""
        self.__volume:float = volume
        self.__allow_frame_delay:int = 10
        #self.__audio_stream = Sound.load_from_video(path, self.__volume) if with_music is True else None
        #self.__audio_channel:int = Sound.find_channel() if with_music else None
    #返回一个复制
    def copy(self) -> object: return VedioPlayer(self._path, self.__volume)
    #把画面画到surface上
    def draw(self, surface:ImageSurface) -> None:
        #如果不为空，则画出
        if len(self.__frame_deque) > 0: draw_array(surface, self.__frame_deque.popleft())
        #播放背景音乐
        if self.__audio_stream is not None and not self.__audio_channel.get_busy():
            self.__audio_channel.play(self.__audio_stream)
    #开始执行线程
    def run(self) -> None:
        if self.__bgm_status is True: Music.play()
        for frame in self._video_container.decode(self._video_stream):
            #如果需要跳出
            if self.__stopped is True:
                #清空deque内储存的所有加载完的帧
                with self.__frame_deque.mutex: self.__frame_deque.deque.clear()
                break
            #处理当前帧
            self._processFrame(frame)
            #确保匀速播放
            if not int(Music.get_pos()/1000*self.__frame_rate)-self.get_frameIndex() >= self.__allowFrameDelay:
                self._clock.tick(self.__frame_rate)
        #确保播放完剩余的帧
        while not self.__frame_deque.empty(): pass
        Music.unload()

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
    VIDEO:object = VedioPlayer(videoPath,surface_size[0],surface_size[1])
    VIDEO.start()
    #播放主循环
    while is_playing is True and VIDEO.is_alive() is True:
        VIDEO.draw(surface)
        skip_button.draw(surface)
        white_progress_bar.percentage = VIDEO.get_percentagePlayed()
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
