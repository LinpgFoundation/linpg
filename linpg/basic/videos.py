import subprocess

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
    __PATH: Final[str] = os.path.join("ThirdPartyLibraries", Specification.get("ThirdPartyLibraries", "ffmpeg"))

    # 检测文件是否存在
    @classmethod
    def __check_path(cls, input_path: str) -> None:
        if not os.path.exists(input_path):
            raise EXCEPTION.FileNotExists()
        elif not os.path.exists(cls.__PATH):
            raise EXCEPTION.ToolIsMissing()

    # 是否opencv模块已经初始化且路径存在
    @staticmethod
    def validation(_path: str) -> None:
        # 如果opencv没有成功地导入
        if not _OPENCV_INITIALIZED:
            EXCEPTION.fatal("You cannot use any video module unless you install opencv!", 4)
        # 确保路径存在
        elif not os.path.exists(_path):
            EXCEPTION.fatal(f'Cannot find file on path: "{_path}"')

    # 使用ffmpeg直接转换文件
    @classmethod
    def convert(cls, input_path: str, output_path: str) -> None:
        # 检测文件是否存在
        cls.__check_path(input_path)
        # 转换
        subprocess.check_call([cls.__PATH, "-i", input_path, output_path], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    # 使用ffmpeg转换视频文件至音乐文件
    @classmethod
    def convert_from_video_to_audio(cls, input_path: str, output_path: str) -> None:
        # 检测文件是否存在
        cls.__check_path(input_path)
        # 转换
        if output_path.endswith(".ogg"):
            subprocess.check_call(
                [cls.__PATH, "-i", input_path, "-vn", "-acodec", "libvorbis", "-y", output_path], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
            )
        else:
            subprocess.check_call([cls.__PATH, "-i", input_path, "-vn", output_path], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    # 获取视频封面
    @classmethod
    def get_thumbnail(cls, path: str, size: Optional[tuple[int, int]] = None) -> ImageSurface:
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
    def split_audio(cls, input_path: str, audio_type: str = "ogg") -> str:
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
        try:
            # 生成视频文件
            cls.convert_from_video_to_audio(input_path, output_path)
            # 如果一切正常，返回output路径
            return output_path
        # 如果不正常...
        except EXCEPTION.FileNotExists:
            EXCEPTION.fatal(f'Cannot find media file on path "{input_path}".')
        except EXCEPTION.ToolIsMissing:
            EXCEPTION.fatal(
                f'To split audio from video, "ffmpeg.exe" needs to be placed under directory "{os.path.dirname(cls.__PATH)}" inside your project. FFmpeg is never a part of Linpg Engine.'
            )
