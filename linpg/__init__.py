"""
def init():
    # 初始化pygame
    pygame.init()
    # 初始化
    Settings.reload()
    # 如果pygame的手柄组件没有初始化，则初始化
    if not pygame.joystick.get_init():
        pygame.joystick.init()
    # 初始化
    Languages.reload()
    # 初始化持久数据库
    PersistentVariables.reload()
"""
