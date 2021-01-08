# cython: language_level=3
from ..basic import *
import threading

#储存角色图片的常量
__CHARACTERS_IMAGE_DICT = {}
#获取特定的角色图片
def getDollImg(self_type,action,imgId):
    return __CHARACTERS_IMAGE_DICT[self_type][action]["img"][imgId]
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
class CHARACTERS_GET_HURT_IMAGE(GameObject):
    def __init__(self,self_type,y,width):
        GameObject.__init__(self,None,y)
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
class Doll(GameObject):
    def __init__(self,DATA,faction,mode):
        GameObject.__init__(self,DATA["x"],DATA["y"])
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
    #设置动作
    def set_action(self,action="wait",ifLoop=True):
        self.reset_imgId(self.__currentAction)
        self.__currentAction = action
        self.__ifActionLoop = ifLoop
        self.__ifActionPlayedOnce = False
    #当前动作
    @property
    def action(self):
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
            raise Exception('LinpgEngine-Error: Character cannot move to a invalid path!')
    #查看是否需要重新渲染地图
    def needUpdateMap(self):
        if self.__reProcessMap == True:
            self.__reProcessMap = False
            return True
        else:
            return False
    #根据路径移动
    def __move_based_on_path(self,MapClass):
        if len(self.__movingPath) > 0:
            if self.x < self.__movingPath[0][0]:
                self.x+=0.05
                self.setFlip(False)
                if self.x >= self.__movingPath[0][0]:
                    self.x = self.__movingPath[0][0]
                    self.__movingPath.pop(0)
                    if MapClass.isAtNight():
                        self.__reProcessMap = True
            elif self.x > self.__movingPath[0][0]:
                self.x-=0.05
                self.setFlip(True)
                if self.x <= self.__movingPath[0][0]:
                    self.x = self.__movingPath[0][0]
                    self.__movingPath.pop(0)
                    if MapClass.isAtNight():
                        self.__reProcessMap = True
            elif self.y < self.__movingPath[0][1]:
                self.y+=0.05
                self.setFlip(True)
                if self.y >= self.__movingPath[0][1]:
                    self.y = self.__movingPath[0][1]
                    self.__movingPath.pop(0)
                    if MapClass.isAtNight():
                        self.__reProcessMap = True
            elif self.y > self.__movingPath[0][1]:
                self.y-=0.05
                self.setFlip(False)
                if self.y <= self.__movingPath[0][1]:
                    self.y = self.__movingPath[0][1]
                    self.__movingPath.pop(0)
                    if MapClass.isAtNight():
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
                raise Exception('LinpgEngine-Error: While you reduce the action points, the module cannot reduce a non-int value!')
        else:
            #作弊模式开启时不扣行动力
            return True
    #获取行动值
    @property
    def current_action_point(self):
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
    #检测是否在对应位置上
    def on_pos(self,pos):
        return is_same_pos(self.get_pos(),pos)
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
    def __blit_doll_img(self,screen,MapClass,action=None,pos=None,alpha=155):
        #调整小人图片的尺寸
        if action == None:
            action =self.__currentAction
        img_of_char = getDollImg(self.type,action,self.__imgId_dict[action]["imgId"])
        img_width = round(MapClass.block_width*1.6)
        img_of_char.set_size(img_width,img_width)
        #调整alpha值
        img_of_char.set_alpha(alpha)
        #反转图片
        if self.ifFlip:
            img_of_char.flip_if_not()
        else:
            img_of_char.flip_back_to_normal()
        #把角色图片画到屏幕上
        if pos == None:
            pos = MapClass.calPosInMap(self.x,self.y)
        img_of_char.set_pos(pos[0]-MapClass.block_width*0.3,pos[1]-MapClass.block_width*0.85)
        img_of_char.draw(screen,console.get_events("dev"))
    def draw(self,screen,MapClass):
        self.__blit_doll_img(screen,MapClass,alpha=self.get_imgAlpaha(self.__currentAction))
        #如果当前动作是移动
        if self.__currentAction == "move" and self.__movingPath != None:
            self.__move_based_on_path(MapClass)
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
                raise Exception('LinpgEngine-Error: self.__ifActionLoop data error: '+self.__ifActionLoop)
        else:
            if self.__imgId_dict[self.__currentAction]["imgId"] > 0:
                self.__imgId_dict[self.__currentAction]["imgId"] -= 1
            else:
                self._ifActionPlayReverse = False
                self.set_action()
    def draw_custom(self,action,pos,screen,MapClass,isContinue=True):
        self.__blit_doll_img(screen,MapClass,action,pos)
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
    def drawUI(self,screen,original_UI_img,MapClass):
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
        xTemp,yTemp = MapClass.calPosInMap(self.x,self.y)
        xTemp += MapClass.block_width*0.25
        yTemp -= MapClass.block_width*0.2
        if self.faction == "character" and self.detection != None:
            eyeImgWidth = round(MapClass.block_width/6*self.eyeImgSize)
            eyeImgHeight = round(MapClass.block_width/10*self.eyeImgSize)
            numberX = (eyeImgWidth - MapClass.block_width/6)/2
            numberY = (eyeImgHeight - MapClass.block_width/10)/2
            if self.detection == True:
                screen.blit(resizeImg(original_UI_img["eye_red"], (eyeImgWidth,eyeImgHeight)),(xTemp+MapClass.block_width*0.51-numberX,yTemp-numberY))
            elif self.detection == False:
                screen.blit(resizeImg(original_UI_img["eye_orange"], (eyeImgWidth,eyeImgHeight)),(xTemp+MapClass.block_width*0.51-numberX,yTemp-numberY))
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
        hpEmptyScale = pygame.transform.scale(original_UI_img["hp_empty"], (round(MapClass.block_width/2), round(MapClass.block_width/10)))
        screen.blit(hpEmptyScale,(xTemp,yTemp))
        screen.blit(pygame.transform.scale(hp_img,(round(MapClass.block_width*percent_of_hp/2),round(MapClass.block_width/10))),(xTemp,yTemp))
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
    def isInAttackRange(self,other,Map):
        attackRange = self.getAttackRange(Map)
        for key in attackRange:
            if (other.x,other.y) in attackRange[key]:
                return True
        return False
    #获取角色的攻击范围
    def getAttackRange(self,Map):
        attacking_range = {"near":[],"middle":[],"far":[]}
        for y in range(self.y-self.max_effective_range,self.y+self.max_effective_range+1):
            if y < self.y:
                for x in range(self.x-self.max_effective_range-(y-self.y),self.x+self.max_effective_range+(y-self.y)+1):
                    if Map.row>y>=0 and Map.column>x>=0:
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
                    elif Map.row>y>=0 and Map.column>x>=0:
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

#友方角色类
class FriendlyCharacter(Doll):
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
        #转换坐标
        x,y = convert_pos(pos)
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

#敌对角色类
class HostileCharacter(Doll):
    def __init__(self,theSangvisFerrisDataDic,defaultData,mode=None):
        for key in theSangvisFerrisDataDic:
            defaultData[key] = theSangvisFerrisDataDic[key]
        Doll.__init__(self,defaultData,"sangvisFerri",mode)
        self.patrol_path = defaultData["patrol_path"] if "patrol_path" in defaultData else []
    def setFlipBasedPos(self,pos):
        #转换坐标
        x,y = convert_pos(pos)
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
    def make_decision(self,Map,friendlyCharacterData,hostileCharacterData,the_characters_detected_last_round):
        character_with_min_hp = None
        characters_can_be_detect = []
        #检测是否有可以立马攻击的敌人
        for character in friendlyCharacterData:
            if friendlyCharacterData[character].detection == True and friendlyCharacterData[character].current_hp>0:
                #如果现在还没有可以直接攻击的角色或者当前历遍到角色的血量比最小值要高
                if character_with_min_hp == None or friendlyCharacterData[character].current_hp <= friendlyCharacterData[character_with_min_hp[0]].current_hp:
                    temp_distance = abs(friendlyCharacterData[character].x-self.x)+abs(friendlyCharacterData[character].y-self.y)
                    if "far" in self.effective_range and self.effective_range["far"][0] <= temp_distance <= self.effective_range["far"][1]:
                        character_with_min_hp = (character,"far")
                    elif "middle" in self.effective_range and self.effective_range["middle"][0] <= temp_distance <= self.effective_range["middle"][1]:
                        character_with_min_hp = (character,"middle")
                    elif "near" in self.effective_range and self.effective_range["near"][0] <= temp_distance <= self.effective_range["near"][1]:
                        if character_with_min_hp == None or friendlyCharacterData[character].current_hp <= friendlyCharacterData[character_with_min_hp[0]].current_hp:
                            character_with_min_hp = (character,"near")
                #按顺序按血量从小到大排列可以检测到的角色
                if len(characters_can_be_detect) == 0:
                    characters_can_be_detect = [character]
                else:
                    for i in range(len(characters_can_be_detect)):
                        if friendlyCharacterData[character].current_hp < friendlyCharacterData[characters_can_be_detect[i]].current_hp:
                            characters_can_be_detect.insert(i,character)
        if character_with_min_hp != None:
            #[行动, 需要攻击的目标, 所在范围]
            return {"action": "attack",
            "target": character_with_min_hp[0],
            "target_area": character_with_min_hp[1]
            }
        elif self.kind == "HOC":
            return {"action": "stay"}
        else:
            #先检测是否有可以移动后攻击的敌人
            ap_need_to_attack = 5
            max_moving_routes_for_attacking = int((self.max_action_point - ap_need_to_attack)/2)
            characters_can_be_attacked = {}
            #再次历遍所有characters_data以获取所有当前角色可以在移动后攻击到的敌对阵营角色
            for character in friendlyCharacterData:
                if friendlyCharacterData[character].detection == True and friendlyCharacterData[character].current_hp>0:
                    #检测当前角色移动后足以攻击到这个敌对阵营的角色
                    the_route = Map.findPath(self.get_pos(),friendlyCharacterData[character].get_pos(),hostileCharacterData,friendlyCharacterData,max_moving_routes_for_attacking,[character])
                    if len(the_route)>0:
                        temp_area = None
                        temp_distance = abs(friendlyCharacterData[character].x-the_route[-1][0])+abs(friendlyCharacterData[character].y-the_route[-1][1])
                        if "far" in self.effective_range and self.effective_range["far"][0] <= temp_distance <= self.effective_range["far"][1]:
                            temp_area = "far"
                        elif "middle" in self.effective_range and self.effective_range["middle"][0] <= temp_distance <= self.effective_range["middle"][1]:
                            temp_area = "middle"
                        elif "near" in self.effective_range and self.effective_range["near"][0] <= temp_distance <= self.effective_range["near"][1]:
                            temp_area = "near"
                        if temp_area != None:
                            if (friendlyCharacterData[character].x,friendlyCharacterData[character].y) in the_route:
                                the_route.remove((friendlyCharacterData[character].x,friendlyCharacterData[character].y))
                            characters_can_be_attacked[character] = {"route":the_route,"area":temp_area}
            #如果存在可以在移动后攻击到的敌人
            if len(characters_can_be_attacked) >= 1:
                character_with_min_hp = None
                for key in characters_can_be_attacked:
                    if character_with_min_hp == None or friendlyCharacterData[key].current_hp < friendlyCharacterData[character_with_min_hp].current_hp:
                        character_with_min_hp = key
                return {
                    "action":"move&attack",
                    "route":characters_can_be_attacked[character_with_min_hp]["route"],
                    "target":character_with_min_hp,
                    "target_area": characters_can_be_attacked[character_with_min_hp]["area"]
                }
            #如果不存在可以在移动后攻击到的敌人
            elif len(characters_can_be_attacked) == 0:
                #如果这一回合没有敌人暴露
                if len(characters_can_be_detect) == 0:
                    #如果上一个回合没有敌人暴露
                    if len(the_characters_detected_last_round) == 0:
                        #如果敌人没有巡逻路线
                        if len(self.patrol_path) == 0:
                            return {"action": "stay"}
                        #如果敌人有巡逻路线
                        else:
                            the_route = Map.findPath(self.get_pos(),self.patrol_path[0],hostileCharacterData,friendlyCharacterData,max_moving_routes_for_attacking)
                            if len(the_route) > 0:
                                return {"action": "move","route":the_route}
                            else:
                                raise Exception('A sangvisFerri cannot find it path!')
                    #如果上一个回合有敌人暴露
                    else:
                        that_character = None
                        for each_chara in the_characters_detected_last_round:
                            if that_character== None:
                                that_character = each_chara
                            else:
                                if hostileCharacterData[that_character].current_hp < hostileCharacterData[that_character].current_hp:
                                    that_character = that_character
                        targetPosTemp = (the_characters_detected_last_round[that_character][0],the_characters_detected_last_round[that_character][1])
                        the_route = Map.findPath(self.get_pos(),targetPosTemp,hostileCharacterData,friendlyCharacterData,max_moving_routes_for_attacking,[that_character])
                        if len(the_route) > 0:
                            if (targetPosTemp) in the_route:
                                the_route.remove(targetPosTemp)
                            return {"action": "move","route":the_route}
                        else:
                            return {"action": "stay"}
                        
                #如果这一回合有敌人暴露
                else:
                    targetPosTemp = (friendlyCharacterData[characters_can_be_detect[0]].x,friendlyCharacterData[characters_can_be_detect[0]].y)
                    the_route = Map.findPath(self.get_pos(),targetPosTemp,hostileCharacterData,friendlyCharacterData,max_moving_routes_for_attacking,[characters_can_be_detect[0]])
                    if len(the_route) > 0:
                        if (targetPosTemp) in the_route:
                            the_route.remove(targetPosTemp)
                        return {"action": "move","route":the_route}
                    else:
                        return {"action": "stay"}

#初始化角色信息
class CharacterDataLoader(threading.Thread):
    def __init__(self,alliances,enemies,mode):
        threading.Thread.__init__(self)
        self.DATABASE = loadCharacterData()
        self.alliances = alliances
        self.enemies = enemies
        self.totalNum = len(alliances)+len(enemies)
        self.currentID = 0
        self.mode = mode
    def run(self):
        for key,value in self.alliances.items():
            if isinstance(value,FriendlyCharacter):
                value.loadImg()
            else:
                self.alliances[key] = FriendlyCharacter(value,self.DATABASE[value["type"]],self.mode)
            self.currentID+=1
        for key,value in self.enemies.items():
            if isinstance(value,HostileCharacter):
                value.loadImg()
            else:
                self.enemies[key] = HostileCharacter(value,self.DATABASE[value["type"]],self.mode)
            self.currentID+=1
    def getResult(self):
        return self.alliances,self.enemies

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
            __CHARACTERS_IMAGE_DICT[character_name][action] = {"img":numpy.asarray([SrcalphaSurface(\
                "Assets/image/{0}/{1}/{2}/{3}_{4}_{5}.png".format(faction,character_name,action,character_name,action,i)\
                    ,0,0) for i in range(files_amount)]),"imgNum":files_amount}
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
        raise Exception('LinpgEngine-Error: Mode is not supported.')
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