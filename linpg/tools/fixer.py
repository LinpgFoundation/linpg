from .converter import *


class ImageFixerSystem(AbstractToolSystem):
    def __init__(self) -> None:
        super().__init__("7.1.0", os.path.join(os.path.dirname(__file__), "convert.exe"))

    def fix(self, input_path: str) -> None:
        if input_path.endswith("*.png"):
            self._check_path(os.path.dirname(input_path))
            for path in glob(input_path):
                # 转换
                self._run_cmd([path])
        else:
            self._check_path(input_path)
            # 转换
            self._run_cmd([input_path])


ImageFixer: ImageFixerSystem = ImageFixerSystem()
