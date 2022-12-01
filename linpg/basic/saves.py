import threading
from dataclasses import dataclass

from .font import *

# 持久数据管理IO
class PersistentData(TypeSafeGetter, TypeSafeSetter):

    __DATA: Final[dict[str, Any]] = {}
    __PATH: Final[str] = Specification.get_directory("save", "persistent." + Config.get_file_type())

    @classmethod
    def _get_data(cls) -> dict:
        return cls.__DATA

    @classmethod
    def set(cls, *_key: str, value: Any, assumeKeyExists: bool = False) -> None:
        super().set(*_key, value=value, assumeKeyExists=assumeKeyExists)
        cls.save()

    @classmethod
    def reload(cls) -> None:
        cls.__DATA.clear()
        if os.path.exists(cls.__PATH):
            cls.__DATA.update(Config.load_file(cls.__PATH))

    @classmethod
    def save(cls) -> None:
        if len(cls.__DATA) > 0:
            Config.save(cls.__PATH, cls.__DATA)
        else:
            Files.delete_if_exist(cls.__PATH)


# 初始化持久数据库
PersistentData.reload()


# 存档系统
class Saves:

    # 存档数据
    @dataclass
    class Progress:
        data: dict
        screenshot: ImageSurface
        createdAt: str
        slotId: int

    # 是否有至少一个存档存在
    @staticmethod
    def any_progress_exists() -> bool:
        return len(glob(Specification.get_directory("save", "*.linpg.save"))) > 0

    # 获取全部存档
    @classmethod
    def get_progresses(cls) -> dict[int, Progress]:
        progresses: dict[int, Saves.Progress] = {}
        for _save in glob(Specification.get_directory("save", "*.linpg.save")):
            _file: Saves.Progress = cls.load(_save)
            progresses[_file.slotId] = _file
        return progresses

    # 获取最近的一次存档
    @classmethod
    def get_latest_progresses(cls) -> Progress:
        progresses: dict[int, Saves.Progress] = cls.get_progresses()
        latest: Optional[Saves.Progress] = None
        for _progress in progresses.values():
            if latest is None or datetime.strptime(latest.createdAt, "%Y-%m-%d %H:%M %p") < datetime.strptime(_progress.createdAt, "%Y-%m-%d %H:%M %p"):
                latest = _progress
        if latest is None:
            EXCEPTION.fatal("No progress exists!")
        return latest

    # 保存存档
    @classmethod
    def __save(cls, _path: str, _data: dict, _screenshot: ImageSurface, slotId: int) -> None:
        # 保存存档文件到本地
        Config.save("data.json", _data)
        Config.save("info.json", {"createdAt": datetime.now().strftime("%Y-%m-%d %H:%M %p"), "slotId": slotId})
        Images.save(_screenshot, "screenshot.png")
        # 将存档文件写入zip文件中
        with zipfile.ZipFile(_path, "w") as zipped_f:
            zipped_f.write("data.json")
            zipped_f.write("info.json")
            zipped_f.write("screenshot.png")
        # 删除本地文件
        Files.delete_if_exist("data.json")
        Files.delete_if_exist("info.json")
        Files.delete_if_exist("screenshot.png")

    @classmethod
    def save(cls, _data: dict, _screenshot: ImageSurface, slotId: int) -> None:
        # 确保储存数据的文件夹存在
        os.makedirs(Specification.get_directory("save"), exist_ok=True)
        save_thread = threading.Thread(
            target=cls.__save,
            args=(Specification.get_directory("save", "save_{}.linpg.save".format(slotId)), _data, _screenshot, slotId),
        )
        # 多线程保存数据
        save_thread.daemon = True
        save_thread.start()
        save_thread.join()

    # 取得存档
    @classmethod
    def load(cls, _path: str) -> Progress:
        # 打开zip文件并读取信息
        zipFile: zipfile.ZipFile = zipfile.ZipFile(_path)
        _data: dict = json.load(io.BytesIO(zipFile.read("data.json")))
        _screenshot: ImageSurface = Images.fromBytesIO(io.BytesIO(zipFile.read("screenshot.png")))
        _info: dict = json.load(io.BytesIO(zipFile.read("info.json")))
        # 断开对zip文件的访问
        zipFile.close()
        # 返回数据
        return cls.Progress(_data, _screenshot, str(_info["createdAt"]), int(_info["slotId"]))
