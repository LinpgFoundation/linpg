from .builder import *

# 视频转换系统
class VideoConverterSystem(AbstractToolSystem):
    def __init__(self) -> None:
        super().__init__("4.4", os.path.join(self._TOOL_FOLDER, self._TOOL_LIBRARIES["ffmpeg"]))

    # 使用ffmpeg直接转换文件
    def convert(self, input_path: str, output_path: str) -> None:
        # 检测文件是否存在
        self._check_path(input_path)
        # 转换
        self._run_cmd(["-i", input_path, output_path])

    # 使用ffmpeg转换视频文件至音乐文件
    def convert_from_video_to_audio(self, input_path: str, output_path: str) -> None:
        # 检测文件是否存在
        self._check_path(input_path)
        # 转换
        if output_path.endswith(".ogg"):
            self._run_cmd(["-i", input_path, "-vn", "-acodec", "libvorbis", "-y", output_path])
        else:
            self._run_cmd(["-i", input_path, "-vn", output_path])


VideoConverter: VideoConverterSystem = VideoConverterSystem()
