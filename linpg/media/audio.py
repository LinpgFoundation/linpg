# cython: language_level=3

import queue
import av
from ..ui import *

#获取视频的音频 （返回路径）
def split_audio_from_video(moviePath:str, audioType:str="mp3") -> str:
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

def load_audio_from_video_as_sound(moviePath:str) -> object:
    path = split_audio_from_video(moviePath)
    sound_audio = load_sound(path)
    if not get_setting("KeepVedioCache"): os.remove(path)
    return sound_audio

def load_audio_from_video_as_music(moviePath:str) -> bool:
    unload_music()
    try:
        path = split_audio_from_video(moviePath)
        load_music(path)
        if not get_setting("KeepVedioCache"): os.remove(path)
        return True
    except BaseException:
        throw_exception("warning", "Cannot load music from {}!\nIf this vedio has no sound, then just ignore this warning.".format(moviePath))
        return False