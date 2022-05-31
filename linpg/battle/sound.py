from .icon import *

# 角色音效管理系统
class EntitySoundManager:

    # 存放音效的字典
    __SOUNDS: dict = {}

    # 为角色创建用于储存音效的文件夹
    @staticmethod
    def mkdir() -> None:
        for each_character in os.listdir(EntitySpriteImageManager.SPRITES_PATH):
            if not os.path.exists(_path := Specification.get_directory("character_sound", each_character)):
                os.mkdir(_path)
                os.mkdir(os.path.join(_path, "attack"))
                os.mkdir(os.path.join(_path, "get_click"))
                os.mkdir(os.path.join(_path, "injured"))
                os.mkdir(os.path.join(_path, "skill"))

    # 加载音效
    @classmethod
    def add(cls, characterType: str) -> None:
        if characterType not in cls.__SOUNDS and os.path.exists(Specification.get_directory("character_sound", characterType)):
            cls.__SOUNDS[characterType] = {}
            for soundType in os.listdir(Specification.get_directory("character_sound", characterType)):
                cls.__SOUNDS[characterType][soundType] = []
                for soundPath in glob(Specification.get_directory("character_sound", characterType, soundType, "*")):
                    cls.__SOUNDS[characterType][soundType].append(Sound.load(soundPath))

    # 播放角色音效
    @classmethod
    def play(cls, characterType: str, soundType: str) -> None:
        if LINPG_RESERVED_SOUND_EFFECTS_CHANNEL is not None:
            _point = cls.__SOUNDS.get(characterType)
            if _point is not None:
                sound_list = _point.get(soundType)
                if sound_list is not None and len(sound_list) > 0:
                    sound = sound_list[get_random_int(0, len(sound_list) - 1) if len(sound_list) > 1 else 0]
                    sound.set_volume(Media.volume.effects / 100.0)
                    LINPG_RESERVED_SOUND_EFFECTS_CHANNEL.play(sound)
