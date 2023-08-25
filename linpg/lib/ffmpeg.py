import os
import subprocess


class FFmpeg:
    @staticmethod
    def execute(*cmds: str):
        subprocess.check_call(
            [os.path.join(os.path.dirname(__file__), "ffmpeg.exe") if os.name == "nt" else "ffmpeg", *cmds], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
        )

    @classmethod
    def convert(cls, input_path: str, output_path: str, nv: bool = False) -> None:
        if nv:
            cls.execute("-i", input_path, "-vn", "-y", output_path)
        else:
            cls.execute("-i", input_path, output_path)
