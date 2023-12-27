#### [English](https://github.com/LinpgFoundation/linpg/blob/master/README.md) | [简体中文](https://github.com/LinpgFoundation/linpg/blob/master/README_SimplifiedChinese.md) | 繁體中文

# :speech_balloon: 前言

###### *"c++是有史以來最偉大的語言，但這並不代表用c++寫遊戲是一件輕松而又有趣的事情，pygame也是如此。"*



# :sparkles: 關於Linpg引擎

![PyPI](https://img.shields.io/pypi/pyversions/linpg?style=for-the-badge&logo=pypi) ![PyPI](https://img.shields.io/pypi/v/linpg?style=for-the-badge&logo=pypi) ![PyPI](https://img.shields.io/pypi/dm/linpg?style=for-the-badge&logo=pypi)

Linpg引擎是Linpg基金會基於pygame庫自主研發的遊戲引擎，目的是為了規範化pygame遊戲的開發，使得遊戲代碼更加整潔，易讀，易擴展，易維護。

Linpg引擎的開發使用了模塊化的理念，並在底層實現了很多遊戲開發過程中常用到的功能。Linpg引擎一直保持著與pygame高度的兼容性，使得開發者可以很容易將現有的pygame項目遷移到Linpg引擎上，或者在自己的pygame項目中使用Linpg引擎提供的功能或者工具。

世上無完人，我們需要你的幫助讓Linpg引擎變得更好。歡迎任何能幫助我們改進Linpg引擎的開發者！

##### 加入我們的Discord: https://discord.gg/3wz6bs5jvu



# :crystal_ball:一些使用 Linpg 開發的遊戲

![](https://github.com/LinpgFoundation/A-story-of-us/raw/master/Assets/image/screenshot/dialog.png)

#### [A-story-of-us](https://github.com/LinpgFoundation/A-story-of-us), 一款僅包含約 100 行代碼的視覺小說遊戲。對於任何對 Linpg 感興趣的人來說，這都是一個很好的起點。

![](https://github.com/TigeiaWorkshop/GFL-LastWish/raw/master/Assets/image/screenshot/battle.png)

#### [GFL-Last Wish](https://github.com/TigeiaWorkshop/GFL-LastWish ), 一款回合製戰略遊戲，展示了 Linpg 引擎的一些先進功能和無限潛力。



# :hammer_and_wrench: 運行庫 

| 必需安裝 |
| :---------- |
| pygame-ce   |
| pyvns       |
| numpy       |
| PySimpleGUI |

| 建議安裝*          |
| ------------------ |
| pyyaml             |
| opencv             |
| speech_recognition |

\* 默認情況下將安裝所有這些庫，因為沒有這些庫就無法啟用某些常用功能。

##### 感謝這些第三方庫的開發者，他（她）們讓使用python開發遊戲不再遙遠。



# :computer: 安裝

### 推薦:

```
pip install linpg
```

我們還強烈建議您下載並使用 [A-story-of-us](https://github.com/LinpgFoundation/A-story-of-us) 作為你的初始模板。

### 從源代碼開始建設：

首先，克隆此 repo：

```
git clone https://github.com/LinpgFoundation/linpg
```

(可選）如果有興趣試用開發版本，可以嘗試`dev` 分支：

```
git checkout dev
```

如果尚未安裝 linpg-toolbox，請使用該命令進行安裝：

```
pip install --upgrade linpgtoolbox
```

運行 `builder.py`：

```
python builder.py
```

然後。。。沒有然後了。


# :world_map: 分支​

### master:

當前最新的穩定版本

### dev:

目前可以運行的最新版本，相對穩定，但可能包含未被發現的問題或未完善的功能。 僅推薦有經驗的開發人員使用。



# :books: 如何貢獻代碼

- 你應該fork "dev"分支作為作為你的起始點。如果"dev"分支不存在，則fork "master"分支。

- 所有PR應該請求合並到"dev"分支中。如果"dev"不存在，則應請求合並到"master"分支。

- 所有PR應該詳細地闡明其做出的改動。



# :construction: 歷代Linpg引擎的變化

| Linpg 1（過時，不再維護） | 狀態               |
| ------------------------- | ------------------ |
| 視覺小說系統的基本實現    | :white_check_mark: |
| 簡易的主菜單頁面          | :white_check_mark: |

------

|Linpg 2（過時，不再維護）|狀態|
| -------------------------------------- | ------------------ |
| 非hard coded，容易編輯的視覺小說系統   | :white_check_mark: |
| 更加動態化的主菜單頁面                 | :white_check_mark: |
| 戰鬥系統的基本實現                     | :white_check_mark: |
| 對視頻文件的支持                       | :white_check_mark: |
| 視覺小說系統保持55幀，戰鬥系統達到45幀 | :white_check_mark: |

------

|Linpg 3 （當前版本）|狀態|
| ------------------------------------ | ------------------ |
| 更加模塊化和美觀現代化的視覺小說系統 | :white_check_mark: |
| 選項菜單模塊                         | :white_check_mark: |
| 更加完善復雜的戰鬥系統               | :white_check_mark: |
| 可用的地圖編輯器                     | :white_check_mark: |
| 可用的對話編輯器                     | :white_check_mark: |
| 大部分功能能在接受正確的輸入後工作   | :hammer:         |
| 視覺小說系統和戰鬥系統達到144幀       | :white_check_mark: |
| 視頻能穩定地以60幀播放               | :white_check_mark: |
| 可用的pygame原生輸入框（僅支持英文） | :white_check_mark: |

------

|Linpg 4（未來-計劃中）|
| -------------------------------------------------------- |
| pyglet支持（兩個庫，一個標準）                           |
| 底層采用c++和cython結合的方式重寫以獲取更高效的性能      |
| 更好的選項菜單模塊                                       |
| 敵方AI系統將部分采用machine learning的意見               |
| 更加便捷美觀的地圖編輯器和對話編輯器                     |
| 更加易讀規範化的代碼                                     |
| 大部分功能能在接受錯誤的輸入後報錯並采取最合適的方案運行 |
| 戰鬥系統能有更多的玩法                                   |
| 輸入框支持中文，日文，以及更多                           |




# :memo: 版權說明

版權信息請查看**LICENSE**文件。