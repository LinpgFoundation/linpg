# cython: language_level=3
from .component import *

#角色立绘系统
class CharacterImageManager:
    def __init__(self):
        #用于存放立绘的字典
        self.__character_image:dict = {}
        #如果是开发模式，则在初始化时加载所有图片
        self.__characters_last_round:tuple = tuple()
        self.__last_round_image_alpha:int = 255
        self.__characters_this_round:tuple = tuple()
        self.__this_round_image_alpha:int = 0
        self.__darkness:int = 50
        self.__img_width:int = int(display.get_width()/2)
        try:
            self.__communication_surface_rect:Rect = Rect(int(self.__img_width*0.25),0,int(self.__img_width*0.5),int(self.__img_width*0.56))
            self.__communication = StaticImage(
                os.path.join(DIALOG_UI_PATH, "communication.png"),
                0, 0,
                self.__communication_surface_rect.width, self.__communication_surface_rect.height
                )
            self.__communication_dark = self.__communication.copy()
            self.__communication_dark.add_darkness(self.__darkness)
        except BaseException:
            self.__communication = None
            self.__communication_dark = None
        self.__CHARACTER_IMAGE_DATABASE:CharacterImageDatabase = CharacterImageDatabase()
        self.__move_x:int = 0
        self.dev_mode:bool = False
        self.character_get_click = None
        self.image_folder_path:str = os.path.join("Assets", "image", "npc")
    #确保角色存在
    def __ensure_the_existence_of(self, name:str) -> None:
        if name not in self.__character_image: self.__load_character(os.path.join(self.image_folder_path,name))
    #加载角色
    def __load_character(self, path:str) -> None:
        name = os.path.basename(path)
        self.__character_image[name] = {}
        self.__character_image[name]["normal"] = load_static_image(path,(0,0),self.__img_width,self.__img_width)
        #生成深色图片
        self.__character_image[name]["dark"] = self.__character_image[name]["normal"].copy()
        self.__character_image[name]["dark"].add_darkness(self.__darkness)
    #画出角色
    def __display_character(self, name:str, x:Union[int,float], y:Union[int,float], alpha:int, surface:ImageSurface) -> None:
        if alpha > 0:
            nameTemp = name.replace("<c>","").replace("<d>","")
            self.__ensure_the_existence_of(nameTemp)
            #加载npc的基础立绘
            img = self.__character_image[nameTemp]["dark"] if "<d>" in name else self.__character_image[nameTemp]["normal"]
            img.set_size(self.__img_width,self.__img_width)
            img.set_alpha(alpha)
            img.set_pos(x,y)
            if "<c>" in name:
                img.set_crop_rect(self.__communication_surface_rect)
                img.draw(surface)
                if "<d>" in name:
                    self.__communication_dark.set_pos(x+self.__communication_surface_rect.x,y+self.__communication_surface_rect.y)
                    self.__communication_dark.draw(surface)
                else:
                    self.__communication.set_pos(x+self.__communication_surface_rect.x,y+self.__communication_surface_rect.y)
                    self.__communication.draw(surface)
            else:
                img.set_crop_rect(None)
                img.draw(surface)
            #如果是开发模式
            if self.dev_mode is True and is_hover(img,(x,y)):
                img.draw_outline(surface)
                self.character_get_click = name
    def draw(self, surface:ImageSurface) -> None:
        window_x = surface.get_width()
        window_y = surface.get_height()
        npcImg_y = window_y-window_x/2
        #调整alpha值
        if self.__last_round_image_alpha > 0:
            self.__last_round_image_alpha -= 15
            x_moved_forNpcLastRound = self.__img_width/4-self.__img_width/4*self.__last_round_image_alpha/255
        else:
            x_moved_forNpcLastRound = 0
        if self.__this_round_image_alpha < 255:
            self.__this_round_image_alpha += 25
            x_moved_forNpcThisRound = self.__img_width/4*self.__this_round_image_alpha/255-self.__img_width/4
        else:
            x_moved_forNpcThisRound = 0
        #初始化被选择的角色名字
        self.character_get_click = None
        #画上上一幕的立绘
        if len(self.__characters_last_round) == 0:
            #前后都无立绘，那干嘛要显示东西
            if len(self.__characters_this_round) == 0:
                pass
            #新增中间那个立绘
            elif len(self.__characters_this_round) == 1:
                self.__display_character(self.__characters_this_round[0],window_x/4+x_moved_forNpcThisRound,npcImg_y,self.__this_round_image_alpha,surface)
            #同时新增左右两边的立绘
            elif len(self.__characters_this_round) == 2:
                self.__display_character(self.__characters_this_round[0],x_moved_forNpcThisRound,npcImg_y,self.__this_round_image_alpha,surface)
                self.__display_character(self.__characters_this_round[1],window_x/2+x_moved_forNpcThisRound,npcImg_y,self.__this_round_image_alpha,surface)
        elif len(self.__characters_last_round) == 1:
            #很快不再需要显示原来中间的立绘
            if len(self.__characters_this_round) == 0:
                self.__display_character(self.__characters_last_round[0],window_x/4+x_moved_forNpcLastRound,npcImg_y,self.__last_round_image_alpha,surface)
            #更换中间的立绘
            elif len(self.__characters_this_round) == 1:
                self.__display_character(self.__characters_last_round[0],window_x/4,npcImg_y,self.__last_round_image_alpha,surface)
                self.__display_character(self.__characters_this_round[0],window_x/4,npcImg_y,self.__this_round_image_alpha,surface)
            elif len(self.__characters_this_round) == 2:
                #如果之前的中间变成了现在的左边，则立绘应该先向左移动
                if self.__CHARACTER_IMAGE_DATABASE.is_the_same_character(self.__characters_last_round[0],self.__characters_this_round[0]):
                    if self.__move_x+window_x/4 > 0:
                        self.__move_x -= int(window_x/40)
                    #显示左边立绘
                    self.__display_character(self.__characters_last_round[0],self.__move_x+window_x/4,npcImg_y,self.__last_round_image_alpha,surface)
                    self.__display_character(self.__characters_this_round[0],self.__move_x+window_x/4,npcImg_y,self.__this_round_image_alpha,surface)
                    #显示右边立绘
                    self.__display_character(self.__characters_this_round[1],window_x/2,npcImg_y,self.__this_round_image_alpha,surface)
                #如果之前的中间变成了现在的右边，则立绘应该先向右移动 - checked
                elif self.__CHARACTER_IMAGE_DATABASE.is_the_same_character(self.__characters_last_round[0],self.__characters_this_round[1]):
                    if self.__move_x+window_x/4 < window_x/2:
                        self.__move_x += int(window_x/40)
                    #显示左边立绘
                    self.__display_character(self.__characters_this_round[0],0,npcImg_y,self.__this_round_image_alpha,surface)
                    #显示右边立绘
                    self.__display_character(self.__characters_last_round[0],self.__move_x+window_x/4,npcImg_y,self.__last_round_image_alpha,surface)
                    self.__display_character(self.__characters_this_round[1],self.__move_x+window_x/4,npcImg_y,self.__this_round_image_alpha,surface)
                #之前的中间和现在两边无任何关系，先隐藏之前的立绘，然后显示现在的立绘 - checked
                else:
                    if self.__last_round_image_alpha > 0:
                        self.__this_round_image_alpha -= 25
                        self.__display_character(self.__characters_last_round[0],window_x/4,npcImg_y,self.__last_round_image_alpha,surface)
                    else:
                        self.__display_character(self.__characters_this_round[0],0,npcImg_y,self.__this_round_image_alpha,surface)
                        self.__display_character(self.__characters_this_round[1],window_x/2,npcImg_y,self.__this_round_image_alpha,surface)
        elif len(self.__characters_last_round)==2:
            #隐藏之前的左右两边立绘
            if len(self.__characters_this_round) == 0:
                self.__display_character(self.__characters_last_round[0],x_moved_forNpcLastRound,npcImg_y,self.__last_round_image_alpha,surface)
                self.__display_character(self.__characters_last_round[1],window_x/2+x_moved_forNpcLastRound,npcImg_y,self.__last_round_image_alpha,surface)
            elif len(self.__characters_this_round) == 1:
                #如果之前的左边变成了现在的中间，则立绘应该先向右边移动
                if self.__CHARACTER_IMAGE_DATABASE.is_the_same_character(self.__characters_last_round[0],self.__characters_this_round[0]):
                    if self.__move_x < window_x/4:
                        self.__move_x += int(window_x/40)
                    #左边立绘向右移动
                    self.__display_character(self.__characters_last_round[0],self.__move_x,npcImg_y,self.__last_round_image_alpha,surface)
                    self.__display_character(self.__characters_this_round[0],self.__move_x,npcImg_y,self.__this_round_image_alpha,surface)
                    #右边立绘消失
                    self.__display_character(self.__characters_last_round[1],window_x/2,npcImg_y,self.__last_round_image_alpha,surface)
                #如果之前的右边变成了现在的中间，则立绘应该先向左边移动
                elif self.__CHARACTER_IMAGE_DATABASE.is_the_same_character(self.__characters_last_round[1],self.__characters_this_round[0]):
                    if self.__move_x+window_x/2 > window_x/4:
                        self.__move_x -= int(window_x/40)
                    #左边立绘消失
                    self.__display_character(self.__characters_last_round[0],0,npcImg_y,self.__last_round_image_alpha,surface)
                    #右边立绘向左移动
                    self.__display_character(self.__characters_last_round[1],self.__move_x+window_x/2,npcImg_y,self.__last_round_image_alpha,surface)
                    self.__display_character(self.__characters_this_round[0],self.__move_x+window_x/2,npcImg_y,self.__this_round_image_alpha,surface)
                else:
                    if self.__last_round_image_alpha > 0:
                        self.__this_round_image_alpha -= 25
                        self.__display_character(self.__characters_last_round[0],0,npcImg_y,self.__last_round_image_alpha,surface)
                        self.__display_character(self.__characters_last_round[1],window_x/2,npcImg_y,self.__last_round_image_alpha,surface)
                    else:
                        self.__display_character(self.__characters_this_round[0],window_x/4,npcImg_y,self.__this_round_image_alpha,surface)
            elif len(self.__characters_this_round) == 2:
                if self.__CHARACTER_IMAGE_DATABASE.is_the_same_character(self.__characters_last_round[0],self.__characters_this_round[1]) and\
                    self.__CHARACTER_IMAGE_DATABASE.is_the_same_character(self.__characters_last_round[1],self.__characters_this_round[0]):
                    if self.__move_x+window_x/2 > 0:
                        self.__move_x -= int(window_x/30)
                    #左边到右边去
                    self.__display_character(self.__characters_last_round[0],-self.__move_x,npcImg_y,self.__last_round_image_alpha,surface)
                    self.__display_character(self.__characters_this_round[1],-self.__move_x,npcImg_y,self.__this_round_image_alpha,surface)
                    #右边到左边去
                    self.__display_character(self.__characters_last_round[1],window_x/2+self.__move_x,npcImg_y,self.__last_round_image_alpha,surface)
                    self.__display_character(self.__characters_this_round[0],window_x/2+self.__move_x,npcImg_y,self.__this_round_image_alpha,surface)
                else:
                    self.__display_character(self.__characters_last_round[0],0,npcImg_y,self.__last_round_image_alpha,surface)
                    self.__display_character(self.__characters_last_round[1],window_x/2,npcImg_y,self.__last_round_image_alpha,surface)
                    self.__display_character(self.__characters_this_round[0],0,npcImg_y,self.__this_round_image_alpha,surface)
                    self.__display_character(self.__characters_this_round[1],window_x/2,npcImg_y,self.__this_round_image_alpha,surface)
    #更新立绘
    def update(self, characterNameList:Union[list,tuple,None]) -> None:
        self.__characters_last_round = self.__characters_this_round
        self.__characters_this_round = tuple(characterNameList) if characterNameList is not None else tuple()
        self.__last_round_image_alpha = 255
        self.__this_round_image_alpha = 5
        self.__move_x = 0

#立绘配置信息数据库
class CharacterImageDatabase:
    def __init__(self):
        self.__DATA_PATH:str = os.path.join("Data", "npcImageDatabase.yaml")
        self.__DATA:dict = {}
        try:
            self.__DATA = load_config(self.__DATA_PATH)
        except FileNotFoundError:
            self.__DATA = {}
            save_config(self.__DATA_PATH, self.__DATA)
            throw_exception("warning", "Cannot find 'npcImageDatabase.yaml' in 'Data' file, a new one is created.")
    def is_the_same_character(self, fileName1:str, fileName2:str) -> bool:
        fileName1 = fileName1.replace("<c>","").replace("<d>","")
        fileName2 = fileName2.replace("<c>","").replace("<d>","")
        for key in self.__DATA:
            if fileName1 in self.__DATA[key]:
                return fileName2 in self.__DATA[key]
            elif fileName2 in self.__DATA[key]:
                return fileName1 in self.__DATA[key]
        return False