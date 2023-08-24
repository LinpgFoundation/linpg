import av

# 尝试导入opencv库
_OPENCV_INITIALIZED: bool = False
try:
    import cv2  # type: ignore

    _OPENCV_INITIALIZED = True
except ImportError:
    pass

from .display import *


# 视频转换系统
class Videos(ABC):
    # 是否opencv模块已经初始化且路径存在
    @staticmethod
    def validation(_path: str) -> None:
        # 如果opencv没有成功地导入
        if not _OPENCV_INITIALIZED:
            EXCEPTION.fatal("You cannot use any video module unless you install opencv!", 4)
        # 确保路径存在
        elif not os.path.exists(_path):
            EXCEPTION.fatal(f'Cannot find file on path: "{_path}"')

    # 获取视频封面
    @classmethod
    def get_thumbnail(cls, path: str, size: tuple[int, int] | None = None) -> ImageSurface:
        cls.validation(path)
        video_stream = cv2.VideoCapture(path)
        video_stream.set(cv2.CAP_PROP_POS_FRAMES, video_stream.get(cv2.CAP_PROP_FRAME_COUNT) // 10)
        current_frame = cv2.cvtColor(video_stream.read()[1], cv2.COLOR_BGR2RGB)
        video_stream.release()
        del video_stream
        if size is not None and (current_frame.shape[0] != size[0] or current_frame.shape[1] != size[1]):
            current_frame = cv2.resize(current_frame, size)
        return Surfaces.from_array(current_frame)

    # 获取视频的音频 （返回路径）
    @classmethod
    def split_audio(cls, input_path: str, audio_type: str = "ogg", codecs: str = "libvorbis") -> str:
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
        output_path: str = os.path.join(Cache.get_directory(), output_file_name)
        # 检测文件是否存在
        if not os.path.exists(input_path):
            EXCEPTION.fatal(f'Cannot find media file on path "{input_path}".')
        # 生成音频文件
        with av.open(input_path, "r") as inp:
            with av.open(output_path, "w", audio_type) as out:
                out_stream = out.add_stream(codecs)
                for frame in inp.decode(audio=0):
                    frame.pts = None
                    for packets in out_stream.encode(frame):
                        out.mux(packets)
                for packets in out_stream.encode(None):
                    out.mux(packets)
        # 返回output路径
        return output_path
