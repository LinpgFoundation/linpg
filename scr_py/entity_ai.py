# cython: language_level=3
"""AI系统"""
def AI(aiInControl,theMap,characters_data,sangvisFerris_data,the_characters_detected_last_round):
    character_with_min_hp = None
    characters_can_be_detect = []
    #检测是否有可以立马攻击的敌人
    for character in characters_data:
        if characters_data[character].detection == True and characters_data[character].current_hp>0:
            #如果现在还没有可以直接攻击的角色或者当前历遍到角色的血量比最小值要高
            if character_with_min_hp == None or characters_data[character].current_hp <= characters_data[character_with_min_hp[0]].current_hp:
                temp_distance = abs(characters_data[character].x-sangvisFerris_data[aiInControl].x)+abs(characters_data[character].y-sangvisFerris_data[aiInControl].y)
                if "far" in sangvisFerris_data[aiInControl].effective_range and sangvisFerris_data[aiInControl].effective_range["far"][0] <= temp_distance <= sangvisFerris_data[aiInControl].effective_range["far"][1]:
                    character_with_min_hp = (character,"far")
                elif "middle" in sangvisFerris_data[aiInControl].effective_range and sangvisFerris_data[aiInControl].effective_range["middle"][0] <= temp_distance <= sangvisFerris_data[aiInControl].effective_range["middle"][1]:
                    character_with_min_hp = (character,"middle")
                elif "near" in sangvisFerris_data[aiInControl].effective_range and sangvisFerris_data[aiInControl].effective_range["near"][0] <= temp_distance <= sangvisFerris_data[aiInControl].effective_range["near"][1]:
                    if character_with_min_hp == None or characters_data[character].current_hp <= characters_data[character_with_min_hp[0]].current_hp:
                        character_with_min_hp = (character,"near")
            #按顺序按血量从小到大排列可以检测到的角色
            if len(characters_can_be_detect) == 0:
                characters_can_be_detect = [character]
            else:
                for i in range(len(characters_can_be_detect)):
                    if characters_data[character].current_hp < characters_data[characters_can_be_detect[i]].current_hp:
                        characters_can_be_detect.insert(i,character)
    if character_with_min_hp != None:
        #[行动, 需要攻击的目标, 所在范围]
        return {"action": "attack",
        "target": character_with_min_hp[0],
        "target_area": character_with_min_hp[1]
        }
    elif sangvisFerris_data[aiInControl].kind == "HOC":
        return {"action": "stay"}
    else:
        #先检测是否有可以移动后攻击的敌人
        ap_need_to_attack = 5
        max_moving_routes_for_attacking = int((sangvisFerris_data[aiInControl].max_action_point - ap_need_to_attack)/2)
        characters_can_be_attacked = {}
        #再次历遍所有characters_data以获取所有当前角色可以在移动后攻击到的敌对阵营角色
        for character in characters_data:
            if characters_data[character].detection == True and characters_data[character].current_hp>0:
                #检测当前角色移动后足以攻击到这个敌对阵营的角色
                the_route = theMap.findPath(sangvisFerris_data[aiInControl],characters_data[character],sangvisFerris_data,characters_data,max_moving_routes_for_attacking,[character])
                if len(the_route)>0:
                    temp_area = None
                    temp_distance = abs(characters_data[character].x-the_route[-1][0])+abs(characters_data[character].y-the_route[-1][1])
                    if "far" in sangvisFerris_data[aiInControl].effective_range and sangvisFerris_data[aiInControl].effective_range["far"][0] <= temp_distance <= sangvisFerris_data[aiInControl].effective_range["far"][1]:
                        temp_area = "far"
                    elif "middle" in sangvisFerris_data[aiInControl].effective_range and sangvisFerris_data[aiInControl].effective_range["middle"][0] <= temp_distance <= sangvisFerris_data[aiInControl].effective_range["middle"][1]:
                        temp_area = "middle"
                    elif "near" in sangvisFerris_data[aiInControl].effective_range and sangvisFerris_data[aiInControl].effective_range["near"][0] <= temp_distance <= sangvisFerris_data[aiInControl].effective_range["near"][1]:
                        temp_area = "near"
                    if temp_area != None:
                        if (characters_data[character].x,characters_data[character].y) in the_route:
                            the_route.remove((characters_data[character].x,characters_data[character].y))
                        characters_can_be_attacked[character] = {"route":the_route,"area":temp_area}
        #如果存在可以在移动后攻击到的敌人
        if len(characters_can_be_attacked) >= 1:
            character_with_min_hp = None
            for key in characters_can_be_attacked:
                if character_with_min_hp == None or characters_data[key].current_hp < characters_data[character_with_min_hp].current_hp:
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
                    if len(sangvisFerris_data[aiInControl].patrol_path) == 0:
                        return {"action": "stay"}
                    #如果敌人有巡逻路线
                    else:
                        the_route = theMap.findPath(sangvisFerris_data[aiInControl],sangvisFerris_data[aiInControl].patrol_path[0],sangvisFerris_data,characters_data,max_moving_routes_for_attacking)
                        if len(the_route) > 0:
                            return {"action": "move","route":the_route}
                        else:
                            raise Exception('A sangvisFerri named '+aiInControl+' cannot find it path!')
                #如果上一个回合有敌人暴露
                else:
                    that_character = None
                    for each_chara in the_characters_detected_last_round:
                        if that_character== None:
                            that_character = each_chara
                        else:
                            if sangvisFerris_data[that_character].current_hp < sangvisFerris_data[that_character].current_hp:
                                that_character = that_character
                    targetPosTemp = (the_characters_detected_last_round[that_character][0],the_characters_detected_last_round[that_character][1])
                    the_route = theMap.findPath(sangvisFerris_data[aiInControl],targetPosTemp,sangvisFerris_data,characters_data,max_moving_routes_for_attacking,[that_character])
                    if len(the_route) > 0:
                        if (targetPosTemp) in the_route:
                            the_route.remove(targetPosTemp)
                        return {"action": "move","route":the_route}
                    else:
                        return {"action": "stay"}
                    
            #如果这一回合有敌人暴露
            else:
                targetPosTemp = (characters_data[characters_can_be_detect[0]].x,characters_data[characters_can_be_detect[0]].y)
                the_route = theMap.findPath(sangvisFerris_data[aiInControl],targetPosTemp,sangvisFerris_data,characters_data,max_moving_routes_for_attacking,[characters_can_be_detect[0]])
                if len(the_route) > 0:
                    if (targetPosTemp) in the_route:
                        the_route.remove(targetPosTemp)
                    return {"action": "move","route":the_route}
                else:
                    return {"action": "stay"}