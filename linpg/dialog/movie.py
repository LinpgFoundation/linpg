# cython: language_level=3
import queue
import av
from ..core import *

#获取视频的音频 （返回路径）
def getAudioFromVideo(moviePath:str, audioType:str="mp3") -> str:
    #如果没有Cache文件夹，则创建一个
    if not os.path.exists("Cache"): os.makedirs("Cache")
    #获取路径
    outPutPath:str = os.path.join("Cache","{0}.{1}".format(os.path.basename(moviePath).replace(".","_"),audioType))
    #如果路径已经存在，则直接返回路径
    if os.path.exists(outPutPath): return outPutPath
    #把视频载入到流容器中
    input_container:object = av.open(moviePath)
    input_stream:object = input_container.streams.audio[0]
    input_stream.thread_type = 'AUTO'
    #创建输出的容器
    output_container = av.open(outPutPath, 'w')
    output_stream = output_container.add_stream(audioType)
    #把input容器中的音乐片段载入到输出容器中
    for frame in input_container.decode(input_stream):
        frame.pts = None
        for packet in output_stream.encode(frame):
            output_container.mux(packet)
    #关闭input容器
    input_container.close()
    #解码输出容器
    for packet in output_stream.encode(None):
        output_container.mux(packet)
    #写入工作完成，关闭输出容器
    output_container.close()
    #读取完成，返回音乐文件的对应目录
    return outPutPath

def loadAudioAsSound(moviePath:str) -> object:
    path = getAudioFromVideo(moviePath)
    PygameAudio = pygame.mixer.Sound(path)
    if not get_setting("KeepVedioCache"): os.remove(path)
    return PygameAudio

def loadAudioAsMusic(moviePath:str) -> bool:
    pygame.mixer.music.unload()
    try:
        path = getAudioFromVideo(moviePath)
        pygame.mixer.music.load(path)
        if not get_setting("KeepVedioCache"): os.remove(path)
        return True
    except:
        throwException("warning", "Cannot load music from {}!\nIf this vedio has no sound, then just ignore this warning.".format(moviePath))
        return False

#视频模块接口，不能实例化
class AbstractVedio(threading.Thread):
    def __init__(self, path:str, width:int, height:int):
        super().__init__()
        self._path = path
        self._video_container = av.open(self._path,mode='r')
        self._video_stream = self._video_container.streams.video[0]
        self._video_stream.thread_type = 'AUTO'
        #self._audio_stream = self._video_container.streams.audio[0]
        #self._audio_stream.thread_type = 'AUTO'
        self._frameRate = round(self._video_stream.average_rate)
        self._frameQueue = queue.Queue(maxsize=self._frameRate)
        self._stopped:bool = False
        self._clock = pygame.time.Clock()
        self._width = width
        self._height = height
        self._pts = 0
        self._threadLock = threading.Lock()
    #处理当前帧的画面
    def _processFrame(self, frame:object):
        #如果当前队列是满的，则等待
        while self._frameQueue.full(): pass
        #加锁，防止self.set_pos()误触self._pts
        self._threadLock.acquire()
        self._pts = frame.pts
        self._threadLock.release()
        array = frame.to_ndarray(width=self._width,height=self._height,format='rgb24')
        array = array.swapaxes(0,1)
        self._frameQueue.put(array)
    """获取信息"""
    def get_frameNum(self) -> int: return self._video_stream.frames
    def get_frameRate(self) -> int: return self._frameRate
    def get_pos(self) -> float: return self._pts*self._video_stream.time_base
    def get_frameIndex(self) -> int: return round(self._pts*self._video_stream.time_base*self._frameRate)
    def get_percentagePlayed(self) -> float: return self._pts/self._video_stream.duration
    #停止
    def stop(self) -> None: self._stopped = True
    #把画面画到屏幕上
    def draw(self, surface:pygame.Surface) -> None:
        pygame.surfarray.blit_array(surface,self._frameQueue.get())

#视频片段展示模块--灵活，但不能保证帧数和音乐同步
class VedioFrame(AbstractVedio):
    def __init__(self, path:str, width:int, height:int, loop:bool=True, with_music:bool=False, play_range:tuple=None, volume:float=1.0):
        super().__init__(path,width,height)
        self.loop = loop
        self.looped_times = 0
        self.bgm = loadAudioAsSound(path) if with_music else None
        self.__volume = volume
        #如果初始音量不为1，则应该设置对应的音量
        if self.__volume != 1.0 and self.bgm is not None: self.bgm.set_volume(self.__volume)
        self.bgm_channel = pygame.mixer.find_channel() if with_music else None
        self.start_point = play_range[0] if play_range is not None else None
        self.end_point = play_range[1] if play_range is not None else None
        self.started:bool = False
    #音量
    def get_volume(self) -> float: return self.__volume
    def set_volume(self, value:float) -> None:
        if self.bgm is not None:
            self.__volume = value
            self.bgm.set_volume(self.__volume)
    #设置播放的位置
    def set_pos(self, offset:float) -> None:
        self._video_container.seek(int(offset/self._video_stream.time_base),any_frame=True,stream=self._video_stream)
        self._frameQueue.queue.clear()
    #返回一个克隆
    def copy(self) -> object:
        with_music = True if self.bgm is not None else False
        return VedioFrame(self._path,self._width,self._height,self.loop,with_music,(self.start_point,self.end_point),self.__volume)
    #开始执行线程
    def run(self) -> None:
        self.started = True
        for frame in self._video_container.decode(self._video_stream):
            #如果要中途停止
            if self._stopped is True: break
            #处理当前Frame
            self._processFrame(frame)
            if self.end_point is not None and self.get_pos() >= self.end_point:
                self.looped_times += 1
                if not self.loop:
                    self._stopped = True
                else:
                    self.set_pos(self.start_point)
            self._clock.tick(self._frameRate)
    #把画面画到屏幕上
    def draw(self, surface:pygame.Surface) -> None:
        super().draw(surface)
        #播放背景音乐
        if self.bgm is not None and not self.bgm_channel.get_busy() and self.loop: self.bgm_channel.play(self.bgm)

#视频播放系统模块--强制帧数和音乐同步，但不灵活
class VedioPlayer(AbstractVedio):
    def __init__(self, path:str, width:int, height:int):
        super().__init__(path,width,height)
        self.__allowFrameDelay:int = 10
        self.__bgm_status:bool = loadAudioAsMusic(path)
    #开始执行线程
    def run(self) -> None:
        if self.__bgm_status is True: pygame.mixer.music.play()
        for frame in self._video_container.decode(self._video_stream):
            #如果需要跳出
            if self._stopped: break
            #处理当前帧
            self._processFrame(frame)
            #确保匀速播放
            if not int(pygame.mixer.music.get_pos()/1000*self._frameRate)-self.get_frameIndex() >= self.__allowFrameDelay:
                self._clock.tick(self._frameRate)
        pygame.mixer.music.unload()

#过场动画
def cutscene(surface:pygame.Surface, videoPath:str) -> None:
    #初始化部分参数
    surface_size:tuple = surface.get_size()
    is_skip:bool = False
    is_playing:bool = True
    #初始化跳过按钮的参数
    skip_button:object = ImageSurface(
        pygame.image.load("Assets/image/UI/dialog_skip.png").convert_alpha(),
        int(surface.get_width()*0.92),
        int(surface.get_height()*0.05),
        int(surface.get_width()*0.055),
        int(surface.get_height()*0.06)
        )
    #生成黑色帘幕
    black_bg:pygame.Surface = pygame.Surface(surface_size,flags=pygame.SRCALPHA).convert_alpha()
    pygame.draw.rect(black_bg,(0,0,0),(0,0,surface_size[0],surface_size[1]))
    black_bg.set_alpha(0)
    #进度条
    bar_height:int = 10
    white_progress_bar:object = ProgressBar(bar_height,surface_size[1]-bar_height*2,surface_size[0]-bar_height*2,bar_height,"white")
    #创建视频文件
    VIDEO:object = VedioPlayer(videoPath,surface_size[0],surface_size[1])
    VIDEO.start()
    #播放主循环
    while is_playing is True and VIDEO.is_alive():
        VIDEO.draw(surface)
        skip_button.draw(surface)
        white_progress_bar.percentage = VIDEO.get_percentagePlayed()
        white_progress_bar.draw(surface)
        events_of_mouse_click = pygame.event.get(pygame.MOUSEBUTTONDOWN)
        if len(events_of_mouse_click) > 0:
            for event in events_of_mouse_click:
                if event.button == 1:
                    if skip_button.is_hover() and not is_skip:
                        is_skip = True
                        pygame.mixer.music.fadeout(5000)
                    break
        if is_skip is True:
            temp_alpha:int = black_bg.get_alpha()
            if temp_alpha < 255:
                black_bg.set_alpha(temp_alpha+5)
            else:
                is_playing = False
                VIDEO.stop()
            surface.blit(black_bg,(0,0))
        pygame.display.flip()