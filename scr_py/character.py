# cython: language_level=3
from .entity import *

#友方角色类
class FriendlyCharacter(Entity):
    def __init__(self,theCharacterDataDic:dict,defaultData:dict,mode=None) -> None:
        for key in theCharacterDataDic:
            defaultData[key] = theCharacterDataDic[key]
        Entity.__init__(self,defaultData,"character",mode)
        self.bullets_carried = defaultData["bullets_carried"]
        self.skill_effective_range = defaultData["skill_effective_range"]
        self.max_skill_range = calculate_range(defaultData["skill_effective_range"])
        self.skill_cover_range = defaultData["skill_cover_range"]
        self._detection = defaultData["detection"] if "detection" in defaultData and defaultData["detection"] != None else 0
        if self.kind != "HOC":
            try:
                self.ImageGetHurt = CharacterGetHurtImageManagement(self.type,get_setting("Screen_size_y")/4,get_setting("Screen_size_y")/2)
            except BaseException:
                print('警告：角色 {} 没有对应的破衣动画'.format(defaultData["type"]))
                if not os.path.exists("Assets/image/npc_icon/{}.png".format(defaultData["type"])):
                    print("而且你也忘了加入对应的头像")
    @property
    def detection(self) -> int: return self._detection
    #调整角色的隐蔽度
    def noticed(self,value:int=10,force:bool=False) -> None:
        if not force:
            self._detection += value
            if self._detection > 100:
                self._detection = 100
            elif self._detection < 0:
                self._detection = 0
        elif force:
            self._detection = 100
        else:
            raise Exception("LinpgEngine-Error: The force has to be a bool not {}".format(force))
    def loadImg(self) -> None:
        super().loadImg()
        self.ImageGetHurt.add(self.type)
    def attackBy(self,attacker,result_of_round):
        damage = randomInt(attacker.min_damage,attacker.max_damage)
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
    def drawUI(self,screen,original_UI_img,MapClass) -> None:
        blit_pos = super().drawUI(screen,original_UI_img,MapClass)
        #展示被察觉的程度
        if self._detection > 0:
            #参数
            eyeImgWidth = round(MapClass.block_width/6)
            eyeImgHeight = round(MapClass.block_width/10)
            numberX = (eyeImgWidth - MapClass.block_width/6)/2
            numberY = (eyeImgHeight - MapClass.block_width/10)/2
            #根据参数调整图片
            original_UI_img["eyeImg"].set_size(eyeImgWidth,eyeImgHeight)
            original_UI_img["eyeImg"].set_pos(blit_pos[0]+MapClass.block_width*0.51-numberX,blit_pos[1]-numberY)
            original_UI_img["eyeImg"].set_percentage(self._detection/100)
            original_UI_img["eyeImg"].draw(screen)
        #重创立绘
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

#敌对角色类
class HostileCharacter(Entity):
    def __init__(self,theSangvisFerrisDataDic,defaultData,mode=None):
        for key in theSangvisFerrisDataDic:
            defaultData[key] = theSangvisFerrisDataDic[key]
        Entity.__init__(self,defaultData,"sangvisFerri",mode)
        self.patrol_path = defaultData["patrol_path"] if "patrol_path" in defaultData else []
        self._vigilance = 0
    def alert(self,value:int=10) -> None:
        self._vigilance += value
        if self._vigilance > 100:
            self._vigilance = 100
        elif self._vigilance < 0:
            self._vigilance = 0
    @property
    def vigilance(self) -> int: return self._vigilance
    @property
    def is_alert(self) -> bool: return True if self._vigilance >= 100 else False
    def drawUI(self,screen,original_UI_img,MapClass) -> None:
        blit_pos = super().drawUI(screen,original_UI_img,MapClass)
        #展示警觉的程度
        if self._vigilance > 0:
            #参数
            eyeImgWidth = round(MapClass.block_width/6)
            eyeImgHeight = round(MapClass.block_width/6)
            numberX = (eyeImgWidth - MapClass.block_width/6)/2
            numberY = (eyeImgHeight - MapClass.block_width/10)/2
            #根据参数调整图片
            original_UI_img["vigilanceImg"].set_size(eyeImgWidth,eyeImgHeight)
            original_UI_img["vigilanceImg"].set_pos(blit_pos[0]+MapClass.block_width*0.51-numberX,blit_pos[1]-numberY)
            original_UI_img["vigilanceImg"].set_percentage(self._vigilance/100)
            original_UI_img["vigilanceImg"].draw(screen)
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
            if console.get_events("dev"): print("total: {0}, current: {1}".format(self.totalNum,self.currentID))
        for key,value in self.enemies.items():
            if isinstance(value,HostileCharacter):
                value.loadImg()
            else:
                self.enemies[key] = HostileCharacter(value,self.DATABASE[value["type"]],self.mode)
            self.currentID+=1
            if console.get_events("dev"): print("total: {0}, current: {1}".format(self.totalNum,self.currentID))
    def getResult(self):
        return self.alliances,self.enemies