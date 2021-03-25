# cython: language_level=3
import time
from tkinter import Tk
from .ui import *

#输入框Interface，请勿实体化
class InputBoxInterface(GameObject2d):
    def __init__(self,x,y,font_size:int,txt_color,default_width) -> None:
        GameObject2d.__init__(self,x,y)
        self.FONTSIZE = font_size
        self.FONT = createFont(self.FONTSIZE)
        self.default_width = default_width
        self.deafult_height = self.FONTSIZE*1.5
        self.input_box = pygame.Rect(x, y, default_width, self.deafult_height)
        self.color = pygame.Color('lightskyblue3')
        self.txt_color = txt_color
        self.active = False
        self._text = None
        self._holder = self.FONT.render("|",get_fontMode(),self.txt_color)
        self.holderIndex = 0
        self.needSave = False
    def get_width(self) -> int: return self.input_box.w
    def get_height(self) -> int: return self.input_box.h
    def get_fontsize(self) -> int: return self.FONTSIZE
    def set_fontsize(self,font_size:int) -> None:
        self.FONTSIZE = int(font_size)
        self.FONT = createFont(self.FONTSIZE)
    def set_pos(self,x,y) -> None:
        super().set_pos(x,y)
        self.input_box = pygame.Rect(x, y, self.default_width, self.FONTSIZE*1.5)

#单行输入框
class SingleLineInputBox(InputBoxInterface):
    def __init__(self,x,y,font_size,txt_color,default_width=150) -> None:
        InputBoxInterface.__init__(self,x,y,font_size,txt_color,default_width)
        self._text = ""
    def get_text(self) -> str:
        self.needSave = False
        if self._text == "":
            return None
        else:
            return self._text
    def set_text(self,new_txt=None) -> None:
        if new_txt != None and len(new_txt)>0:
            self._text = new_txt
            self.holderIndex = len(new_txt)-1
        else:
            self._text = ""
            self.holderIndex = 0
        self._reset_inputbox_width()
    def _add_char(self,char) -> None:
        if len(char) > 0:
            self._text = self._text[:self.holderIndex]+char+self._text[self.holderIndex:]
            self.holderIndex += len(char)
            self._reset_inputbox_width()
        else:
            throwException("warning","The value of event.unicode is empty!")
    def _remove_char(self,action) -> None:
        if action == "ahead":
            if self.holderIndex > 0:
                self._text = self._text[:self.holderIndex-1]+self._text[self.holderIndex:]
                self.holderIndex -= 1
        elif action == "behind":
            if self.holderIndex < len(self._text):
                self._text = self._text[:self.holderIndex]+self._text[self.holderIndex+1:]
        else:
            throwException("error","Action has to be either 'ahead' or 'behind'!")
        self._reset_inputbox_width()
    def _reset_holderIndex(self,mouse_x) -> None:
        last_width = 0
        local_x = mouse_x-self.x
        new_width = 0
        i = 0
        for i in range(len(self._text)):
            new_width = self.FONT.size(self._text[:i])[0]+self.FONTSIZE*0.25
            if new_width>local_x:
                break
            else:
                last_width = new_width
        if (new_width-local_x) < (local_x-last_width):
            self.holderIndex = i
        else:
            self.holderIndex = i-1
    def _reset_inputbox_width(self)  -> None:
        if self._text != None and len(self._text)>0:
            self.input_box.w = max(self.default_width, self.FONT.size(self._text)[0]+self.FONTSIZE*0.6)
        else:
            self.input_box.w = self.default_width
    def _keyDownEvents(self,event) -> bool:
        if event.key == pygame.K_BACKSPACE:
            self._remove_char("ahead")
            return True
        elif event.key == pygame.K_DELETE:
            self._remove_char("behind")
            return True
        elif event.key == pygame.K_LEFT and self.holderIndex > 0:
            self.holderIndex -= 1
            return True
        elif event.key == pygame.K_RIGHT and self.holderIndex < len(self._text):
            self.holderIndex += 1
            return True
        elif event.key == pygame.K_LCTRL and pygame.key.get_pressed()[pygame.K_v]\
            or event.key == pygame.K_v and pygame.key.get_pressed()[pygame.K_LCTRL]:
            self._add_char(Tk().clipboard_get())
            return True
        return False
    def display(self,screen,pygame_events=pygame.event.get()) -> None:
        mouse_x,mouse_y = pygame.mouse.get_pos()
        for event in pygame_events:
            if self.active:
                if event.type == pygame.KEYDOWN:
                    if self._keyDownEvents(event):
                        pass
                    elif event.key == pygame.K_ESCAPE:
                        self.active = False
                        self.needSave = True
                    else:
                        self._add_char(event.unicode)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.x<=mouse_x<=self.x+self.input_box.w and self.y<=mouse_y<=self.y+self.input_box.h:
                        self._reset_holderIndex(mouse_x)
                    else:
                        self.active = False
                        self.needSave = True
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and 0<=mouse_x-self.x<=self.input_box.w and 0<=mouse_y-self.y<=self.input_box.h:
                self.active = True
                self._reset_holderIndex(mouse_x)
        # 画出文字
        if self._text != None and len(self._text) > 0:
            screen.blit(self.FONT.render(self._text,get_fontMode(),findColorRGBA(self.txt_color)), (self.x+self.FONTSIZE*0.25,self.y))
        #画出输入框
        if self.active:
            pygame.draw.rect(screen, self.color, self.input_box, 2)
            #画出 “|” 符号
            if int(time.time()%2)==0 or len(pygame_events)>0:
                screen.blit(self._holder, (self.x+self.FONTSIZE*0.25+self.FONT.size(self._text[:self.holderIndex])[0], self.y))

#多行输入框
class MultipleLinesInputBox(InputBoxInterface):
    def __init__(self,x,y,font_size,txt_color,default_width=150) -> None:
        InputBoxInterface.__init__(self,x,y,font_size,txt_color,default_width)
        self._text = [""]
        self.lineId = 0
    def get_text(self) -> list:
        self.needSave = False
        if len(self._text) == 0 or self._text == [""]:
            return None
        else:
            return self._text
    def set_text(self,new_txt=None) -> None:
        if new_txt == None or len(self._text) == 0:
            self._text = [""]
        elif isinstance(new_txt,list):
            self._text = new_txt
            self._reset_inputbox_size()
        else:
            throwException("error","The new_txt for MultipleLinesInputBox.set_text() must be a list!")
    def set_fontsize(self,font_size) -> None:
        super().set_fontsize(font_size)
        self._reset_inputbox_size()
    def _reset_inputbox_width(self) -> None:
        if self._text != None and len(self._text) > 0:
            width = self.default_width
            for txtTmp in self._text:
                new_width = self.FONT.size(txtTmp)[0]+self.FONTSIZE/2
                if new_width > width:
                    width = new_width
        else:
            width = self.default_width
        self.input_box.w = width
    def _reset_inputbox_height(self) -> None: self.input_box.h = self.deafult_height*len(self._text)
    def _reset_inputbox_size(self) -> None:
        self._reset_inputbox_width()
        self._reset_inputbox_height()
    def _add_char(self,char) -> None:
        if len(char) > 0:
            if "\n" not in char:
                self._text[self.lineId] = self._text[self.lineId][:self.holderIndex]+char+self._text[self.lineId][self.holderIndex:]
                self.holderIndex += len(char)
                self._reset_inputbox_width()
            else:
                theStringAfterHolderIndex = self._text[self.lineId][self.holderIndex:]
                self._text[self.lineId] = self._text[self.lineId][:self.holderIndex]
                for i in range(len(char)-1):
                    if char[i] != '\n':
                        self._text[self.lineId] += char[i]
                        self.holderIndex += 1
                    else:
                        self.lineId += 1
                        self._text.insert(self.lineId,"")
                        self.holderIndex = 0
                self._text[self.lineId] += theStringAfterHolderIndex
                self._reset_inputbox_size()
        else:
            throwException("warning","The value of event.unicode is empty!")
    #删除对应字符
    def _remove_char(self,action:str) -> None:
        if action == "ahead":
            if self.holderIndex > 0:
                self._text[self.lineId] = self._text[self.lineId][:self.holderIndex-1]+self._text[self.lineId][self.holderIndex:]
                self.holderIndex -= 1
            elif self.lineId > 0:
                #如果当前行有内容
                if len(self._text[self.lineId]) > 0:
                    self.holderIndex = len(self._text[self.lineId-1])
                    self._text[self.lineId-1] += self._text[self.lineId]
                    self._text.pop(self.lineId)
                    self.lineId -= 1
                else:
                    self._text.pop(self.lineId)
                    self.lineId -= 1
                    self.holderIndex = len(self._text[self.lineId])
        elif action == "behind":
            if self.holderIndex < len(self._text[self.lineId]):
                self._text[self.lineId] = self._text[self.lineId][:self.holderIndex]+self._text[self.lineId][self.holderIndex+1:]
            elif self.lineId < len(self._text)-1:
                #如果下一行有内容
                if len(self._text[self.lineId+1]) > 0:
                    self._text[self.lineId] += self._text[self.lineId+1]
                self._text.pop(self.lineId+1)
        else:
            throwException("error", "Action has to be either 'ahead' or 'behind'!")
        self._reset_inputbox_size()
    def _reset_holderIndex(self,mouse_x:int,mouse_y:int) -> None:
        self.lineId = round((mouse_y-self.y)/self.FONTSIZE)-1
        if self.lineId < 0:
            self.lineId = 0
        elif self.lineId >= len(self._text):
            self.lineId = len(self._text)-1
        last_width = 0
        local_x = mouse_x-self.x
        new_width = 0
        i = 0
        for i in range(len(self._text[self.lineId])):
            new_width = self.FONT.size(self._text[self.lineId][:i])[0]+self.FONTSIZE*0.25
            if new_width>local_x:
                break
            else:
                last_width = new_width
        if (new_width-local_x) < (local_x-last_width):
            self.holderIndex = i
        else:
            self.holderIndex = i-1
    def display(self,screen,pygame_events=pygame.event.get()) -> bool:
        mouse_x,mouse_y = pygame.mouse.get_pos()
        for event in pygame_events:
            if self.active:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        self._remove_char("ahead")
                    elif event.key == pygame.K_DELETE:
                        self._remove_char("behind")
                    elif event.key == pygame.K_LEFT and self.holderIndex > 0:
                        self.holderIndex -= 1
                    elif event.key == pygame.K_RIGHT and self.holderIndex < len(self._text[self.lineId]):
                        self.holderIndex += 1
                    elif event.key == pygame.K_UP and self.lineId>0:
                        self.lineId -= 1
                        if self.holderIndex > len(self._text[self.lineId])-1:
                            self.holderIndex = len(self._text[self.lineId])-1
                    elif event.key == pygame.K_DOWN and self.lineId<len(self._text)-1:
                        self.lineId += 1
                        if self.holderIndex > len(self._text[self.lineId])-1:
                            self.holderIndex = len(self._text[self.lineId])-1
                    elif event.key == pygame.K_LCTRL and pygame.key.get_pressed()[pygame.K_v] or event.key == pygame.K_v and pygame.key.get_pressed()[pygame.K_LCTRL]:
                        self._add_char(Tk().clipboard_get())
                        return True
                    #ESC，关闭
                    elif event.key == pygame.K_ESCAPE:
                        self.active = False
                        self.needSave = True
                    elif event.key == pygame.K_RETURN:
                        #如果“|”位于最后
                        if self.holderIndex == len(self._text[self.lineId]):
                            self._text.insert(self.lineId+1,"")
                        else:
                            self._text.insert(self.lineId+1,self._text[self.lineId][self.holderIndex:])
                            self._text[self.lineId] = self._text[self.lineId][:self.holderIndex]
                        self.lineId+=1
                        self.holderIndex=0
                        self._reset_inputbox_size()
                    else:
                        self._add_char(event.unicode)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.x<=mouse_x<=self.x+self.input_box.w and self.y<=mouse_y<=self.y+self.input_box.h:
                        self._reset_holderIndex(mouse_x,mouse_y)
                    else:
                        self.active = False
                        self.needSave = True
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.x<=mouse_x<=self.x+self.input_box.w and self.y<=mouse_y<=self.y+self.input_box.h:
                self.active = True
                self._reset_holderIndex(mouse_x,mouse_y)
        if self._text != None:
            for i in range(len(self._text)): 
                # 画出文字
                screen.blit(self.FONT.render(self._text[i],get_fontMode(),findColorRGBA(self.txt_color)),(self.x+self.FONTSIZE*0.25,self.y+i*self.deafult_height))
        if self.active:
            # 画出输入框
            pygame.draw.rect(screen, self.color, self.input_box, 2)
            #画出 “|” 符号
            if int(time.time()%2)==0 or len(pygame_events)>0:
                screen.blit(self._holder, (self.x+self.FONTSIZE*0.1+self.FONT.size(self._text[self.lineId][:self.holderIndex])[0], self.y+self.lineId*self.deafult_height))

#控制台
class Console(SingleLineInputBox):
    def __init__(self,x,y,font_size=32,default_width=150) -> None:
        self.color_inactive = pygame.Color('lightskyblue3')
        self.color_active = pygame.Color('dodgerblue2')
        SingleLineInputBox.__init__(self,x,y,font_size,self.color_active,default_width)
        self.color = self.color_active
        self.active = True
        self.hidden = True
        self.textHistory = []
        self.backwordID = 1
        self.events = {}
        if try_get_setting("DeveloperMode"): self.events["dev"] = True
        self.txtOutput = []
    def get_events(self,key=None):
        if key == None:
            return self.events
        elif key != None and key in self.events:
            return self.events[key]
        else:
            return None
    def _keyDownEvents(self,event) -> bool:
        if super()._keyDownEvents(event):
            return True
        #向上-过去历史
        elif event.key == pygame.K_UP and self.backwordID<len(self.textHistory):
            self.backwordID += 1
            self.set_text(self.textHistory[len(self.textHistory)-self.backwordID])
            return True
        #向下-过去历史，最近的一个
        elif event.key == pygame.K_DOWN and self.backwordID>1:
            self.backwordID -= 1
            self.set_text(self.textHistory[len(self.textHistory)-self.backwordID])
            return True
        #回车
        elif event.key == pygame.K_RETURN:
            if len(self._text)>0:
                if self._text[0]=="/":
                    if self._text == "/cheat on":
                        self.events["cheat"] = True
                        self.txtOutput.append("Cheat mode activated")
                    elif self._text == "/cheat off":
                        self.events["cheat"] = False
                        self.txtOutput.append("Cheat mode deactivated")
                    elif self._text[:5] == "/say ":
                        self.txtOutput.append(self._text[5:])
                    elif self._text == "/dev on":
                        self.txtOutput.append("Development mode activated")
                        self.events["dev"] = True
                    elif self._text == "/dev off":
                        self.txtOutput.append("Development mode deactivated")
                        self.events["dev"] = False
                    else:
                        self.txtOutput.append("Unknown command")
                else:
                    self.txtOutput.append(self._text)
                self.textHistory.append(self._text) 
                self.set_text()
                self.backwordID = 1
            else:
                throwException("warning","The input box is empty!")
            return True
        #ESC，关闭
        elif event.key == pygame.K_ESCAPE:
            self.active = False
            # Change the current color of the input box.
            self.color = self.color_active if self.active else self.color_inactive
            return True
        return False
    def display(self,screen,pygame_events=pygame.event.get()) -> None:
        if self.hidden == True:
            for event in pygame_events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_BACKQUOTE:
                    self.hidden = False
                    break
        elif self.hidden == False:
            for event in pygame_events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x,mouse_y = pygame.mouse.get_pos()
                    if self.x <= mouse_x <= self.x+self.input_box.w and self.y <= mouse_y <= self.y+self.input_box.h:
                        self.active = not self.active
                        # Change the current color of the input box.
                        self.color = self.color_active if self.active else self.color_inactive
                    else:
                        self.active = False
                        self.color = self.color_inactive
                elif event.type == pygame.KEYDOWN:
                    if self.active:
                        if self._keyDownEvents(event):
                            pass
                        else:
                            self._add_char(event.unicode)
                    else:
                        if event.key == pygame.K_BACKQUOTE or event.key == pygame.K_ESCAPE:
                            self.hidden = True
                            self.set_text()
            #画出输出信息
            for i in range(len(self.txtOutput)):
                screen.blit(self.FONT.render(self.txtOutput[i],get_fontMode(),self.color),(self.x+self.FONTSIZE*0.25, self.y-(len(self.txtOutput)-i)*self.FONTSIZE*1.5))
            # 画出文字
            if self._text != None and len(self._text) > 0:
                screen.blit(self.FONT.render(self._text,get_fontMode(),self.color),(self.x+self.FONTSIZE*0.25, self.y))
            #画出输入框
            pygame.draw.rect(screen, self.color, self.input_box, 2)
            #画出 “|” 符号
            if int(time.time()%2)==0 or len(pygame_events)>0:
                screen.blit(self._holder, (self.x+self.FONTSIZE*0.25+self.FONT.size(self._text[:self.holderIndex])[0], self.y))

#初始化控制台模块
console = Console(0,0)