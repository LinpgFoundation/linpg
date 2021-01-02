# cython: language_level=3
import threading
from ..basic import *

#储存角色图片的常量
__CHARACTERS_IMAGE_DICT = {}
#获取特定的角色图片
def getDollImg(self_type,action,imgId,width):
    img = __CHARACTERS_IMAGE_DICT[self_type][action]["img"][imgId]
    return pygame.transform.scale(img,(width,width))
#获取角色对应图片的ID
def getDollImgNum(self_type,action):
    return __CHARACTERS_IMAGE_DICT[self_type][action]["imgNum"]

#储存角色音效的常量
__CHARACTERS_SOUND_DICT = {}
__CHARACTERS_SOUND_CHANNEL = 5
#加载角色音效
def _load_sound_to_CHARACTERS_SOUND_DICT(self_type):
    if self_type not in __CHARACTERS_SOUND_DICT and os.path.exists("Assets/sound/character/"+self_type):
        sound_files = os.listdir("Assets/sound/character/{}/".format(self_type))
        if len(sound_files) > 0:
            volume = get_setting("Sound","sound_effects")
            __CHARACTERS_SOUND_DICT[self_type] = {}
            for kindOfSound in sound_files:
                __CHARACTERS_SOUND_DICT[self_type][kindOfSound] = []
                allSoundOfThatKind = glob.glob("Assets/sound/character/{}/{}/*".format(self_type,kindOfSound))
                if len(allSoundOfThatKind) > 0:
                    for soundPath in allSoundOfThatKind:
                        sound = pygame.mixer.Sound(soundPath)
                        sound.set_volume(volume/100.0)
                        __CHARACTERS_SOUND_DICT[self_type][kindOfSound].append(sound)
#播放角色音效
def _play_CHARACTERS_SOUND(self_type,kind_of_sound):
    if self_type in __CHARACTERS_SOUND_DICT:
        sound_list = __CHARACTERS_SOUND_DICT[self_type]
        if kind_of_sound in sound_list:
            sound_list = sound_list[kind_of_sound]
            if len(sound_list) == 1:
                pygame.mixer.Channel(__CHARACTERS_SOUND_CHANNEL).play(sound_list[0])
            elif len(sound_list) > 1:
                pygame.mixer.Channel(__CHARACTERS_SOUND_CHANNEL).play(sound_list[random.randint(0,len(sound_list)-1)])

#角色UI的文字
DOLL_UI_FONT = createFont(get_setting("Screen_size_x")/192)
#角色受伤立绘
__CHARACTERS_GET_HURT_IMAGE_DICT = {}
def _get_CHARACTERS_GET_HURT_IMAGE(self_type):
    return __CHARACTERS_GET_HURT_IMAGE_DICT[self_type]
def _add_CHARACTERS_GET_HURT_IMAGE(self_type):
    if self_type not in __CHARACTERS_GET_HURT_IMAGE_DICT:
        __CHARACTERS_GET_HURT_IMAGE_DICT[self_type] = pygame.image.load(os.path.join("Assets/image/npc/{}_hurt.png".format(self_type))).convert_alpha()
#角色受伤立绘图形模块
class CHARACTERS_GET_HURT_IMAGE:
    def __init__(self,self_type,y,width):
        self.x = None
        self.y = y
        self.yToGo = None
        self.width = int(width)
        self.alpha = 255
        _add_CHARACTERS_GET_HURT_IMAGE(self_type)
    def draw(self,screen,self_type):
        GetHurtImage = pygame.transform.scale(_get_CHARACTERS_GET_HURT_IMAGE(self_type),(self.width,self.width))
        if self.alpha != 255:
            GetHurtImage.set_alpha(self.alpha)
        screen.blit(GetHurtImage,(self.x,self.y))

#人形模块
class Doll:
    def __init__(self,DATA,faction,mode):
        #当前行动值
        self.__current_action_point = DATA["action_point"]
        #最大行动值
        self.max_action_point = DATA["action_point"]
        #攻击范围
        self.attack_range = DATA["attack_range"]
        #当然弹夹的子弹数
        self.current_bullets = DATA["current_bullets"] if "current_hp" in DATA else DATA["magazine_capacity"]
        #当前血量
        self.current_hp = DATA["current_hp"] if "current_hp" in DATA else DATA["max_hp"]
        #不可再生的护甲值
        self.irrecoverable_armor = DATA["irrecoverable_armor"] if "irrecoverable_armor" in DATA else 0
        #当前可再生的护甲值
        self.current_recoverable_armor = DATA["recoverable_armor"] if "recoverable_armor" in DATA else 0
        #最大可再生的护甲值
        self.max_recoverable_armor = DATA["recoverable_armor"] if "recoverable_armor" in DATA else 0
        #是否濒死
        self.dying = False if self.current_hp > 0 else 3
        #攻击距离
        self.effective_range = DATA["effective_range"]
        #最大攻击距离
        self.max_effective_range = calculate_range(self.effective_range)
        #武器类型
        self.kind = DATA["kind"]
        #阵营
        self.faction = faction
        #角色武器名称
        self.type = DATA["type"]
        #gif图片管理
        self.__imgId_dict = character_gif_dic(self.type,faction,mode)
        #弹夹容量
        self.magazine_capacity = DATA["magazine_capacity"]
        #最大攻击力
        self.max_damage = DATA["max_damage"]
        #最大血量
        self.max_hp = DATA["max_hp"]
        #最小攻击力
        self.min_damage = DATA["min_damage"]
        #是否图片镜像
        self.ifFlip = False
        #x坐标
        self.x = DATA["x"]
        #y坐标
        self.y = DATA["y"]
        #受伤的立绘
        self.ImageGetHurt = None
        #当前动作
        self.__currentAction = "wait"
        #动作是否重复
        self.__ifActionLoop = True
        #动作是正序列播放还是反序播放
        self._ifActionPlayReverse = False
        #是否动作已经播放一遍
        self.__ifActionPlayedOnce = False
        #需要移动的路径
        self.__movingPath = None
        #是否需要重新渲染地图
        self.__reProcessMap = False
    def __lt__(self,other):
        return self.y+self.x < other.y+other.x
    #设置动作
    def set_action(self,action="wait",ifLoop=True):
        self.reset_imgId(self.__currentAction)
        self.__currentAction = action
        self.__ifActionLoop = ifLoop
        self.__ifActionPlayedOnce = False
    #获取当前动作
    def get_action(self):
        return self.__currentAction
    #是否闲置
    def is_idle(self):
        return self.__currentAction == "wait"
    #设置需要移动的路径
    def move_follow(self,path):
        if isinstance(path,(list,tuple)) and len(path)>0:
            self.__movingPath = path
            self.set_action("move")
        else:
            raise Exception('ZeroEngine-Error: Character cannot move to a invalid path!')
    #查看是否需要重新渲染地图
    def needUpdateMap(self):
        if self.__reProcessMap == True:
            self.__reProcessMap = False
            return True
        else:
            return False
    #根据路径移动
    def __move_based_on_path(self,theMapClass):
        if len(self.__movingPath) > 0:
            if self.x < self.__movingPath[0][0]:
                self.x+=0.05
                self.setFlip(False)
                if self.x >= self.__movingPath[0][0]:
                    self.x = self.__movingPath[0][0]
                    self.__movingPath.pop(0)
                    if theMapClass.isAtNight():
                        self.__reProcessMap = True
            elif self.x > self.__movingPath[0][0]:
                self.x-=0.05
                self.setFlip(True)
                if self.x <= self.__movingPath[0][0]:
                    self.x = self.__movingPath[0][0]
                    self.__movingPath.pop(0)
                    if theMapClass.isAtNight():
                        self.__reProcessMap = True
            elif self.y < self.__movingPath[0][1]:
                self.y+=0.05
                self.setFlip(True)
                if self.y >= self.__movingPath[0][1]:
                    self.y = self.__movingPath[0][1]
                    self.__movingPath.pop(0)
                    if theMapClass.isAtNight():
                        self.__reProcessMap = True
            elif self.y > self.__movingPath[0][1]:
                self.y-=0.05
                self.setFlip(False)
                if self.y <= self.__movingPath[0][1]:
                    self.y = self.__movingPath[0][1]
                    self.__movingPath.pop(0)
                    if theMapClass.isAtNight():
                        self.__reProcessMap = True
        else:
            self.__movingPath = None
            if self.get_imgId("set") != None:
                self.set_action("set",False)
            else:
                self.set_action()
    #减少行动值
    def reduce_action_point(self,value):
        if not console.get_events("cheat"):
            if isinstance(value,int):
                if self.__current_action_point >= value:
                    #有足够的行动值来减去
                    self.__current_action_point -= value
                    return True
                else:
                    #没有足够的行动值来减去
                    return False
            else:
                raise Exception('ZeroEngine-Error: While you reduce the action points, the module cannot reduce a non-int value!')
        else:
            #作弊模式开启时不扣行动力
            return True
    #获取行动值
    def get_action_point(self):
        return self.__current_action_point
    def have_enough_action_point(self,value):
        return self.__current_action_point >= value
    def reset_action_point(self):
        self.__current_action_point = self.max_action_point
    def near(self,otherDoll):
        if self.x == otherDoll.x:
            if abs(self.y-otherDoll.y) <= 1:
                return True
            else:
                return False
        elif self.y == otherDoll.y:
            if abs(self.x-otherDoll.x) <= 1:
                return True
            else:
                return False
        else:
            return False
    def get_pos(self):
        return self.x,self.y
    #检测是否在对应位置上
    def on_pos(self,pos):
        if isinstance(pos,dict):
            return self.x == pos["x"] and self.y == pos["y"]
        else:
            return self.x == pos[0] and self.y == pos[1]
    def loadImg(self):
        for theAction in self.__imgId_dict:
            character_creator(self.type,theAction,self.faction)
        _load_sound_to_CHARACTERS_SOUND_DICT(self.type)
        if self.faction == "character":
            _add_CHARACTERS_GET_HURT_IMAGE(self.type)
    def attackBy(self,attacker):
        damage = random.randint(attacker.min_damage,attacker.max_damage)
        self.decreaseHp(damage)
        return damage
    def decreaseHp(self,damage):
        damage = abs(damage)
        #如果有可再生的护甲
        if self.current_recoverable_armor > 0:
            #如果伤害大于护甲值,则以护甲值为最大护甲将承受的伤害
            if damage > self.current_recoverable_armor:
                damage_take_by_armor = random.randint(0,self.current_recoverable_armor)
            #如果伤害小于护甲值,则以伤害为最大护甲将承受的伤害
            else:
                damage_take_by_armor = random.randint(0,damage)
            self.current_recoverable_armor -= damage_take_by_armor
            damage -= damage_take_by_armor
        #如果有不可再生的护甲
        if self.irrecoverable_armor > 0 and damage > 0:
            if damage > self.irrecoverable_armor:
                damage_take_by_armor = random.randint(0,self.irrecoverable_armor)
            #如果伤害小于护甲值,则以伤害为最大护甲将承受的伤害
            else:
                damage_take_by_armor = random.randint(0,damage)
            self.irrecoverable_armor -= damage_take_by_armor
            damage -= damage_take_by_armor
        #如果还有伤害,则扣除血量
        if damage > 0:
            self.current_hp -= damage
        #如果角色血量小等于0，进入死亡状态
        if self.current_hp <= 0:
            self.current_hp = 0
            self.set_action("die",None)
    def heal(self,hpHealed):
        self.current_hp+=abs(hpHealed)
    def setFlip(self,theBool):
        if self.ifFlip != theBool:
            self.ifFlip = theBool
    def draw(self,screen,theMapClass):
        #调整小人图片的尺寸
        img_of_char = getDollImg(self.type,self.__currentAction,self.__imgId_dict[self.__currentAction]["imgId"],round(theMapClass.block_width*1.6))
        #调整alpha值
        imgAlpha = self.get_imgAlpaha(self.__currentAction)
        if imgAlpha != 255:
            img_of_char.set_alpha(imgAlpha)
        #反转图片
        if self.ifFlip == True:
            img_of_char = pygame.transform.flip(img_of_char,True,False)
        #如果当前动作是移动
        if self.__currentAction == "move" and self.__movingPath != None:
            self.__move_based_on_path(theMapClass)
        #把角色图片画到屏幕上
        xTemp,yTemp = theMapClass.calPosInMap(self.x,self.y)
        screen.blit(img_of_char,(xTemp-theMapClass.block_width*0.3,yTemp-theMapClass.block_width*0.85))
        #如果角色图片还没播放完
        if not self._ifActionPlayReverse:
            if self.__imgId_dict[self.__currentAction]["imgId"] < getDollImgNum(self.type,self.__currentAction)-1:
                self.__imgId_dict[self.__currentAction]["imgId"] += 1
            #如果角色图片播放完需要重新播
            elif self.__ifActionLoop == True:
                self.__ifActionPlayedOnce = True
                self.__imgId_dict[self.__currentAction]["imgId"] = 0
            #如果角色图片播放完但不打算重新播
            elif self.__ifActionLoop == None:
                self.__ifActionPlayedOnce = True
            #如果角色图片播放完需要回到待机状态
            elif self.__ifActionLoop == False:
                self.set_action()
            else:
                raise Exception('ZeroEngine-Error: self.__ifActionLoop data error: '+self.__ifActionLoop)
        else:
            if self.__imgId_dict[self.__currentAction]["imgId"] > 0:
                self.__imgId_dict[self.__currentAction]["imgId"] -= 1
            else:
                self._ifActionPlayReverse = False
                self.set_action()
    def draw_custom(self,action,pos,screen,theMapClass,alpha=155,isContinue=True):
        #调整小人图片的尺寸
        img_of_char = getDollImg(self.type,action,self.__imgId_dict[action]["imgId"],round(theMapClass.block_width*1.6))
        #反转图片
        if self.ifFlip == True:
            img_of_char = pygame.transform.flip(img_of_char,True,False)
        img_of_char.set_alpha(alpha)
        #把角色图片画到屏幕上
        screen.blit(img_of_char,(pos[0]-theMapClass.block_width*0.3,pos[1]-theMapClass.block_width*0.85))
        #调整id，并返回对应的bool状态
        if self.__imgId_dict[action]["imgId"] < getDollImgNum(self.type,action)-1:
            self.__imgId_dict[action]["imgId"] += 1
            return True
        else:
            if isContinue == True:
                self.__imgId_dict[action]["imgId"] = 0
                return True
            else:
                return False
    def drawUI(self,screen,original_UI_img,theMapClass):
        hp_img = None
        if self.dying == False:
            if original_UI_img != None:
                hp_img = original_UI_img["hp_green"]
            current_hp_to_display = DOLL_UI_FONT.render("{}/{}".format(self.current_hp,self.max_hp),get_fontMode(),(0,0,0))
            percent_of_hp = self.current_hp/self.max_hp
        else:
            if original_UI_img != None:
                hp_img = original_UI_img["hp_red"]
            current_hp_to_display = DOLL_UI_FONT.render("{}/3".format(self.dying),get_fontMode(),(0,0,0))
            percent_of_hp = self.dying/3
        #把角色图片画到屏幕上
        xTemp,yTemp = theMapClass.calPosInMap(self.x,self.y)
        xTemp += theMapClass.block_width*0.25
        yTemp -= theMapClass.block_width*0.2
        if self.faction == "character" and self.detection != None:
            eyeImgWidth = round(theMapClass.block_width/6*self.eyeImgSize)
            eyeImgHeight = round(theMapClass.block_width/10*self.eyeImgSize)
            numberX = (eyeImgWidth - theMapClass.block_width/6)/2
            numberY = (eyeImgHeight - theMapClass.block_width/10)/2
            if self.detection == True:
                screen.blit(resizeImg(original_UI_img["eye_red"], (eyeImgWidth,eyeImgHeight)),(xTemp+theMapClass.block_width*0.51-numberX,yTemp-numberY))
            elif self.detection == False:
                screen.blit(resizeImg(original_UI_img["eye_orange"], (eyeImgWidth,eyeImgHeight)),(xTemp+theMapClass.block_width*0.51-numberX,yTemp-numberY))
            if self.eyeImgSize > 1:
                self.eyeImgSize-=1
            if self.ImageGetHurt != None and self.ImageGetHurt.x != None:
                self.ImageGetHurt.draw(screen,self.type)
                if self.ImageGetHurt.x < self.ImageGetHurt.width/4:
                    self.ImageGetHurt.x += self.ImageGetHurt.width/25
                else:
                    if self.ImageGetHurt.yToGo > 0:
                        self.ImageGetHurt.yToGo -= 5
                    else:
                        if self.ImageGetHurt.alpha > 0:
                            self.ImageGetHurt.alpha -= 2
                        else:
                            self.ImageGetHurt.x = None
        hpEmptyScale = pygame.transform.scale(original_UI_img["hp_empty"], (round(theMapClass.block_width/2), round(theMapClass.block_width/10)))
        screen.blit(hpEmptyScale,(xTemp,yTemp))
        screen.blit(pygame.transform.scale(hp_img,(round(theMapClass.block_width*percent_of_hp/2),round(theMapClass.block_width/10))),(xTemp,yTemp))
        displayInCenter(current_hp_to_display,hpEmptyScale,xTemp,yTemp,screen)
    #获取角色特定动作的图片播放ID
    def get_imgId(self,action):
        action = self.__imgId_dict[action]
        if action != None:
            return action["imgId"]
        else:
            return None
    #获取角色特定动作的图片总数量
    def get_imgNum(self,action):
        return getDollImgNum(self.type,action)
    #设定角色特定动作的图片播放ID
    def set_imgId(self,action,theId):
        self.__imgId_dict[action]["imgId"] = theId
    #重置角色特定动作的图片播放ID
    def reset_imgId(self,action):
        self.__imgId_dict[action]["imgId"] = 0
    #增加角色特定动作的图片播放ID
    def add_imgId(self,action,amount=1):
        self.__imgId_dict[action]["imgId"]+=amount
    #获取角色特定动作的图片透明度
    def get_imgAlpaha(self,action):
        return self.__imgId_dict[action]["alpha"]
    #设定角色特定动作的图片透明度
    def set_imgAlpaha(self,action,alpha):
        self.__imgId_dict[action]["alpha"] = alpha
    #调整角色的隐蔽度
    def noticed(self,force=False):
        if force == False:
            if self.detection == None:
                self.eyeImgSize = 10
                self.detection = False
            elif self.detection == False:
                self.eyeImgSize = 10
                self.detection = True
        elif force == True:
            self.eyeImgSize = 10
            self.detection = True
    #判断是否在攻击范围内
    def isInAttackRange(self,other,theMap):
        attackRange = self.getAttackRange(theMap)
        for key in attackRange:
            if (other.x,other.y) in attackRange[key]:
                return True
        return False
    #获取角色的攻击范围
    def getAttackRange(self,theMap):
        attacking_range = {"near":[],"middle":[],"far":[]}
        for y in range(self.y-self.max_effective_range,self.y+self.max_effective_range+1):
            if y < self.y:
                for x in range(self.x-self.max_effective_range-(y-self.y),self.x+self.max_effective_range+(y-self.y)+1):
                    if theMap.row>y>=0 and theMap.column>x>=0:
                        if "far" in self.effective_range and self.effective_range["far"] != None and self.effective_range["far"][0] <= abs(x-self.x)+abs(y-self.y) <= self.effective_range["far"][1]:
                            attacking_range["far"].append((x,y))
                        elif "middle" in self.effective_range and self.effective_range["middle"] != None and self.effective_range["middle"][0] <= abs(x-self.x)+abs(y-self.y) <= self.effective_range["middle"][1]:
                            attacking_range["middle"].append((x,y))
                        elif "near" in self.effective_range and self.effective_range["near"] != None and self.effective_range["near"][0] <= abs(x-self.x)+abs(y-self.y) <= self.effective_range["near"][1]:
                            attacking_range["near"].append((x,y))
            else:
                for x in range(self.x-self.max_effective_range+(y-self.y),self.x+self.max_effective_range-(y-self.y)+1):
                    if x == self.x and y == self.y:
                        pass
                    elif theMap.row>y>=0 and theMap.column>x>=0:
                        if "far" in self.effective_range and self.effective_range["far"] != None and self.effective_range["far"][0] <= abs(x-self.x)+abs(y-self.y) <= self.effective_range["far"][1]:
                            attacking_range["far"].append((x,y))
                        elif "middle" in self.effective_range and self.effective_range["middle"] != None and self.effective_range["middle"][0] <= abs(x-self.x)+abs(y-self.y) <= self.effective_range["middle"][1]:
                            attacking_range["middle"].append((x,y))
                        elif "near" in self.effective_range and self.effective_range["near"] != None and self.effective_range["near"][0] <= abs(x-self.x)+abs(y-self.y) <= self.effective_range["near"][1]:
                            attacking_range["near"].append((x,y))
        return attacking_range
    #播放角色声音
    def playSound(self,kind_of_sound):
        _play_CHARACTERS_SOUND(self.type,kind_of_sound)

#格里芬角色类
class CharacterDataManager(Doll):
    def __init__(self,theCharacterDataDic,defaultData,mode=None):
        for key in theCharacterDataDic:
            defaultData[key] = theCharacterDataDic[key]
        Doll.__init__(self,defaultData,"character",mode)
        self.bullets_carried = defaultData["bullets_carried"]
        self.skill_effective_range = defaultData["skill_effective_range"]
        self.max_skill_range = calculate_range(defaultData["skill_effective_range"])
        self.skill_cover_range = defaultData["skill_cover_range"]
        self.detection = defaultData["detection"] if "detection" in defaultData else None
        self.eyeImgSize = 0
        if self.kind != "HOC":
            try:
                self.ImageGetHurt = CHARACTERS_GET_HURT_IMAGE(self.type,get_setting("Screen_size_y")/4,get_setting("Screen_size_y")/2)
            except BaseException:
                print('警告：角色 {} 没有对应的破衣动画'.format(defaultData["type"]))
                if not os.path.exists("Assets/image/npc_icon/{}.png".format(defaultData["type"])):
                    print("而且你也忘了加入对应的头像")
    def attackBy(self,attacker,result_of_round):
        damage = random.randint(attacker.min_damage,attacker.max_damage)
        self.decreaseHp(damage,result_of_round)
        return damage
    def decreaseHp(self,damage,result_of_round):
        super().decreaseHp(damage)
        if self.current_hp <= 0 and self.dying == False:
            if self.kind != "HOC":
                self.dying = 3
                if self.ImageGetHurt != None:
                    self.ImageGetHurt.x = -self.ImageGetHurt.width
                    self.ImageGetHurt.alpha = 255
                    self.ImageGetHurt.yToGo = 255
                    self.playSound("injured")
            result_of_round["times_characters_down"] += 1
    def heal(self,hpHealed):
        super().heal(hpHealed)
        if self.dying != False:
            self.dying = False
            self._ifActionPlayReverse = True
    #根据坐标反转角色
    def setFlipBasedPos(self,pos):
        #检测坐标
        if isinstance(pos,(list,tuple)):
            x = pos[0]
            y = pos[1]
        elif isinstance(pos,dict):
            x = pos["x"]
            y = pos["y"]
        else:
            x = pos.x
            y = pos.y
        #检测坐标
        if self.x > x:
            self.setFlip(True)
        elif self.x == x:
            if self.y > y:
                self.setFlip(False)
            else:
                self.setFlip(True)
        else:
            self.setFlip(False)

#铁血角色类
class SangvisFerriDataManager(Doll):
    def __init__(self,theSangvisFerrisDataDic,defaultData,mode=None):
        for key in theSangvisFerrisDataDic:
            defaultData[key] = theSangvisFerrisDataDic[key]
        Doll.__init__(self,defaultData,"sangvisFerri",mode)
        self.patrol_path = defaultData["patrol_path"] if "patrol_path" in defaultData else []
    def setFlipBasedPos(self,pos):
        #检测坐标
        if isinstance(pos,(list,tuple)):
            x = pos[0]
            y = pos[1]
        elif isinstance(pos,dict):
            x = pos["x"]
            y = pos["y"]
        else:
            x = pos.x
            y = pos.y
        #检测坐标
        if self.x < x:
            self.setFlip(True)
        elif self.x == x:
            if self.y < y:
                self.setFlip(False)
            else:
                self.setFlip(True)
        else:
            self.setFlip(False)

#初始化角色信息
class initializeCharacterDataThread(threading.Thread):
    def __init__(self,characters,sangvisFerris,mode=None):
        threading.Thread.__init__(self)
        self.DATABASE = loadCharacterData()
        self.characters_data = {}
        self.sangvisFerris_data = {}
        self.characters = characters
        self.sangvisFerris = sangvisFerris
        self.totalNum = len(characters)+len(sangvisFerris)
        self.currentID = 0
        self.mode = mode
    def run(self):
        for each_character in self.characters:
            self.characters_data[each_character] = CharacterDataManager(self.characters[each_character],self.DATABASE[self.characters[each_character]["type"]],self.mode)
            self.currentID+=1
        for each_character in self.sangvisFerris:
            self.sangvisFerris_data[each_character] = SangvisFerriDataManager(self.sangvisFerris[each_character],self.DATABASE[self.sangvisFerris[each_character]["type"]],self.mode)
            self.currentID+=1
    def getResult(self):
        return self.characters_data,self.sangvisFerris_data

class loadCharacterDataFromSaveThread(threading.Thread):
    def __init__(self,characters_data,sangvisFerris_data):
        threading.Thread.__init__(self)
        self.totalNum = len(characters_data)+len(sangvisFerris_data)
        self.currentID = 0
        self.characters_data = characters_data
        self.sangvisFerris_data = sangvisFerris_data
    def run(self):
        for each_character in self.characters_data:
            self.characters_data[each_character].loadImg()
            self.currentID+=1
        for each_character in self.sangvisFerris_data:
            self.sangvisFerris_data[each_character].loadImg()
            self.currentID+=1

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

#动图制作模块：接受一个友方角色名和动作,当前的方块标准长和高，返回对应角色动作list或者因为没图片而返回None
#810*810 possition:405/567
def character_creator(character_name,action,faction):
    global __CHARACTERS_IMAGE_DICT
    if character_name in __CHARACTERS_IMAGE_DICT:
        if action in __CHARACTERS_IMAGE_DICT[character_name]:
            return {"imgId":0,"alpha":255}
        else:
            __CHARACTERS_IMAGE_DICT[character_name][action] = {}
    else:
        __CHARACTERS_IMAGE_DICT[character_name] = {}
        #__CHARACTERS_IMAGE_DICT[character_name][action] = {}
    if os.path.exists("Assets/image/{0}/{1}/{2}".format(faction,character_name,action)):
        files_amount = len(glob.glob("Assets/image/{0}/{1}/{2}/*.png".format(faction,character_name,action)))
        if files_amount > 0:
            images_list = [pygame.image.load(os.path.join("Assets/image/{0}/{1}/{2}/{3}_{4}_{5}.png".format(faction,character_name,action,character_name,action,i))).convert_alpha() for i in range(files_amount)]
            __CHARACTERS_IMAGE_DICT[character_name][action] = {"img":images_list,"imgNum":files_amount}
            return {"imgId":0,"alpha":255}
        else:
            return None
    else:
        return None

#动图字典制作模块：接受一个友方角色名，返回对应的动图字典：
def character_gif_dic(character_name,faction,mode):
    if mode == None:
        imgId_dict = {
            "attack":character_creator(character_name,"attack",faction),
            "attack2":character_creator(character_name,"attack2",faction),
            "move":character_creator(character_name,"move",faction),
            "reload":character_creator(character_name,"reload",faction),
            "repair":character_creator(character_name,"reload",faction),
            "set":character_creator(character_name,"set",faction),
            "skill":character_creator(character_name,"skill",faction),
            "victory":character_creator(character_name,"victory",faction),
            "victoryloop":character_creator(character_name,"victoryloop",faction),
            "wait":character_creator(character_name,"wait",faction),
            "wait2":character_creator(character_name,"wait2",faction),
        }
        imgId_dict["die"] = character_creator(character_name,"die",faction)
        """
        if faction == "character":
            imgId_dict["die"] = character_creator(character_name,"die",faction)
        else:
            temp_list = ["","2","3"]
            imgId_dict["die"] = character_creator(character_name,"die"+temp_list[random.randint(0,2)],faction)
            if imgId_dict["die"]==None:
                imgId_dict["die"] = character_creator(character_name,"die",faction)
        """
        #加载角色的音效
        _load_sound_to_CHARACTERS_SOUND_DICT(character_name)
    elif mode == "dev":
        imgId_dict = {"wait":character_creator(character_name,"wait",faction)}
    else:
        raise Exception('ZeroEngine-Error: Mode is not supported.')
    return imgId_dict

#为角色创建用于储存音效的文件夹
def autoMkdirForCharacterSounds():
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
            print("ZeroEngine-Notice:A new character call {} has been updated to the data file.".format(name))
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
            print("ZeroEngine-Notice:A new character call {} has been updated to the data file.".format(name))
    if ifAnythingChange == True:
        saveConfig("Data/character_data.yaml",loadData)
    autoMkdirForCharacterSounds()
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
            pygame.mixer.Channel(self.__channel).play(self.__soundsData[kind][random.randint(0,len(self.__soundsData[kind])-1)])