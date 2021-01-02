# cython: language_level=3
from .battle import *

class mapCreator(BattleSystemInterface):
    def __init__(self,chapterType,chapterId,collection_name=None):
        BattleSystemInterface.__init__(self,chapterType,chapterId,collection_name)
        self.fileLocation = "Data/{0}/chapter{1}_map.yaml".format(self.chapterType,self.chapterId) if self.chapterType == "main_chapter" else "Data/{0}/{1}/chapter{2}_map.yaml".format(self.chapterType,self.collection_name,self.chapterId)
        display.set_caption("Girls frontline-Last Wish: MapCreator")
        unloadBackgroundMusic()
    def initialize(self,screen):
        #屏幕尺寸
        self.window_x,self.window_y = screen.get_size()
        self.decorations_setting = loadConfig("Data/decorations.yaml","decorations")
        #载入地图数据
        mapFileData = loadConfig(self.fileLocation)
        #初始化角色信息
        characterDataThread = initializeCharacterDataThread(mapFileData["character"],mapFileData["sangvisFerri"],"dev")
        #加载角色信息
        characterDataThread.start()
        characterDataThread.join()
        self.characters_data,self.sangvisFerris_data = characterDataThread.getResult()
        #加载所有角色的数据
        self.DATABASE = characterDataThread.DATABASE
        #初始化地图
        self.MAP = mapFileData["map"]
        if self.MAP == None or len(self.MAP) == 0:
            SnowEnvImg = ["TileSnow01","TileSnow01ToStone01","TileSnow01ToStone02","TileSnow02","TileSnow02ToStone01","TileSnow02ToStone02"]
            block_y = 50
            block_x = 50
            default_map = [[SnowEnvImg[randomInt(0,5)] for a in range(block_x)] for i in range(block_y)]
            mapFileData["map"] = default_map
            saveConfig(self.fileLocation,mapFileData)
        else:
            block_y = len(mapFileData["map"])
            block_x = len(mapFileData["map"][0])
        #加载地图
        self._create_map(mapFileData,False)
        del mapFileData
        #加载背景图片
        self.envImgDict={}
        for imgPath in glob.glob(r'Assets/image/environment/block/*.png'):
            img_name = imgPath.replace(".","").replace("Assets","").replace("block","").replace("image","").replace("environment","").replace("png","").replace("\\","").replace("/","")
            self.envImgDict[img_name] = loadImg(imgPath,int(self.MAP.block_width/3))
        #加载所有友方的角色的图片文件
        self.charactersImgDict={}
        for imgPath in glob.glob(r'Assets/image/character/*'):
            img_name = imgPath.replace(".","").replace("Assets","").replace("image","").replace("character","").replace("\\","").replace("/","")
            self.charactersImgDict[img_name] = loadImg(imgPath+"/wait/"+img_name+"_wait_0.png",self.MAP.block_width)
        #加载所有敌对角色的图片文件
        self.sangvisFerrisImgDict={}
        for imgPath in glob.glob(r'Assets/image/sangvisFerri/*'):
            img_name = imgPath.replace(".","").replace("Assets","").replace("image","").replace("sangvisFerri","").replace("\\","").replace("/","")
            self.sangvisFerrisImgDict[img_name] = loadImg(imgPath+"/wait/"+img_name+"_wait_0.png",self.MAP.block_width)
        #加载所有的装饰品
        self.decorationsImgDict = {}
        for imgPath in glob.glob(r'Assets/image/environment/decoration/*'):
            img_name = imgPath.replace(".png","").replace(".","").replace("Assets","").replace("image","").replace("environment","").replace("decoration","").replace("\\","").replace("/","")
            self.decorationsImgDict[img_name] = loadImg(imgPath,self.MAP.block_width/5)
        #绿色方块/方块标准
        self.greenBlock = loadImg("Assets/image/UI/range/green.png",int(self.MAP.block_width*0.8))
        self.greenBlock.set_alpha(150)
        self.redBlock = loadImg("Assets/image/UI/range/red.png",int(self.MAP.block_width*0.8))
        self.redBlock.set_alpha(150)
        self.deleteMode = False
        self.object_to_put_down = None
        #加载容器图片
        self.UIContainer = loadDynamicImage("Assets/image/UI/container.png",(0,self.window_y),(0,self.window_y*0.75),(0,self.window_y*0.25/10),int(self.window_x*0.8), int(self.window_y*0.25))
        self.UIContainerButton = loadImage("Assets/image/UI/container_button.png",(self.window_x*0.33,-self.window_y*0.05),int(self.window_x*0.14),int(self.window_y*0.06))
        widthTmp = int(self.window_x*0.2)
        self.UIContainerRight = loadDynamicImage("Assets/image/UI/container.png",(self.window_x*0.8+widthTmp,0),(self.window_x*0.8,0),(widthTmp/10,0),widthTmp,self.window_y)
        self.UIContainerRightButton = loadImage("Assets/image/UI/container_button.png",(-self.window_x*0.03,self.window_y*0.4),int(self.window_x*0.04),int(self.window_y*0.2))
        self.UIContainerRight.rotate(90)
        self.UIContainerRightButton.rotate(90)
        #UI按钮
        self.UIButton = {}
        UI_x = self.MAP.block_width*0.5
        UI_y = int(self.window_y*0.02)
        UI_height = int(self.MAP.block_width*0.3)
        self.UIButton["save"] = ButtonWithFadeInOut("Assets/image/UI/menu.png",get_lang("MapCreator","save"),"black",100,UI_x,UI_y,UI_height)
        UI_x += self.UIButton["save"].get_width()+UI_height
        self.UIButton["back"] = ButtonWithFadeInOut("Assets/image/UI/menu.png",get_lang("MapCreator","back"),"black",100,UI_x,UI_y,UI_height)
        UI_x += self.UIButton["back"].get_width()+UI_height
        self.UIButton["delete"] = ButtonWithFadeInOut("Assets/image/UI/menu.png",get_lang("MapCreator","delete"),"black",100,UI_x,UI_y,UI_height)
        UI_x += self.UIButton["delete"].get_width()+UI_height
        self.UIButton["reload"] = ButtonWithFadeInOut("Assets/image/UI/menu.png",get_lang("MapCreator","reload"),"black",100,UI_x,UI_y,UI_height)
        #数据控制器
        self.data_to_edit = None
        #其他函数
        self.UI_local_x = 0
        self.UI_local_y = 0
        self.isPlaying = True
        #读取地图原始文件
        self.originalData = loadConfig(self.fileLocation)
    def display(self,screen):
        #更新输入事件
        self._update_event()
        mouse_x,mouse_y = controller.get_pos()
        block_get_click = self.MAP.calBlockInMap(mouse_x,mouse_y)
        for event in self._get_event():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.object_to_put_down = None
                    self.data_to_edit = None
                    self.deleteMode = False
                self._check_key_down(event)
            elif event.type == pygame.KEYUP:
                self._check_key_up(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                #上下滚轮-放大和缩小地图
                if ifHover(self.UIContainerRight) and event.button == 4 and self.UI_local_y<0:
                    self.UI_local_y += self.window_y*0.1
                elif ifHover(self.UIContainerRight) and event.button == 5:
                    self.UI_local_y -= self.window_y*0.1
                elif ifHover(self.UIContainerRightButton,None,self.UIContainerRight.x):
                    self.UIContainerRight.switch()
                    self.UIContainerRightButton.flip(True,False)
                elif ifHover(self.UIContainerButton,None,0,self.UIContainer.y):
                    self.UIContainer.switch()
                    self.UIContainerButton.flip(False,True)
                elif ifHover(self.UIContainer):
                    #上下滚轮-放大和缩小地图
                    if event.button == 4 and self.UI_local_x<0:
                        self.UI_local_x += self.window_x*0.05
                    elif event.button == 5:
                        self.UI_local_x -= self.window_x*0.05
                elif self.deleteMode == True and block_get_click != None:
                    #查看当前位置是否有装饰物
                    decoration = self.MAP.find_decoration_on((block_get_click["x"],block_get_click["y"]))
                    #如果发现有冲突的装饰物
                    if decoration != None:
                        self.MAP.remove_decoration(decoration)
                    else:
                        any_chara_replace = None
                        for key,value in dicMerge(self.characters_data,self.sangvisFerris_data).items():
                            if value.x == block_get_click["x"] and value.y == block_get_click["y"]:
                                any_chara_replace = key
                                break
                        if any_chara_replace != None:
                            if any_chara_replace in self.characters_data:
                                self.characters_data.pop(any_chara_replace)
                                self.originalData["character"].pop(any_chara_replace)
                            elif any_chara_replace in self.sangvisFerris_data:
                                self.sangvisFerris_data.pop(any_chara_replace)
                                self.originalData["sangvisFerri"].pop(any_chara_replace)
                elif ifHover(self.UIButton["save"]) and self.object_to_put_down == None and self.deleteMode == False:
                    saveConfig(self.fileLocation,self.originalData)
                elif ifHover(self.UIButton["back"]) and self.object_to_put_down == None and self.deleteMode == False:
                    self.isPlaying = False
                    break
                elif ifHover(self.UIButton["delete"]) and self.object_to_put_down == None and self.deleteMode == False:
                    self.object_to_put_down = None
                    self.data_to_edit = None
                    self.deleteMode = True
                elif ifHover(self.UIButton["reload"]) and self.object_to_put_down == None and self.deleteMode == False:
                    tempLocal_x,tempLocal_y = self.MAP.getPos()
                    #读取地图数据
                    mapFileData = loadConfig(self.fileLocation)
                    #初始化角色信息
                    self.characters_data = {}
                    for each_character in mapFileData["character"]:
                        self.characters_data[each_character] = CharacterDataManager(mapFileData["character"][each_character],self.DATABASE[mapFileData["character"][each_character]["type"]],self.window_y,"dev")
                    self.sangvisFerris_data = {}
                    for each_character in mapFileData["sangvisFerri"]:
                        self.sangvisFerris_data[each_character] = SangvisFerriDataManager(mapFileData["sangvisFerri"][each_character],self.DATABASE[mapFileData["sangvisFerri"][each_character]["type"]],"dev")
                    #加载地图
                    self._create_map(mapFileData,False)
                    del mapFileData
                    self.MAP.setPos(tempLocal_x,tempLocal_y)
                    #读取地图
                    self.originalData = loadConfig(self.fileLocation)
                else:
                    if pygame.mouse.get_pressed()[0] and block_get_click != None:
                        if self.object_to_put_down != None:
                            if self.object_to_put_down["type"] == "block":
                                self.originalData["map"][block_get_click["y"]][block_get_click["x"]] = self.object_to_put_down["id"]
                                self.MAP.update_block(block_get_click,self.object_to_put_down["id"])
                            elif self.object_to_put_down["type"] == "decoration":
                                #查看当前位置是否有装饰物
                                decoration = self.MAP.find_decoration_on((block_get_click["x"],block_get_click["y"]))
                                #如果发现有冲突的装饰物
                                if decoration != None:
                                    self.MAP.remove_decoration(decoration)
                                decorationType = self.decorations_setting[self.object_to_put_down["id"]]
                                if decorationType not in self.originalData["decoration"]:
                                    self.originalData["decoration"][decorationType] = {}
                                the_id = 0
                                while self.object_to_put_down["id"]+"_"+str(the_id) in self.originalData["decoration"][decorationType]:
                                    the_id+=1
                                nameTemp = self.object_to_put_down["id"]+"_"+str(the_id)
                                self.originalData["decoration"][decorationType][nameTemp] = {"image": self.object_to_put_down["id"],"x": block_get_click["x"],"y": block_get_click["y"]}
                                self.MAP.load_decorations(self.originalData["decoration"])
                            elif self.object_to_put_down["type"] == "character" or self.object_to_put_down["type"] == "sangvisFerri":
                                any_chara_replace = None
                                for key,value in dicMerge(self.characters_data,self.sangvisFerris_data).items():
                                    if value.x == block_get_click["x"] and value.y == block_get_click["y"]:
                                        any_chara_replace = key
                                        break
                                if any_chara_replace != None:
                                    if any_chara_replace in self.characters_data:
                                        self.characters_data.pop(any_chara_replace)
                                        self.originalData["character"].pop(any_chara_replace)
                                    elif any_chara_replace in self.sangvisFerris_data:
                                        self.sangvisFerris_data.pop(any_chara_replace)
                                        self.originalData["sangvisFerri"].pop(any_chara_replace)
                                the_id = 0
                                if self.object_to_put_down["type"] == "character":
                                    while self.object_to_put_down["id"]+"_"+str(the_id) in self.characters_data:
                                        the_id+=1
                                    nameTemp = self.object_to_put_down["id"]+"_"+str(the_id)
                                    self.originalData["character"][nameTemp] = {
                                        "bullets_carried": 100,
                                        "type": self.object_to_put_down["id"],
                                        "x": block_get_click["x"],
                                        "y": block_get_click["y"]
                                    }
                                    self.characters_data[nameTemp] = CharacterDataManager(self.originalData["character"][nameTemp],self.DATABASE[self.originalData["character"][nameTemp]["type"]],self.window_y,"dev")
                                elif self.object_to_put_down["type"] == "sangvisFerri":
                                    while self.object_to_put_down["id"]+"_"+str(the_id) in self.sangvisFerris_data:
                                        the_id+=1
                                    nameTemp = self.object_to_put_down["id"]+"_"+str(the_id)
                                    self.originalData["sangvisFerri"][nameTemp] = {
                                        "type": self.object_to_put_down["id"],
                                        "x": block_get_click["x"],
                                        "y": block_get_click["y"]
                                    }
                                    self.sangvisFerris_data[nameTemp] = SangvisFerriDataManager(self.originalData["sangvisFerri"][nameTemp],self.DATABASE[self.originalData["sangvisFerri"][nameTemp]["type"]],"dev")
        #其他移动的检查
        self._check_right_click_move(mouse_x,mouse_y)
        self._check_jostick_events()

        #画出地图
        self._display_map(screen)

        if block_get_click != None and ifHover(self.UIContainerRight)==False and ifHover(self.UIContainer)==False:
            if self.deleteMode == True:
                xTemp,yTemp = self.MAP.calPosInMap(block_get_click["x"],block_get_click["y"])
                drawImg(self.redBlock,(xTemp+self.MAP.block_width*0.1,yTemp),screen)
            elif self.object_to_put_down != None:
                xTemp,yTemp = self.MAP.calPosInMap(block_get_click["x"],block_get_click["y"])
                drawImg(self.greenBlock,(xTemp+self.MAP.block_width*0.1,yTemp),screen)

        #角色动画
        for key in self.characters_data:
            self.characters_data[key].draw(screen,self.MAP)
            if self.object_to_put_down == None and pygame.mouse.get_pressed()[0] and self.characters_data[key].x == int(mouse_x/self.greenBlock.get_width()) and self.characters_data[key].y == int(mouse_y/self.greenBlock.get_height()):
                self.data_to_edit = self.characters_data[key]
        for key in self.sangvisFerris_data:
            self.sangvisFerris_data[key].draw(screen,self.MAP)
            if self.object_to_put_down == None and pygame.mouse.get_pressed()[0] and self.sangvisFerris_data[key].x == int(mouse_x/self.greenBlock.get_width()) and self.sangvisFerris_data[key].y == int(mouse_y/self.greenBlock.get_height()):
                self.data_to_edit = self.sangvisFerris_data[key]

        #展示设施
        self.MAP.display_decoration(screen,self.characters_data,self.sangvisFerris_data)

        #画出UI
        self.UIContainerButton.display(screen,0,self.UIContainer.y)
        self.UIContainer.draw(screen)
        self.UIContainerRightButton.display(screen,self.UIContainerRight.x)
        self.UIContainerRight.draw(screen)
        for Image in self.UIButton:
            ifHover(self.UIButton[Image])
            self.UIButton[Image].display(screen)

        #显示所有可放置的友方角色
        i=0
        for key in self.charactersImgDict:
            tempX = self.UIContainer.x+self.MAP.block_width*i*0.6+self.UI_local_x
            if 0 <= tempX <= self.UIContainer.width*0.9:
                tempY = self.UIContainer.y-self.MAP.block_width*0.25
                drawImg(self.charactersImgDict[key],(tempX,tempY),screen)
                if pygame.mouse.get_pressed()[0] and ifHover(self.charactersImgDict[key],(tempX,tempY)):
                    self.object_to_put_down = {"type":"character","id":key}
            elif tempX > self.UIContainer.width*0.9:
                break
            i+=1
        i=0
        #显示所有可放置的敌方角色
        for key in self.sangvisFerrisImgDict:
            tempX = self.UIContainer.x+self.MAP.block_width*i*0.6+self.UI_local_x
            if 0 <= tempX <= self.UIContainer.width*0.9:
                tempY = self.UIContainer.y+self.MAP.block_width*0.25
                drawImg(self.sangvisFerrisImgDict[key],(tempX,tempY),screen)
                if pygame.mouse.get_pressed()[0] and ifHover(self.sangvisFerrisImgDict[key],(tempX,tempY)):
                    self.object_to_put_down = {"type":"sangvisFerri","id":key}
            elif tempX > self.UIContainer.width*0.9:
                break
            i+=1
        
        #显示所有可放置的环境方块
        i=0
        for img_name in self.envImgDict:
            posY = self.UIContainerRight.y+self.MAP.block_width*5*int(i/4)+self.UI_local_y
            if self.window_y*0.05<posY<self.window_y*0.9:
                posX = self.UIContainerRight.x+self.MAP.block_width/6+self.MAP.block_width/2.3*(i%4)
                drawImg(self.envImgDict[img_name],(posX,posY),screen)
                if pygame.mouse.get_pressed()[0] and ifHover(self.envImgDict[img_name],(posX,posY)):
                    self.object_to_put_down = {"type":"block","id":img_name}
            i+=1
        for img_name in self.decorationsImgDict:
            posY = self.UIContainerRight.y+self.MAP.block_width*5*int(i/4)+self.UI_local_y
            if self.window_y*0.05<posY<self.window_y*0.9:
                posX = self.UIContainerRight.x+self.MAP.block_width/6+self.MAP.block_width/2.3*(i%4)
                drawImg(self.decorationsImgDict[img_name],(posX,posY),screen)
                if pygame.mouse.get_pressed()[0] and ifHover(self.decorationsImgDict[img_name],(posX,posY)):
                    self.object_to_put_down = {"type":"decoration","id":img_name}
            i+=1
        
        #跟随鼠标显示即将被放下的物品
        if self.object_to_put_down != None:
            if self.object_to_put_down["type"] == "block":
                drawImg(self.envImgDict[self.object_to_put_down["id"]],(mouse_x,mouse_y),screen)
            elif self.object_to_put_down["type"] == "decoration":
                drawImg(self.decorationsImgDict[self.object_to_put_down["id"]],(mouse_x,mouse_y),screen)
            elif self.object_to_put_down["type"] == "character":
                drawImg(self.charactersImgDict[self.object_to_put_down["id"]],(mouse_x-self.MAP.block_width/2,mouse_y-self.MAP.block_width/2.1),screen)
            elif self.object_to_put_down["type"] == "sangvisFerri":
                drawImg(self.sangvisFerrisImgDict[self.object_to_put_down["id"]],(mouse_x-self.MAP.block_width/2,mouse_y-self.MAP.block_width/2.1),screen)
        
        #显示即将被编辑的数据
        if self.data_to_edit != None:
            drawImg(fontRender("action points: "+str(self.data_to_edit.max_action_point),"black",15),(self.window_x*0.91,self.window_y*0.8),screen)
            drawImg(fontRender("attack range: "+str(self.data_to_edit.attack_range),"black",15),(self.window_x*0.91,self.window_y*0.8+20),screen)
            drawImg(fontRender("current bullets: "+str(self.data_to_edit.current_bullets),"black",15),(self.window_x*0.91,self.window_y*0.8+20*2),screen)
            drawImg(fontRender("magazine capacity: "+str(self.data_to_edit.magazine_capacity),"black",15),(self.window_x*0.91,self.window_y*0.8+20*3),screen)
            drawImg(fontRender("max hp: "+str(self.data_to_edit.max_hp),"black",15),(self.window_x*0.91,self.window_y*0.8+20*4),screen)
            drawImg(fontRender("effective range: "+str(self.data_to_edit.effective_range),"black",15),(self.window_x*0.91,self.window_y*0.8+20*5),screen)
            drawImg(fontRender("max damage: "+str(self.data_to_edit.max_damage),"black",15),(self.window_x*0.91,self.window_y*0.8+20*6),screen)
            drawImg(fontRender("min damage: "+str(self.data_to_edit.min_damage),"black",15),(self.window_x*0.91,self.window_y*0.8+20*7),screen)
            drawImg(fontRender("x: "+str(self.data_to_edit.x),"black",15),(self.window_x*0.91,self.window_y*0.8+20*8),screen)
            drawImg(fontRender("y: "+str(self.data_to_edit.y),"black",15),(self.window_x*0.91,self.window_y*0.8+20*9),screen)

        display.flip()