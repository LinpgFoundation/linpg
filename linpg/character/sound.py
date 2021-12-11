from .icon import *

# 角色音效管理系统
class EntitySoundManager(AbstractSoundManager):

    __CHARACTER_SOUNDS_PATH: str = os.path.join("Assets", "sound", "character")

    def __init__(self, channel_id: int):
        super().__init__(channel_id)
        self.__SOUNDS: dict = {}

    # 为角色创建用于储存音效的文件夹
    @classmethod
    def mkdir(cls) -> None:
        for each_character in os.listdir("Assets/image/character/"):
            path = os.path.join(cls.__CHARACTER_SOUNDS_PATH, each_character)
            if not os.path.exists(path):
                os.mkdir(path)
                os.mkdir(path + "/attack")
                os.mkdir(path + "/get_click")
                os.mkdir(path + "/injured")
                os.mkdir(path + "/skill")

    # 加载音效
    def add(self, characterType: str) -> None:
        if characterType not in self.__SOUNDS and os.path.exists(os.path.join(self.__CHARACTER_SOUNDS_PATH, characterType)):
            self.__SOUNDS[characterType] = {}
            for soundType in os.listdir(os.path.join(self.__CHARACTER_SOUNDS_PATH, characterType)):
                self.__SOUNDS[characterType][soundType] = []
                for soundPath in glob(os.path.join(self.__CHARACTER_SOUNDS_PATH, characterType, soundType, "*")):
                    self.__SOUNDS[characterType][soundType].append(Sound.load(soundPath))

    # 播放角色音效
    def play(self, characterType: str, soundType: str) -> None:
        if characterType in self.__SOUNDS and soundType in self.__SOUNDS[characterType]:
            sound_list = self.__SOUNDS[characterType][soundType]
            if len(sound_list) > 0:
                if len(sound_list) > 1:
                    sound = sound_list[get_random_int(0, len(sound_list) - 1)]
                else:
                    sound = sound_list[0]
                sound.set_volume(Media.volume.effects / 100.0)
                Sound.play(sound, self._channel_id)


# 射击音效
class AttackingSoundManager(AbstractSoundManager):
    def __init__(self, volume: int, channel_id: int):
        super().__init__(channel_id)

        ATTACK_SOUNDS_PATH: str = os.path.join("Assets", "sound", "attack")

        self.__SOUNDS: dict = {
            # 突击步枪
            "AR": glob(os.path.join(ATTACK_SOUNDS_PATH, "ar_*.ogg")),
            # 手枪
            "HG": glob(os.path.join(ATTACK_SOUNDS_PATH, "hg_*.ogg")),
            # 机枪
            "MG": glob(os.path.join(ATTACK_SOUNDS_PATH, "mg_*.ogg")),
            # 步枪
            "RF": glob(os.path.join(ATTACK_SOUNDS_PATH, "rf_*.ogg")),
            # 冲锋枪
            "SMG": glob(os.path.join(ATTACK_SOUNDS_PATH, "smg_*.ogg")),
        }
        self.volume: int = volume
        for key in self.__SOUNDS:
            for i in range(len(self.__SOUNDS[key])):
                self.__SOUNDS[key][i] = Sound.load(self.__SOUNDS[key][i], volume / 100.0)

    # 播放
    def play(self, kind: str) -> None:
        if kind in self.__SOUNDS:
            Sound.play(self.__SOUNDS[kind][get_random_int(0, len(self.__SOUNDS[kind]) - 1)], self._channel_id)
