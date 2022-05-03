from .icon import *

# 角色音效管理系统
class EntitySoundManager:

    # 音效所在的路径
    __CHARACTER_SOUNDS_PATH: str = os.path.join("Assets", "sound", "character")
    # 存放音效的字典
    __SOUNDS: dict = {}

    # 为角色创建用于储存音效的文件夹
    @classmethod
    def mkdir(cls) -> None:
        for each_character in os.listdir(EntitySpriteImageManager.SPRITES_PATH):
            path = os.path.join(cls.__CHARACTER_SOUNDS_PATH, each_character)
            if not os.path.exists(path):
                os.mkdir(path)
                os.mkdir(os.path.join(path, "attack"))
                os.mkdir(os.path.join(path, "get_click"))
                os.mkdir(os.path.join(path, "injured"))
                os.mkdir(os.path.join(path, "skill"))

    # 加载音效
    @classmethod
    def add(cls, characterType: str) -> None:
        if characterType not in cls.__SOUNDS and os.path.exists(os.path.join(cls.__CHARACTER_SOUNDS_PATH, characterType)):
            cls.__SOUNDS[characterType] = {}
            for soundType in os.listdir(os.path.join(cls.__CHARACTER_SOUNDS_PATH, characterType)):
                cls.__SOUNDS[characterType][soundType] = []
                for soundPath in glob(os.path.join(cls.__CHARACTER_SOUNDS_PATH, characterType, soundType, "*")):
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
