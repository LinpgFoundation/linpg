# cython: language_level=3
from ..scr_core.function import *

#存储角色受伤立绘的常量
_CHARACTERS_GET_HURT_IMAGE_DICT = {}

#角色受伤立绘图形模块
class CharacterGetHurtImageManagement(GameObject):
    def __init__(self,self_type,y,width):
        GameObject.__init__(self,None,y)
        self.yToGo = None
        self.width = int(width)
        self.alpha = 255
        self.add(self_type)
    def draw(self,screen,characterType:str) -> None:
        GetHurtImage = resizeImg(_CHARACTERS_GET_HURT_IMAGE_DICT[characterType],(self.width,self.width))
        if self.alpha != 255:
            GetHurtImage.set_alpha(self.alpha)
        screen.blit(GetHurtImage,(self.x,self.y))
    def add(self,characterType:str) -> None:
        global _CHARACTERS_GET_HURT_IMAGE_DICT
        if characterType not in _CHARACTERS_GET_HURT_IMAGE_DICT:
            _CHARACTERS_GET_HURT_IMAGE_DICT[characterType] = loadImg("Assets/image/npc/{}_hurt.png".format(characterType))

#角色音效管理系统
class CharacterSoundManagement:
    def __init__(self,channel_id:int) -> None:
        self.channel_id = channel_id
        self.__sounds_dict = {}
    #加载音效
    def add(self,characterType:str) -> None:
        if characterType not in self.__sounds_dict and os.path.exists("Assets/sound/character/"+characterType):
            self.__sounds_dict[characterType] = {}
            for soundType in os.listdir("Assets/sound/character/{}/".format(characterType)):
                self.__sounds_dict[characterType][soundType] = []
                for soundPath in glob.glob("Assets/sound/character/{}/{}/*".format(characterType,soundType)):
                    self.__sounds_dict[characterType][soundType].append(pygame.mixer.Sound(soundPath))
    #播放角色音效
    def play(self,characterType:str,soundType:str) -> None:
        if characterType in self.__sounds_dict and soundType in self.__sounds_dict[characterType]:
            sound_list = self.__sounds_dict[characterType][soundType]
            if len(sound_list) > 1:
                sound = sound_list[randomInt(0,len(sound_list)-1)]
            else:
                sound = sound_list[0]
            sound.set_volume(get_setting("Sound","sound_effects")/100.0)
            pygame.mixer.Channel(self.channel_id).play(sound)

#计算最远攻击距离
def calculate_range(effective_range_dic):
    if effective_range_dic != None:
        max_attack_range = 0
        if "far" in effective_range_dic and effective_range_dic["far"] != None and max_attack_range < effective_range_dic["far"][-1]:
            max_attack_range = effective_range_dic["far"][-1]
        if "middle" in effective_range_dic and effective_range_dic["middle"] != None and max_attack_range < effective_range_dic["middle"][-1]:
            max_attack_range = effective_range_dic["middle"][-1]
        if "near" in effective_range_dic and effective_range_dic["near"] != None and max_attack_range < effective_range_dic["near"][-1]:
            max_attack_range = effective_range_dic["near"][-1]
        return max_attack_range
    else:
        return None

#角色图片管理模块
class CharacterImageManagement:
    def __init__(self) -> None:
        self.__CHARACTERS_IMAGE_DICT = {}
    def get_img(self,characterType:str,action:str,imgId:int) -> pygame.Surface:
        return self.__CHARACTERS_IMAGE_DICT[characterType][action]["img"][imgId]
    def get_img_num(self,characterType:str,action:str) -> int:
        return self.__CHARACTERS_IMAGE_DICT[characterType][action]["imgNum"]
    #动图字典制作模块：接受一个友方角色名，返回对应的动图字典：
    def createGifDict(self,characterType:str,faction:str,mode:str) -> dict:
        if mode == None:
            imgId_dict = {
                "attack":self.loadImageCollection(characterType,"attack",faction),
                "attack2":self.loadImageCollection(characterType,"attack2",faction),
                "move":self.loadImageCollection(characterType,"move",faction),
                "reload":self.loadImageCollection(characterType,"reload",faction),
                "repair":self.loadImageCollection(characterType,"reload",faction),
                "set":self.loadImageCollection(characterType,"set",faction),
                "skill":self.loadImageCollection(characterType,"skill",faction),
                "victory":self.loadImageCollection(characterType,"victory",faction),
                "victoryloop":self.loadImageCollection(characterType,"victoryloop",faction),
                "wait":self.loadImageCollection(characterType,"wait",faction),
                "wait2":self.loadImageCollection(characterType,"wait2",faction),
            }
            imgId_dict["die"] = self.loadImageCollection(characterType,"die",faction)
            """
            if faction == "character":
                imgId_dict["die"] = self.loadImageCollection(characterType,"die",faction)
            else:
                temp_list = ["","2","3"]
                imgId_dict["die"] = self.loadImageCollection(characterType,"die"+temp_list[randomInt(0,2)],faction)
                if imgId_dict["die"]==None:
                    imgId_dict["die"] = self.loadImageCollection(characterType,"die",faction)
            """
        elif mode == "dev":
            imgId_dict = {"wait":self.loadImageCollection(characterType,"wait",faction)}
        else:
            raise Exception('LinpgEngine-Error: Mode is not supported.')
        return imgId_dict
    #动图制作模块：接受一个友方角色名和动作,当前的方块标准长和高，返回对应角色动作list或者因为没图片而返回None
    #810*810 position:405/567
    def loadImageCollection(self,characterType:str,action:str,faction:str) -> dict:
        if characterType not in self.__CHARACTERS_IMAGE_DICT:
            self.__CHARACTERS_IMAGE_DICT[characterType] = {}
        elif action in self.__CHARACTERS_IMAGE_DICT[characterType]:
            return {"imgId":0,"alpha":255}
        if os.path.exists("Assets/image/{0}/{1}/{2}".format(faction,characterType,action)):
            files_amount = len(glob.glob("Assets/image/{0}/{1}/{2}/*.png".format(faction,characterType,action)))
            if files_amount > 0:
                self.__CHARACTERS_IMAGE_DICT[characterType][action] = {"img":numpy.asarray([SrcalphaSurface(\
                    "Assets/image/{0}/{1}/{2}/{3}_{4}_{5}.png".format(faction,characterType,action,characterType,action,i)\
                        ,0,0) for i in range(files_amount)]),"imgNum":files_amount}
                return {"imgId":0,"alpha":255}
            else:
                return None
        else:
            return None

#为角色创建用于储存音效的文件夹
def makeFolderForCharacterSounds():
    for each_character in os.listdir("Assets/image/character/"):
        path = os.path.join("Assets/sound/character",each_character)
        if not os.path.exists(path):
            os.mkdir(path)
            os.mkdir(path+"/attack")
            os.mkdir(path+"/get_click")
            os.mkdir(path+"/injured")
            os.mkdir(path+"/skill")

#加载并更新更新位于Data中的角色数据配置文件-character_data.yaml
def loadCharacterData():
    loadData = loadConfig("Data/character_data.yaml")
    ifAnythingChange = False
    for path in glob.glob(r'Assets/image/character/*'):
        name = path.replace("Assets/image/character\\","")
        if name not in loadData:
            loadData[name] = {
            "action_point": 1,
            "attack_range": 1,
            "effective_range":{
                "far": [5,6],
                "middle":[3,4],
                "near":[1,2],
            },
            "kind": None,
            "magazine_capacity": 1,
            "max_damage": 1,
            "max_hp": 1,
            "min_damage": 1,
            "skill_cover_range": None,
            "skill_effective_range": None,
            }
            ifAnythingChange = True
            print("LinpgEngine-Notice:A new character call {} has been updated to the data file.".format(name))
    for path in glob.glob(r'Assets/image/sangvisFerri/*'):
        name = path.replace("Assets/image/sangvisFerri\\","")
        if name not in loadData:
            loadData[name] = {
            "action_point": 1,
            "attack_range": 1,
            "effective_range":{
                "far": [5,6],
                "middle":[3,4],
                "near":[1,2],
            },
            "kind": None,
            "magazine_capacity": 1,
            "max_damage": 1,
            "max_hp": 1,
            "min_damage": 1,
            }
            ifAnythingChange = True
            print("LinpgEngine-Notice:A new character call {} has been updated to the data file.".format(name))
    if ifAnythingChange == True:
        saveConfig("Data/character_data.yaml",loadData)
    makeFolderForCharacterSounds()
    return loadData

#射击音效 -- 频道2
class AttackingSoundManager:
    def __init__(self,volume,channel):
        self.__soundsData = {
            #突击步枪
            "AR": glob.glob(r'Assets/sound/attack/ar_*.ogg'),
            #手枪
            "HG": glob.glob(r'Assets/sound/attack/hg_*.ogg'),
            #机枪
            "MG": glob.glob(r'Assets/sound/attack/mg_*.ogg'),
            #步枪
            "RF": glob.glob(r'Assets/sound/attack/rf_*.ogg'),
            #冲锋枪
            "SMG": glob.glob(r'Assets/sound/attack/smg_*.ogg'),
        }
        self.__channel = channel
        self.volume = volume
        for key in self.__soundsData:
            for i in range(len(self.__soundsData[key])):
                self.__soundsData[key][i] = pygame.mixer.Sound(self.__soundsData[key][i])
                self.__soundsData[key][i].set_volume(volume/100.0)
    def set_channel(self,channel):
        self.__channel = channel
    def play(self,kind):
        if kind in self.__soundsData:
            pygame.mixer.Channel(self.__channel).play(self.__soundsData[kind][randomInt(0,len(self.__soundsData[kind])-1)])