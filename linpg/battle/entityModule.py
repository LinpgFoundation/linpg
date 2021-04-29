# cython: language_level=3
from .map import *

#存储角色受伤立绘的常量
_CHARACTERS_GET_HURT_IMAGE_DICT:dict = {}

#角色受伤立绘图形模块
class EntityGetHurtImage(GameObject):
    def __init__(self, self_type:str, y:Union[int,float], width:int):
        super().__init__(None,y)
        self.yToGo = None
        self.width = int(width)
        self.alpha = 255
        self.add(self_type)
    def draw(self, screen:pygame.Surface, characterType:str) -> None:
        GetHurtImage = resizeImg(_CHARACTERS_GET_HURT_IMAGE_DICT[characterType],(self.width,self.width))
        if self.alpha != 255:
            GetHurtImage.set_alpha(self.alpha)
        screen.blit(GetHurtImage,(self.x,self.y))
    def add(self, characterType:str) -> None:
        global _CHARACTERS_GET_HURT_IMAGE_DICT
        if characterType not in _CHARACTERS_GET_HURT_IMAGE_DICT:
            _CHARACTERS_GET_HURT_IMAGE_DICT[characterType] = loadImg("Assets/image/npc/{}_hurt.png".format(characterType))

#指向储存角色被察觉和警觉的图标的指针
_BEING_NOTICED_IMG:pygame.Surface = None
_FULLY_EXPOSED_IMG:pygame.Surface = None
_ORANGE_VIGILANCE_IMG:pygame.Surface = None
_RED_VIGILANCE_IMG:pygame.Surface = None

class EntityDynamicProgressBarSurface(DynamicProgressBarSurface):
    def __init__(self, mode:str="horizontal"):
        super().__init__(None,None,0,0,0,0,mode)
        self.load_image()
    #检测被察觉的图标是否生产，如果没有则生成
    def load_image(self):
        global _BEING_NOTICED_IMG,_FULLY_EXPOSED_IMG,_ORANGE_VIGILANCE_IMG,_RED_VIGILANCE_IMG
        #被察觉图标
        if _BEING_NOTICED_IMG is None: _BEING_NOTICED_IMG = imgLoadFunction("Assets/image/UI/eye_orange.png",True)
        if _FULLY_EXPOSED_IMG is None: _FULLY_EXPOSED_IMG = imgLoadFunction("Assets/image/UI/eye_red.png",True)
        #警觉图标
        if _ORANGE_VIGILANCE_IMG is None: _ORANGE_VIGILANCE_IMG = imgLoadFunction("Assets/image/UI/vigilance_orange.png",True)
        if _RED_VIGILANCE_IMG is None: _RED_VIGILANCE_IMG = imgLoadFunction("Assets/image/UI/vigilance_red.png",True)
    def draw(self, surface:pygame.Surface, isFriendlyCharacter:bool=True) -> None:
        global _BEING_NOTICED_IMG,_FULLY_EXPOSED_IMG,_ORANGE_VIGILANCE_IMG,_RED_VIGILANCE_IMG
        if not isFriendlyCharacter:
            surface.blit(resizeImg(_ORANGE_VIGILANCE_IMG,self.size),self.pos)
        else:
            surface.blit(resizeImg(_BEING_NOTICED_IMG,self.size),self.pos)
        self._check_and_update_percentage()
        if self._current_percentage > 0:
            imgOnTop = resizeImg(_FULLY_EXPOSED_IMG,self.size) if isFriendlyCharacter is True else resizeImg(_RED_VIGILANCE_IMG,self.size)
            if self._mode:
                if self._current_percentage < self._percentage_to_be:
                    img2 = cropImg(imgOnTop,size=(int(self._width*self._percentage_to_be/self.accuracy),self._height))
                    img2.set_alpha(100)
                    surface.blit(img2,self.pos)
                    surface.blit(imgOnTop.subsurface((0,0,int(self._width*self._current_percentage/self.accuracy),self._height)),self.pos)
                else:
                    if self._current_percentage > self._percentage_to_be:
                        img2 = cropImg(imgOnTop,size=(int(self._width*self._current_percentage/self.accuracy),self._height))
                        img2.set_alpha(100)
                        surface.blit(img2,self.pos)
                    surface.blit(imgOnTop.subsurface((0,0,int(self._width*self._percentage_to_be/self.accuracy),self._height)),self.pos)
            else:
                if self._current_percentage < self._percentage_to_be:
                    img2 = cropImg(imgOnTop,size=(self._width,int(self._height*self._percentage_to_be/self.accuracy)))
                    img2.set_alpha(100)
                    surface.blit(img2,self.pos)
                    surface.blit(imgOnTop.subsurface((0,0,self._width,int(self._height*self._current_percentage/self.accuracy))),self.pos)
                else:
                    if self._current_percentage > self._percentage_to_be:
                        img2 = cropImg(imgOnTop,size=(self._width,int(self._height*self._current_percentage/self.accuracy)))
                        img2.set_alpha(100)
                        surface.blit(img2,self.pos)
                    surface.blit(imgOnTop.subsurface((0,0,self._width,int(self._height*self._percentage_to_be/self.accuracy))),self.pos)

#指向储存血条图片的指针（不初始化直到Entity或其子类被调用）
_HP_GREEN_IMG:pygame.Surface = None
_HP_RED_IMG:pygame.Surface = None
_HP_EMPTY_IMG:pygame.Surface = None

class EntityHpBar(DynamicProgressBarSurface):
    def __init__(self):
        super().__init__(None,None,0,0,0,0)
        self.load_image()
    #检测被察觉的图标是否生产，如果没有则生成
    def load_image(self):
        global _HP_GREEN_IMG,_HP_RED_IMG,_HP_EMPTY_IMG
        if _HP_GREEN_IMG is None: _HP_GREEN_IMG = imgLoadFunction("Assets/image/UI/hp_green.png",True)
        if _HP_RED_IMG is None: _HP_RED_IMG = imgLoadFunction("Assets/image/UI/hp_red.png",True)
        if  _HP_EMPTY_IMG is None: _HP_EMPTY_IMG = imgLoadFunction("Assets/image/UI/hp_empty.png",True)
    def draw(self, surface:pygame.Surface, isDying:bool) -> None:
        global _HP_GREEN_IMG,_HP_RED_IMG,_HP_EMPTY_IMG
        surface.blit(resizeImg(_HP_EMPTY_IMG,self.size),self.pos)
        self._check_and_update_percentage()
        if self._current_percentage > 0:
            imgOnTop = resizeImg(_HP_GREEN_IMG,self.size) if not isDying else resizeImg(_HP_RED_IMG,self.size)
            if self._mode:
                if self._current_percentage < self._percentage_to_be:
                    img2 = cropImg(imgOnTop,size=(int(self._width*self._percentage_to_be/self.accuracy),self._height))
                    img2.set_alpha(100)
                    surface.blit(img2,self.pos)
                    surface.blit(imgOnTop.subsurface((0,0,int(self._width*self._current_percentage/self.accuracy),self._height)),self.pos)
                else:
                    if self._current_percentage > self._percentage_to_be:
                        img2 = cropImg(imgOnTop,size=(int(self._width*self._current_percentage/self.accuracy),self._height))
                        img2.set_alpha(100)
                        surface.blit(img2,self.pos)
                    surface.blit(imgOnTop.subsurface((0,0,int(self._width*self._percentage_to_be/self.accuracy),self._height)),self.pos)
            else:
                if self._current_percentage < self._percentage_to_be:
                    img2 = cropImg(imgOnTop,size=(self._width,int(self._height*self._percentage_to_be/self.accuracy)))
                    img2.set_alpha(100)
                    surface.blit(img2,self.pos)
                    surface.blit(imgOnTop.subsurface((0,0,self._width,int(self._height*self._current_percentage/self.accuracy))),self.pos)
                else:
                    if self._current_percentage > self._percentage_to_be:
                        img2 = cropImg(imgOnTop,size=(self._width,int(self._height*self._current_percentage/self.accuracy)))
                        img2.set_alpha(100)
                        surface.blit(img2,self.pos)
                    surface.blit(imgOnTop.subsurface((0,0,self._width,int(self._height*self._percentage_to_be/self.accuracy))),self.pos)

#音效管理模块-字典
class AbstractEntitySoundManager(AbstractSoundManager):
    def __init__(self, channel_id:int):
        super().__init__(channel_id)
        self._SOUNDS_PATH:str = ''
        self._sounds_dict:dict = {}

#角色音效管理系统
class EntitySoundManager(AbstractEntitySoundManager):
    def __init__(self, channel_id:int):
        super().__init__(channel_id)
        self._SOUNDS_PATH = "Assets/sound/character"
    #加载音效
    def add(self, characterType:str) -> None:
        if characterType not in self._sounds_dict and os.path.exists(os.path.join(self._SOUNDS_PATH,characterType)):
            self._sounds_dict[characterType] = {}
            for soundType in os.listdir(os.path.join(self._SOUNDS_PATH,characterType)):
                self._sounds_dict[characterType][soundType] = []
                for soundPath in glob(os.path.join(self._SOUNDS_PATH,characterType,soundType,"*")):
                    self._sounds_dict[characterType][soundType].append(pygame.mixer.Sound(soundPath))
    #播放角色音效
    def play(self, characterType:str, soundType:str) -> None:
        if characterType in self._sounds_dict and soundType in self._sounds_dict[characterType]:
            sound_list = self._sounds_dict[characterType][soundType]
            if len(sound_list) > 0:
                if len(sound_list) > 1:
                    sound = sound_list[randomInt(0,len(sound_list)-1)]
                else:
                    sound = sound_list[0]
                sound.set_volume(get_setting("Sound","sound_effects")/100.0)
                pygame.mixer.Channel(self._channel_id).play(sound)

#射击音效 -- 频道2
class AttackingSoundManager(AbstractEntitySoundManager):
    def __init__(self, volume:int, channel_id:int):
        super().__init__(channel_id)
        self._SOUNDS_PATH = "Assets/sound/attack"
        self._sounds_dict = {
            #突击步枪
            "AR": glob(os.path.join(self._SOUNDS_PATH,'ar_*.ogg')),
            #手枪
            "HG": glob(os.path.join(self._SOUNDS_PATH,'hg_*.ogg')),
            #机枪
            "MG": glob(os.path.join(self._SOUNDS_PATH,'mg_*.ogg')),
            #步枪
            "RF": glob(os.path.join(self._SOUNDS_PATH,'rf_*.ogg')),
            #冲锋枪
            "SMG": glob(os.path.join(self._SOUNDS_PATH,'smg_*.ogg')),
        }
        self.volume:int = volume
        for key in self._sounds_dict:
            for i in range(len(self._sounds_dict[key])):
                self._sounds_dict[key][i] = pygame.mixer.Sound(self._sounds_dict[key][i])
                self._sounds_dict[key][i].set_volume(volume/100.0)
    #播放
    def play(self, kind:str) -> None:
        if kind in self._sounds_dict:
            pygame.mixer.Channel(self._channel_id).play(self._sounds_dict[kind][randomInt(0,len(self._sounds_dict[kind])-1)])

#计算最远攻击距离
def calculate_range(effective_range_dic:dict) -> int:
    if effective_range_dic is not None:
        max_attack_range:int = 0
        if "far" in effective_range_dic and effective_range_dic["far"] is not None and max_attack_range < effective_range_dic["far"][-1]:
            return effective_range_dic["far"][-1]
        if "middle" in effective_range_dic and effective_range_dic["middle"] is not None and max_attack_range < effective_range_dic["middle"][-1]:
            return effective_range_dic["middle"][-1]
        if "near" in effective_range_dic and effective_range_dic["near"] is not None and max_attack_range < effective_range_dic["near"][-1]:
            return effective_range_dic["near"][-1]
        return max_attack_range
    else:
        return 0

#角色图片管理模块
class EntityImageManager:
    def __init__(self):
        self.__CHARACTERS_IMAGE_DICT = {}
    def get_img(self, characterType:str, action:str, imgId:int) -> pygame.Surface:
        return self.__CHARACTERS_IMAGE_DICT[characterType][action]["img"][imgId]
    def get_img_num(self, characterType:str, action:str) -> int:
        return self.__CHARACTERS_IMAGE_DICT[characterType][action]["imgNum"]
    #动图字典制作模块：接受一个友方角色名，返回对应的动图字典：
    def createGifDict(self, characterType:str, faction:str, mode:str) -> dict:
        if mode == "default":
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
            if faction != "sangvisFerri":
                imgId_dict["die"] = self.loadImageCollection(characterType,"die",faction)
            else:
                imgId_dict["die"] = self.loadImageCollection(characterType,"die",faction)
                """
                temp_list = ["","2","3"]
                imgId_dict["die"] = self.loadImageCollection(characterType,"die"+temp_list[randomInt(0,2)],faction)
                if imgId_dict["die"] is None:
                    imgId_dict["die"] = self.loadImageCollection(characterType,"die",faction)
                """
        elif mode == "dev":
            imgId_dict = {"wait":self.loadImageCollection(characterType,"wait",faction)}
        else:
            throwException("error","Mode is not supported")
        return imgId_dict
    #动图制作模块：接受一个友方角色名和动作,当前的方块标准长和高，返回对应角色动作list或者因为没图片而返回None
    #810*810 position:405/567
    def loadImageCollection(self, characterType:str, action:str, faction:str) -> dict:
        if characterType not in self.__CHARACTERS_IMAGE_DICT:
            self.__CHARACTERS_IMAGE_DICT[characterType] = {}
        elif action in self.__CHARACTERS_IMAGE_DICT[characterType]:
            return {"imgId":0,"alpha":255}
        if os.path.exists("Assets/image/{0}/{1}/{2}".format(faction,characterType,action)):
            files_amount = len(glob("Assets/image/{0}/{1}/{2}/*.png".format(faction,characterType,action)))
            if files_amount > 0:
                self.__CHARACTERS_IMAGE_DICT[characterType][action] = {
                    "img": numpy.asarray([StaticImageSurface("Assets/image/{0}/{1}/{2}/{3}_{4}_{5}.png"
                    .format(faction,characterType,action,characterType,action,i),0,0) for i in range(files_amount)]),
                    "imgNum": files_amount
                    }
                if faction == "sangvisFerri":
                    for img in self.__CHARACTERS_IMAGE_DICT[characterType][action]["img"]:
                        img.flip_original()
                return {"imgId":0,"alpha":255}
            else:
                return None
        else:
            return None

#为角色创建用于储存音效的文件夹
def makeFolderForCharacterSounds() -> None:
    for each_character in os.listdir("Assets/image/character/"):
        path = os.path.join("Assets/sound/character",each_character)
        if not os.path.exists(path):
            os.mkdir(path)
            os.mkdir(path+"/attack")
            os.mkdir(path+"/get_click")
            os.mkdir(path+"/injured")
            os.mkdir(path+"/skill")

#加载并更新更新位于Data中的角色数据配置文件-character_data.yaml
def loadCharacterData() -> None:
    loadData = loadConfig("Data/character_data.yaml")
    ifAnythingChange = False
    for path in glob(r'Assets/image/character/*'):
        name = os.path.basename(path)
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
            throwException("info","A new character call {} has been updated to the data file.".format(name))
    for path in glob(r'Assets/image/sangvisFerri/*'):
        name = os.path.basename(path)
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
            throwException("info","A new character call {} has been updated to the data file.".format(name))
    if ifAnythingChange is True:
        saveConfig("Data/character_data.yaml",loadData)
    makeFolderForCharacterSounds()
    return loadData

#用于存放角色做出的决定
class DecisionHolder:
    def __init__(self, action:str, data:any):
        self.action = action
        self.data = data
    @property
    def route(self):
        if self.action == "move":
            return self.data
        else:
            throwException("error","The character does not decide to move!")
    @property
    def target(self):
        if self.action == "attack":
            return self.data[0]
        else:
            throwException("error","The character does not decide to attack!")
    @property
    def target_area(self):
        if self.action == "attack":
            return self.data[1]
        else:
            throwException("error","The character does not decide to attack!")
