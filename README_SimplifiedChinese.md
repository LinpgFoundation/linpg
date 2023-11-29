#### [English](https://github.com/LinpgFoundation/linpg/blob/master/README.md) | 简体中文 | [繁體中文](https://github.com/LinpgFoundation/linpg/blob/master/README_TraditionalChinese.md)

# :speech_balloon: 前言

###### *"c++是有史以来最伟大的语言，但这并不代表用c++写游戏是一件轻松而又有趣的事情，pygame也是如此。"*



# :sparkles: 关于Linpg引擎

![PyPI](https://img.shields.io/pypi/pyversions/linpg?style=for-the-badge&logo=pypi) ![PyPI](https://img.shields.io/pypi/v/linpg?style=for-the-badge&logo=pypi) ![PyPI](https://img.shields.io/pypi/dm/linpg?style=for-the-badge&logo=pypi)

Linpg引擎是Linpg基金会基于pygame库自主研发的游戏引擎，目的是为了规范化pygame游戏的开发，使得游戏代码更加整洁，易读，易扩展，易维护。

Linpg引擎的开发使用了模块化的理念，并在底层实现了很多游戏开发过程中常用到的功能。Linpg引擎一直保持着与pygame高度的兼容性，使得开发者可以很容易将现有的pygame项目迁移到Linpg引擎上，或者在自己的pygame项目中使用Linpg引擎提供的功能或者工具。

世上无完人，我们需要你的帮助让Linpg引擎变得更好。欢迎任何能帮助我们改进Linpg引擎的开发者！

##### 加入我们的Discord: https://discord.gg/3wz6bs5jvu



# :crystal_ball:一些使用 Linpg 开发的游戏

![](https://github.com/LinpgFoundation/A-story-of-us/raw/master/Assets/image/screenshot/dialog.png)

#### [A-story-of-us](https://github.com/LinpgFoundation/A-story-of-us), 一款仅包含约 100 行代码的视觉小说游戏。对于任何对 Linpg 感兴趣的人来说，这都是一个很好的起点。

![](https://github.com/TigeiaWorkshop/GFL-LastWish/raw/master/Assets/image/screenshot/battle.png)

#### [GFL-Last Wish](https://github.com/TigeiaWorkshop/GFL-LastWish ), 一款回合制战略游戏，展示了 Linpg 引擎的一些先进功能和无限潜力。



# :hammer_and_wrench: 运行库 

| 必需安装 |
| :---------- |
| pygame-ce   |
| pyvns       |
| numpy       |
| PySimpleGUI |

| 建议安装*          |
| ------------------ |
| pyyaml             |
| opencv             |
| speech_recognition |

\* 默认情况下将安装所有这些库，因为没有这些库就无法启用某些常用功能。

##### 感谢这些第三方库的开发者，他（她）们让使用python开发游戏不再遥远。



# :computer: 安装

### 推荐:

```
pip install linpg
```

我们还强烈建议您下载并使用 [A-story-of-us](https://github.com/LinpgFoundation/A-story-of-us) 作为你的初始模板。

### 从源代码开始建设：

首先，克隆此 repo：

```
git clone https://github.com/LinpgFoundation/linpg
```

(可选）如果有兴趣试用最新版本，则应切换到 `dev` 分支：

```
git checkout dev
```

如果尚未安装 linpg-toolbox，请使用命令进行安装：

```
pip install --upgrade linpgtoolbox
```

运行 `builder.py`：

```
python builder.py
```

就这样，好好享受吧！


# :world_map: 分支​

### master:

该分支提供了当前的稳定版本

### dev:

目前可以运行的最新版本，相对稳定，但可能包含未被发现的问题或未完善的功能。 推荐有经验的开发人员使用。



# :books: 如何贡献代码

- 你应该fork "dev"分支作为作为你的起始点。如果"dev"分支不存在，则fork "master"分支。

- 所有PR应该请求merge到"dev"分支中。如果"dev"不存在，则请求merge到"master"分支。

- 所有PR应该详细地阐明其做出的改动。



# :construction: 历代Linpg引擎的变化

| Linpg 1（过时，不再维护） | 状态               |
| ------------------------- | ------------------ |
| 视觉小说系统的基本实现    | :white_check_mark: |
| 简易的主菜单页面          | :white_check_mark: |

------

|Linpg 2（过时，不再维护）|状态|
| -------------------------------------- | ------------------ |
| 非hard coded，容易编辑的视觉小说系统   | :white_check_mark: |
| 更加动态化的主菜单页面                 | :white_check_mark: |
| 战斗系统的基本实现                     | :white_check_mark: |
| 对视频文件的支持                       | :white_check_mark: |
| 视觉小说系统保持55帧，战斗系统达到45帧 | :white_check_mark: |

------

|Linpg 3 （当前版本）|状态|
| ------------------------------------ | ------------------ |
| 更加模块化和美观现代化的视觉小说系统 | :white_check_mark: |
| 选项菜单模块                         | :white_check_mark: |
| 更加完善复杂的战斗系统               | :white_check_mark: |
| 可用的地图编辑器                     | :white_check_mark: |
| 可用的对话编辑器                     | :white_check_mark: |
| 大部分功能能在接受正确的输入后工作   | :hammer:         |
| 视觉小说系统和战斗系统达到144帧       | :white_check_mark: |
| 视频能稳定地以60帧播放               | :white_check_mark: |
| 可用的pygame原生输入框（仅支持英文） | :white_check_mark: |

------

|Linpg 4（未来-计划中）|
| -------------------------------------------------------- |
| pyglet支持（两个库，一个标准）                           |
| 底层采用c++和cython结合的方式重写以获取更高效的性能      |
| 更好的选项菜单模块                                       |
| 敌方AI系统将部分采用machine learning的意见               |
| 更加便捷美观的地图编辑器和对话编辑器                     |
| 更加易读规范化的代码                                     |
| 大部分功能能在接受错误的输入后报错并采取最合适的方案运行 |
| 战斗系统能有更多的玩法                                   |
| 输入框支持中文，日文，以及更多                           |




# :memo: 版权说明

版权信息请查看**LICENSE**文件。