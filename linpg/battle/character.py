# cython: language_level=3
from .entity import *

#攻击所需的AP
AP_IS_NEEDED_TO_ATTACK:int = 5
AP_IS_NEEDED_TO_MOVE_ONE_BLOCK:int = 2

#友方角色类
class FriendlyCharacter(Entity):
    def __init__(self, theCharacterDataDic:dict, defaultData:dict, mode:str) -> None:
        for key in theCharacterDataDic:
            defaultData[key] = theCharacterDataDic[key]
        super().__init__(defaultData,"character",mode)
        self.bullets_carried = defaultData["bullets_carried"]
        self.skill_effective_range = defaultData["skill_effective_range"]
        self.max_skill_range = calculate_range(defaultData["skill_effective_range"])
        self.skill_cover_range = defaultData["skill_cover_range"]
        self._detection = defaultData["detection"] if "detection" in defaultData and defaultData["detection"] is not None else 0
        #生成被察觉的图标
        self.__beNoticedImage = EntityDynamicProgressBarSurface()
        self.__beNoticedImage.set_percentage(self._detection/100)
        #尝试加载重创立绘
        try:
            self.__getHurtImage = EntityGetHurtImage(self.type,display.get_height()/4,display.get_height()/2)
        except BaseException:
            throw_exception("warning","Character {} does not have damaged artwork!".format(self.type))
            self.__getHurtImage = None
            if not os.path.exists("Assets/image/npc_icon/{}.png".format(self.type)): print("And also its icon.")
    def load_image(self) -> None:
        super().load_image()
        self.__getHurtImage.add(self.type)
        self.__beNoticedImage.load_image()
    @property
    def detection(self) -> int: return self._detection
    @property
    def is_detected(self) -> bool: return self._detection >= 100
    #调整角色的隐蔽度
    def notice(self, value:int=10) -> None:
        self._detection += value
        if self._detection > 100:
            self._detection = 100
        elif self._detection < 0:
            self._detection = 0
        self.__beNoticedImage.set_percentage(self._detection/100)
    def decreaseHp(self, damage:int) -> None:
        super().decreaseHp(damage)
        #如果角色在被攻击后处于濒死状态
        if not self.is_alive() and not self.dying and self.kind != "HOC":
            self.dying = DYING_ROUND_LIMIT
            if self.__getHurtImage is not None:
                self.__getHurtImage.x = -self.__getHurtImage.width
                self.__getHurtImage.alpha = 255
                self.__getHurtImage.yToGo = 255
                self.play_sound("injured")
    def heal(self, hpHealed:int) -> None:
        super().heal(hpHealed)
        if self.dying is not False:
            self.dying = False
            self._if_play_action_in_reversing = True
    def drawUI(self, surface:ImageSurface, MapClass:object) -> None:
        blit_pos = super().drawUI(surface,MapClass)
        #展示被察觉的程度
        if self._detection > 0:
            #参数
            eyeImgWidth = round(MapClass.block_width/6)
            eyeImgHeight = round(MapClass.block_width/10)
            numberX = (eyeImgWidth - MapClass.block_width/6)/2
            numberY = (eyeImgHeight - MapClass.block_width/10)/2
            #根据参数调整图片
            self.__beNoticedImage.set_size(eyeImgWidth,eyeImgHeight)
            self.__beNoticedImage.set_pos(blit_pos[0]+MapClass.block_width*0.51-numberX,blit_pos[1]-numberY)
            self.__beNoticedImage.draw(surface)
        #重创立绘
        if self.__getHurtImage is not None and self.__getHurtImage.x is not None:
            self.__getHurtImage.draw(surface,self.type)
            if self.__getHurtImage.x < self.__getHurtImage.width/4:
                self.__getHurtImage.x += self.__getHurtImage.width/25
            else:
                if self.__getHurtImage.yToGo > 0:
                    self.__getHurtImage.yToGo -= 5
                else:
                    if self.__getHurtImage.alpha > 0:
                        self.__getHurtImage.alpha -= 2
                    else:
                        self.__getHurtImage.x = None

#敌对角色类
class HostileCharacter(Entity):
    def __init__(self, theSangvisFerrisDataDic:dict, defaultData:dict, mode:str):
        for key in theSangvisFerrisDataDic:
            defaultData[key] = theSangvisFerrisDataDic[key]
        super().__init__(defaultData,"sangvisFerri",mode)
        self.__patrol_path = deque(defaultData["patrol_path"]) if "patrol_path" in defaultData else deque()
        self._vigilance = 0
        self.__vigilanceImage = EntityDynamicProgressBarSurface("vertical")
        self.__vigilanceImage.set_percentage(self._vigilance/100)
    def load_image(self) -> None:
        super().load_image()
        self.__vigilanceImage.load_image()
    def alert(self, value:int=10) -> None:
        self._vigilance += value
        #防止警觉度数值超过阈值
        if self._vigilance > 100:
            self._vigilance = 100
        elif self._vigilance < 0:
            self._vigilance = 0
        else:
            pass
        self.__vigilanceImage.set_percentage(self._vigilance/100)
    @property
    def vigilance(self) -> int: return self._vigilance
    @property
    def is_alert(self) -> bool: return self._vigilance >= 100
    #画UI - 列如血条
    def drawUI(self, surface:ImageSurface, MapClass:object) -> None:
        blit_pos = super().drawUI(surface,MapClass)
        #展示警觉的程度
        if self._vigilance > 0:
            #参数
            eyeImgWidth = round(MapClass.block_width/6)
            eyeImgHeight = round(MapClass.block_width/6)
            numberX = (eyeImgWidth - MapClass.block_width/6)/2
            numberY = (eyeImgHeight - MapClass.block_width/10)/2
            #根据参数调整图片
            self.__vigilanceImage.set_size(eyeImgWidth,eyeImgHeight)
            self.__vigilanceImage.set_pos(blit_pos[0]+MapClass.block_width*0.51-numberX,blit_pos[1]-numberY)
            self.__vigilanceImage.draw(surface,False)
    def make_decision(self, Map:object, friendlyCharacterData:dict, hostileCharacterData:dict, the_characters_detected_last_round:dict) -> queue:
        #存储友方角色价值榜
        target_value_board = []
        for name,theCharacter in friendlyCharacterData.items():
            if theCharacter.is_alive() and theCharacter.is_detected:
                weight = 0
                #计算距离的分数
                weight += abs(self.x-theCharacter.x)+abs(self.y-theCharacter.y)
                #计算血量分数
                weight += self.current_hp*self.hp_precentage
                target_value_board.append((name,weight))
        #最大移动距离
        blocks_can_move = int((self.max_action_point)/AP_IS_NEEDED_TO_MOVE_ONE_BLOCK)
        #角色将会在该回合采取的行动
        actions = queue.Queue()
        #如果角色有可以攻击的对象，且角色至少有足够的行动点数攻击
        if len(target_value_board) > 0 and self.max_action_point > AP_IS_NEEDED_TO_ATTACK:
            action_point_can_use = self.max_action_point
            #筛选分数最低的角色作为目标
            target = target_value_board[0][0]
            min_weight = target_value_board[0][1]
            for data in target_value_board[1:]:
                if data[1] < min_weight:
                    min_weight = data[1]
                    target = data[0]
            targetCharacterData = friendlyCharacterData[target]
            if self.can_attack(targetCharacterData):
                actions.put(DecisionHolder("attack",tuple((target,self.range_target_in(targetCharacterData)))))
                action_point_can_use -= AP_IS_NEEDED_TO_ATTACK
                """
                if action_point_can_use > AP_IS_NEEDED_TO_ATTACK:
                    if self.hp_precentage > 0.2:
                        #如果自身血量正常，则应该考虑再次攻击角色
                        actions.put(DecisionHolder("attack",target))
                        action_point_can_use -= AP_IS_NEEDED_TO_ATTACK
                    else:
                        pass
                """
            else:
                #寻找一条能到达该角色附近的线路
                the_route = Map.findPath(self.pos,targetCharacterData.pos,hostileCharacterData,friendlyCharacterData,blocks_can_move,[target])
                if len(the_route) > 0:
                    potential_attacking_pos_index = {}
                    for i in range(len(the_route)-int(AP_IS_NEEDED_TO_ATTACK/AP_IS_NEEDED_TO_MOVE_ONE_BLOCK+1)):
                        #当前正在处理的坐标
                        pos_on_route = the_route[i]
                        #获取可能的攻击范围
                        range_target_in_if_can_attack = self.range_target_in(targetCharacterData,pos_on_route)
                        if range_target_in_if_can_attack is not None and range_target_in_if_can_attack not in potential_attacking_pos_index:
                            potential_attacking_pos_index[range_target_in_if_can_attack] = i+1
                            if range_target_in_if_can_attack == "near":
                                break
                    if "near" in potential_attacking_pos_index:
                        actions.put(DecisionHolder("move",the_route[:potential_attacking_pos_index["near"]]))
                        actions.put(DecisionHolder("attack",tuple((target,"near"))))
                    elif "middle" in potential_attacking_pos_index:
                        actions.put(DecisionHolder("move",the_route[:potential_attacking_pos_index["middle"]]))
                        actions.put(DecisionHolder("attack",tuple((target,"middle"))))
                    elif "far" in potential_attacking_pos_index:
                        actions.put(DecisionHolder("move",the_route[:potential_attacking_pos_index["far"]]))
                        actions.put(DecisionHolder("attack",tuple((target,"far"))))
                    else:
                        actions.put(DecisionHolder("move",the_route))
                else:
                    throw_exception("error","A hostile character cannot find a valid path when trying to attack {}!".format(target))
        #如果角色没有可以攻击的对象，则查看角色是否需要巡逻
        elif len(self.__patrol_path) > 0:
            #如果巡逻坐标点只有一个（意味着角色需要在该坐标上长期镇守）
            if len(self.__patrol_path) == 1:
                if not is_same_pos(self.pos,self.__patrol_path[0]):
                    the_route = Map.findPath(self.pos,self.__patrol_path[0],hostileCharacterData,friendlyCharacterData,blocks_can_move)
                    if len(the_route) > 0:
                        actions.put(DecisionHolder("move",the_route))
                    else:
                        throw_exception("error","A hostile character cannot find a valid path!")
                else:
                    #如果角色在该点上，则原地待机
                    pass
            #如果巡逻坐标点有多个
            else:
                the_route = Map.findPath(self.pos,self.__patrol_path[0],hostileCharacterData,friendlyCharacterData,blocks_can_move)
                if len(the_route) > 0:
                    actions.put(DecisionHolder("move",the_route))
                    #如果角色在这次移动后到达了最近的巡逻点，则应该更新最近的巡逻点
                    if is_same_pos(the_route[-1],self.__patrol_path[0]): self.__patrol_path.append(self.__patrol_path.popleft())
                else:
                    throw_exception("error","A hostile character cannot find a valid path!")
        else:
            pass
        #放回一个装有指令的列表
        return actions

#初始化角色信息
class CharacterDataLoader(threading.Thread):
    def __init__(self, alliances:dict, enemies:dict, mode:str) -> None:
        super().__init__()
        self.DATABASE = loadCharacterData()
        self.alliances = deepcopy(alliances)
        self.enemies = deepcopy(enemies)
        self.totalNum = len(alliances)+len(enemies)
        self.currentID = 0
        self.mode = mode
    def run(self) -> None:
        for key,value in self.alliances.items():
            if isinstance(value,FriendlyCharacter):
                value.load_image()
            else:
                self.alliances[key] = FriendlyCharacter(value,self.DATABASE[value["type"]],self.mode)
            self.currentID+=1
            if get_setting("DeveloperMode"): print("total: {0}, current: {1}".format(self.totalNum,self.currentID))
        for key,value in self.enemies.items():
            if isinstance(value,HostileCharacter):
                value.load_image()
            else:
                self.enemies[key] = HostileCharacter(value,self.DATABASE[value["type"]],self.mode)
            self.currentID += 1
            if get_setting("DeveloperMode"): print("total: {0}, current: {1}".format(self.totalNum,self.currentID))
    def getResult(self) -> tuple: return self.alliances,self.enemies