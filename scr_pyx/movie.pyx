# cython: language_level=3
import os, queue, threading
from math import ceil
import av, pygame
from ..scr_core.surface import ProgressBar,ImageSurface,get_setting

cdef getAudioFromVideo(moviePath:str, audioType:str="mp3"):
    #如果没有Cache文件夹，则创建一个
    if not os.path.exists("Cache"): os.makedirs("Cache")
    #获取路径
    outPutPath = "Cache/{0}.{1}".format(os.path.basename(moviePath).replace(".","_"),audioType)
    #如果路径已经存在，则直接返回路径
    if os.path.exists(outPutPath): return outPutPath
    #把视频载入到流容器中
    input_container = av.open(moviePath)
    input_stream = input_container.streams.audio[0]
    input_stream.thread_type = 'AUTO'
    #创建输出的容器
    output_container = av.open(outPutPath, 'w')
    output_stream = output_container.add_stream(audioType)
    cdef object frame,packet
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

def loadAudioAsSound(moviePath:str):
    path = getAudioFromVideo(moviePath)
    PygameAudio = pygame.mixer.Sound(path)
    if not get_setting("KeepVedioCache"): os.remove(path)
    return PygameAudio

def loadAudioAsMusic(moviePath:str):
    pygame.mixer.music.unload()
    path = getAudioFromVideo(moviePath)
    pygame.mixer.music.load(path)
    if not get_setting("KeepVedioCache"): os.remove(path)

#视频模块接口，不能实例化
class AbstractVedio(threading.Thread):
    def __init__(self, path:str, width:int, height:int):
        threading.Thread.__init__(self)
        self._path = path
        self._video_container = av.open(self._path,mode='r')
        self._video_stream = self._video_container.streams.video[0]
        self._video_stream.thread_type = 'AUTO'
        self._audio_stream = self._video_container.streams.audio[0]
        self._audio_stream.thread_type = 'AUTO'
        self._frameRate = ceil(self._video_stream.average_rate)
        self._frameQueue = queue.Queue(maxsize=self._frameRate)
        self._stopped = False
        self._clock = pygame.time.Clock()
        self._width = width
        self._height = height
        self._pts = 0
        self._threadLock = threading.Lock()
    def get_frameNum(self) -> int: return self._video_stream.frames
    def get_frameRate(self) -> int: return self._frameRate
    def get_pos(self) -> float: return self._pts*self._video_stream.time_base
    def get_frameIndex(self) -> int: return round(self._pts*self._video_stream.time_base*self._frameRate)
    def get_percentagePlayed(self) -> float: return self._pts/self._video_stream.duration
    def stop(self): self._stopped = True
    def _processFrame(self,frame):
        while self._frameQueue.full():
            pass
        #加锁，防止self.set_pos()误触self._pts
        self._threadLock.acquire()
        self._pts = frame.pts
        self._threadLock.release()
        array = frame.to_ndarray(width=self._width,height=self._height,format='rgb24')
        array = array.swapaxes(0,1)
        self._frameQueue.put(array)
    def display(self,screen): pygame.surfarray.blit_array(screen, self._frameQueue.get())

#视频片段展示模块--灵活，但不能保证帧数和音乐同步
class VedioFrame(AbstractVedio):
    def __init__(self, path:str, width:int, height:int, loop:int=True, with_music:int=False, play_range:tuple=None, volume:float=1):
        AbstractVedio.__init__(self,path,width,height)
        self.loop = loop
        self.looped_times = 0
        self.bgm = loadAudioAsSound(path) if with_music else None
        self.volume = volume
        if self.volume != 1 and self.bgm != None:
            self.bgm.set_volume(self.volume)
        self.bgm_channel = pygame.mixer.find_channel() if with_music else None
        self.start_point = play_range[0] if play_range != None else None
        self.end_point = play_range[1] if play_range != None else None
    def set_pos(self,float offset):
        self._video_container.seek(int(offset/self._video_stream.time_base),any_frame=True,stream=self._video_stream)
        self._frameQueue.queue.clear()
    def run(self):
        for frame in self._video_container.decode(self._video_stream):
            if self._stopped:
                break
            self._processFrame(frame)
            if self.end_point != None and self.get_pos() >= self.end_point:
                self.looped_times += 1
                if self.loop != True:
                    self._stopped = True
                else:
                    self.set_pos(self.start_point)
            self._clock.tick(self._frameRate)
    def draw(self,screen): self.display(screen)
    def display(self,screen):
        super().display(screen)
        if self.bgm != None and not self.bgm_channel.get_busy() and self.loop == True:
            self.bgm_channel.play(self.bgm)
    def clone(self):
        with_music = True if self.bgm != None else False
        return VedioFrame(self._path,self._width,self._height,self.loop,with_music,(self.start_point,self.end_point),self.volume)
    def set_volume(self,float value):
        if self.bgm != None:
            self.volume = value
            self.bgm.set_volume(value)

#视频播放系统模块--强制帧数和音乐同步，但不灵活
class VedioPlayer(AbstractVedio):
    def __init__(self,path:str,width:int,height:int):
        AbstractVedio.__init__(self,path,width,height)
        self.__allowFrameDelay = 10
        loadAudioAsMusic(path)
    def run(self):
        pygame.mixer.music.play()
        for frame in self._video_container.decode(self._video_stream):
            if self._stopped:
                break
            self._processFrame(frame)
            if not int(pygame.mixer.music.get_pos()/1000*self._frameRate)-self.get_frameIndex() >= self.__allowFrameDelay:
                self._clock.tick(self._frameRate)
        pygame.mixer.music.unload()

#过场动画
def cutscene(screen,videoPath):
    #初始化部分参数
    cdef (int, int) screen_size = screen.get_size()
    cdef int is_skip = 0
    cdef int is_playing = 0
    cdef int temp_alpha
    #初始化跳过按钮的参数
    skip_button = ImageSurface(
        pygame.image.load("Assets/image/UI/dialog_skip.png").convert_alpha(),
        int(screen.get_width()*0.92),
        int(screen.get_height()*0.05),
        int(screen.get_width()*0.055),
        int(screen.get_height()*0.06)
        )
    #生成黑色帘幕
    black_bg = pygame.Surface((screen_size[0],screen_size[1]),flags=pygame.SRCALPHA).convert_alpha()
    pygame.draw.rect(black_bg,(0,0,0),(0,0,screen_size[0],screen_size[1]))
    black_bg.set_alpha(0)
    #进度条
    cdef int bar_height = 10
    white_progress_bar = ProgressBar(bar_height,screen_size[1]-bar_height*2,screen_size[0]-bar_height*2,bar_height,"white")
    #创建视频文件
    VIDEO = VedioPlayer(videoPath,screen_size[0],screen_size[1])
    VIDEO.start()
    #播放主循环
    while is_playing == 0:
        if VIDEO.is_alive():
            VIDEO.display(screen)
            skip_button.draw(screen)
            white_progress_bar.percentage = VIDEO.get_percentagePlayed()
            white_progress_bar.draw(screen)
            events_of_mouse_click = pygame.event.get(pygame.MOUSEBUTTONDOWN)
            if len(events_of_mouse_click) > 0:
                for event in events_of_mouse_click:
                    if event.button == 1:
                        if skip_button.isHover() and is_skip == 0:
                            is_skip = 1
                            pygame.mixer.music.fadeout(5000)
                        break
            if is_skip == 1:
                temp_alpha = black_bg.get_alpha()
                if temp_alpha < 255:
                    black_bg.set_alpha(temp_alpha+5)
                else:
                    is_playing = 1
                    VIDEO.stop()
                screen.blit(black_bg,(0,0))
            pygame.display.flip()
        else:
            break