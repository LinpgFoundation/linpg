# cython: language_level=3
from .characterModule import *

#储存角色图片的常量
_CHARACTERS_IMAGE_SYS = CharacterImageManagement()
#储存角色音效的常量
_CHARACTERS_SOUND_SYSTEM = CharacterSoundManagement(5)
#角色UI的文字数据
_ENTITY_UI_FONT = createFont(get_setting("Screen_size_x")/192)

#人形模块
class Entity(GameObject):
    def __init__(self,DATA:dict,faction:str,mode:str) -> None:
        GameObject.__init__(self,DATA["x"],DATA["y"])
        #最大行动值
        self.max_action_point = DATA["action_point"]
        #当前行动值
        self.__current_action_point = DATA["action_point"]
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
        self.__imgId_dict = _CHARACTERS_IMAGE_SYS.createGifDict(self.type,faction,mode)
        #加载角色的音效
        if mode != "dev":
            _CHARACTERS_SOUND_SYSTEM.add(self.type)
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
        #idle动作
        self.idle_action = "wait"
        #当前动作
        self.__currentAction = self.idle_action
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
    """角色动作参数管理"""
    #当前动作
    @property
    def action(self): return self.__currentAction
    #获取当前动作，建议使用self.action
    def get_action(self) -> str: return self.__currentAction
    #设置动作
    def set_action(self,action:str="wait",ifLoop:bool=True) -> None:
        self.reset_imgId(self.__currentAction)
        self.__currentAction = action
        self.__ifActionLoop = ifLoop
        self.__ifActionPlayedOnce = False
    #是否闲置
    def is_idle(self) -> bool: return self.__currentAction == self.idle_action
    #获取角色特定动作的图片播放ID
    def get_imgId(self,action:str):
        action = self.__imgId_dict[action]
        if action != None:
            return action["imgId"]
        else:
            return None
    #获取角色特定动作的图片总数量
    def get_imgNum(self,action:str) -> int: return _CHARACTERS_IMAGE_SYS.get_img_num(self.type,action)
    #设定角色特定动作的图片播放ID
    def set_imgId(self,action:str,imgId:int) -> None: self.__imgId_dict[action]["imgId"] = imgId
    #重置角色特定动作的图片播放ID
    def reset_imgId(self,action:str) -> None: self.set_imgId(action,0)
    #增加角色特定动作的图片播放ID
    def add_imgId(self,action:str,amount:int=1) -> None: self.__imgId_dict[action]["imgId"] += amount
    #获取角色特定动作的图片透明度
    def get_imgAlpaha(self,action:str) -> int: return self.__imgId_dict[action]["alpha"]
    #设定角色特定动作的图片透明度
    def set_imgAlpaha(self,action:str,alpha:int) -> None: self.__imgId_dict[action]["alpha"] = alpha
    """角色行动值参数管理"""
    #当前行动值
    @property
    def current_action_point(self): return self.__current_action_point
    #获取当前行动值,建议使用self.current_action_point
    def get_current_action_point(self) -> int : return self.__current_action_point
    #设置当前行动值，不建议非开发者使用
    def set_current_action_point(self,point:int) -> None: self.__current_action_point = int(point)
    #重置行动点数
    def reset_action_point(self) -> None: self.set_current_action_point(self.max_action_point)
    #是否有足够的开发点数
    def have_enough_action_point(self,value:int) -> bool: return self.__current_action_point >= value
    #尝试减少行动值，如果成功，返回true,失败则返回false
    def try_reduce_action_point(self,value:int) -> bool:
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
    """角色血量参数管理"""
    #治愈
    def heal(self,hpHealed:int) -> None: self.current_hp += hpHealed
    #降低血量
    def decreaseHp(self,damage:int):
        damage = abs(damage)
        #如果有可再生的护甲
        if self.current_recoverable_armor > 0:
            #如果伤害大于护甲值,则以护甲值为最大护甲将承受的伤害
            if damage > self.current_recoverable_armor:
                damage_take_by_armor = randomInt(0,self.current_recoverable_armor)
            #如果伤害小于护甲值,则以伤害为最大护甲将承受的伤害
            else:
                damage_take_by_armor = randomInt(0,damage)
            self.current_recoverable_armor -= damage_take_by_armor
            damage -= damage_take_by_armor
        #如果有不可再生的护甲
        if self.irrecoverable_armor > 0 and damage > 0:
            if damage > self.irrecoverable_armor:
                damage_take_by_armor = randomInt(0,self.irrecoverable_armor)
            #如果伤害小于护甲值,则以伤害为最大护甲将承受的伤害
            else:
                damage_take_by_armor = randomInt(0,damage)
            self.irrecoverable_armor -= damage_take_by_armor
            damage -= damage_take_by_armor
        #如果还有伤害,则扣除血量
        if damage > 0:
            self.current_hp -= damage
        #如果角色血量小等于0，进入死亡状态
        if self.current_hp <= 0:
            self.current_hp = 0
            self.set_action("die",None)
    #被一个Entity攻击
    def attackBy(self,attacker):
        damage = randomInt(attacker.min_damage,attacker.max_damage)
        self.decreaseHp(damage)
        return damage
    """其他"""
    #设置反转
    def setFlip(self,theBool:bool) -> None:self.ifFlip = theBool
    #播放角色声音
    def playSound(self,kind_of_sound:str) -> None: _CHARACTERS_SOUND_SYSTEM.play(self.type,kind_of_sound)
    #设置需要移动的路径
    def move_follow(self,path) -> None:
        if isinstance(path,(list,tuple)) and len(path)>0:
            self.__movingPath = path
            self.set_action("move")
        else:
            raise Exception('LinpgEngine-Error: Character cannot move to a invalid path!')
    #根据路径移动
    def __move_based_on_path(self,MapClass) -> None:
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
    #查看是否需要重新渲染地图
    def needUpdateMap(self) -> bool:
        if self.__reProcessMap:
            self.__reProcessMap = False
            return True
        else:
            return False
    #加载图片
    def loadImg(self) -> None:
        for theAction in self.__imgId_dict:
            _CHARACTERS_IMAGE_SYS.loadImageCollection(self.type,theAction,self.faction)
        _CHARACTERS_SOUND_SYSTEM.add(self.type)
    #调整角色的隐蔽度
    def noticed(self,force:bool=False) -> None:
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
    #查看是否一个Entity在该角色的附近
    def near(self,otherEntity) -> bool:
        if self.x == otherEntity.x:
            if abs(self.y-otherEntity.y) <= 1:
                return True
            else:
                return False
        elif self.y == otherEntity.y:
            if abs(self.x-otherEntity.x) <= 1:
                return True
            else:
                return False
        else:
            return False
    #判断是否在攻击范围内
    def isInAttackRange(self,otherEntity,Map) -> bool:
        attackRange = self.getAttackRange(Map)
        for key in attackRange:
            if (otherEntity.x,otherEntity.y) in attackRange[key]:
                return True
        return False
    #获取角色的攻击范围
    def getAttackRange(self,Map) -> dict:
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
    """画出角色"""
    #把角色画到screen上
    def __blit_entity_img(self,screen,MapClass,action=None,pos=None,alpha=155) -> None:
        #调整小人图片的尺寸
        if action == None:
            action = self.__currentAction
        img_of_char = _CHARACTERS_IMAGE_SYS.get_img(self.type,action,self.__imgId_dict[action]["imgId"])
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
    def draw(self,screen,MapClass) -> None:
        self.__blit_entity_img(screen,MapClass,alpha=self.get_imgAlpaha(self.__currentAction))
        #如果当前动作是移动
        if self.__currentAction == "move" and self.__movingPath != None:
            self.__move_based_on_path(MapClass)
        #如果角色图片还没播放完
        if not self._ifActionPlayReverse:
            if self.__imgId_dict[self.__currentAction]["imgId"] < self.get_imgNum(self.__currentAction)-1:
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
    def draw_custom(self,action,pos,screen,MapClass,isContinue=True) -> None:
        self.__blit_entity_img(screen,MapClass,action,pos)
        #调整id，并返回对应的bool状态
        if self.__imgId_dict[action]["imgId"] < self.get_imgNum(action)-1:
            self.__imgId_dict[action]["imgId"] += 1
            return True
        else:
            if isContinue == True:
                self.__imgId_dict[action]["imgId"] = 0
                return True
            else:
                return False
    def drawUI(self,screen,original_UI_img,MapClass) -> None:
        hp_img = None
        if self.dying == False:
            if original_UI_img != None:
                hp_img = original_UI_img["hp_green"]
            current_hp_to_display = _ENTITY_UI_FONT.render("{}/{}".format(self.current_hp,self.max_hp),get_fontMode(),(0,0,0))
            percent_of_hp = self.current_hp/self.max_hp
        else:
            if original_UI_img != None:
                hp_img = original_UI_img["hp_red"]
            current_hp_to_display = _ENTITY_UI_FONT.render("{}/3".format(self.dying),get_fontMode(),(0,0,0))
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
        hpEmptyScale = resizeImg(original_UI_img["hp_empty"],(MapClass.block_width/2, MapClass.block_width/10))
        screen.blit(hpEmptyScale,(xTemp,yTemp))
        screen.blit(resizeImg(hp_img,(MapClass.block_width*percent_of_hp/2,MapClass.block_width/10)),(xTemp,yTemp))
        displayInCenter(current_hp_to_display,hpEmptyScale,xTemp,yTemp,screen)