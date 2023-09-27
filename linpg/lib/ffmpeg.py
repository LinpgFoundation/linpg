import os
import subprocess


class FFmpeg:
    @staticmethod
    def execute(*cmds: str) -> None:
        if os.name == "nt":
            subprocess.check_call([os.path.join(os.path.dirname(__file__), "ffmpeg.exe"), *cmds], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        else:
            try:
                subprocess.check_call(["ffmpeg", *cmds], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            except Exception:
                from ..exception import EXCEPTION

                EXCEPTION.fatal("FFmpeg is necessary and have to be installed if you are currently running non-windows system such as linux!")

    @classmethod
    def convert(cls, input_path: str, output_path: str, nv: bool = False) -> None:
        if nv:
            cls.execute("-i", input_path, "-vn", "-y", output_path)
        else:
            cls.execute("-i", input_path, output_path)
