import sys
import time

import pyautogui
import pygame.display

import gamePage
from functions import *

pygame.init()

pygame.display.set_icon(pygame.image.load(get_file(xiaoZhuPngPath)))
pygame.display.set_caption("谁喝酒道具")
Window = pygame.display.set_mode(defaultWindowSize, pygame.NOFRAME)
hwnd = pygame.display.get_wm_info()["window"]
windowInform = getWindowInform()


# 移动窗口方法
def checkWindowMoveEvent(pos):
    global moveWindowTemp, windowMoving
    if pos[1] <= windowInform['head'] and MouseLeft and headButtonPress == 0:
        windowMoving = True

    if windowMoving:
        if moveWindowTemp is None:
            moveWindowTemp = pos
        window_pos_x, window_pos_y = pyautogui.position()
        moveWindow(hwnd, window_pos_x - moveWindowTemp[0], window_pos_y - moveWindowTemp[1], Window.get_size())
        if not MouseLeft:
            windowMoving = False
    else:
        moveWindowTemp = None


MouseLeft = False
MouseRight = False
moveWindowTemp = None
windowMoving = False
headButtonPress = 0
headButtonFunc = 0

IN_GAME_PAGE = True
IN_RESULT_PAGE = False

titleFont = pygame.font.Font(get_file(thinFontPath), 15)
headButton = pygame.image.load(get_file(headButtonPath))

title = titleFont.render("数字炸弹", True, titleColor)

clock = pygame.time.Clock()
while True:
    timeDis = clock.tick(60)
    event = pygame.event.get()

    # 获取鼠标相关信息
    mousePos = pygame.mouse.get_pos()
    temp = pygame.mouse.get_pressed()
    if temp[0]:
        MouseLeft = True
    else:
        MouseLeft = False
    if temp[2]:
        MouseRight = True
    else:
        MouseRight = False
    del temp

    # 处理事件
    for e in event:
        if e.type == pygame.QUIT:
            sys.exit()

    # 鼠标移入进入游戏
    if (pygame.mouse.get_focused()) and (not pygame.key.get_focused()):
        set_focus_to_window()

    # 显示标题控件
    tempSurface = pygame.surface.Surface((windowInform["width"], windowInform["head"]))
    tempSurface.blit(headBackground, (0, 0))

    # 标题和按钮
    k = (windowInform['head'] * 0.5) / headButtonHeight
    tempHeadButton = pygame.transform.smoothscale(headButton, (k * headButtonWidth, k * headButtonHeight))
    tempSurface.blit(tempHeadButton,
                     (windowInform['width'] + headButtonPosX * k, windowInform["head"] + headButtonPosY * k))
    tempSurface.blit(title, (windowInform['width'] / 2 - title.get_size()[0] / 2,
                             windowInform['head'] - tempHeadButton.get_size()[1] / 2 - title.get_size()[1]))

    if (windowInform['width'] + headButtonPosX * k < mousePos[0] < windowInform['width'] + headButtonPosX * k +
        tempHeadButton.get_size()[0]) and \
            (windowInform["head"] + headButtonPosY * k < mousePos[1] < windowInform["head"] + headButtonPosY * k +
             tempHeadButton.get_size()[1]):
        buttonPosX = windowInform['width'] + headButtonPosX * k
        # 0未按下 1已按下等待动作 2动作完成
        if MouseLeft and headButtonPress == 0 and not windowMoving:
            headButtonPress = 1
            headButtonFunc = 0

        if headButtonPress == 1:
            if mousePos[0] < buttonPosX + tempHeadButton.get_size()[0] * (1 / 3):
                headButtonFunc = 1
            elif mousePos[0] < buttonPosX + tempHeadButton.get_size()[0] * (2 / 3):
                headButtonFunc = 2
            elif mousePos[0] < buttonPosX + tempHeadButton.get_size()[0]:
                headButtonFunc = 3

            headButtonPress = 2

        if not MouseLeft:
            headButtonPress = 0
            if headButtonFunc == 1:
                toast("分享个damn！是正经小程序嘛就分享？")
            elif headButtonFunc == 2:
                minimize_window(hwnd)
            elif headButtonFunc == 3:
                sys.exit()
            headButtonFunc = 0
    else:
        headButtonPress = 0
        headButtonFunc = 0

    # 标题底部分割线
    lineSurface = pygame.surface.Surface((windowInform['width'], headLineSize))
    lineSurface.fill(headLineColor)
    tempSurface.blit(lineSurface, (0, windowInform['head'] - headLineSize))

    # 移动窗口
    checkWindowMoveEvent(mousePos)

    Window.blit(tempSurface, (0, 0))

    if IN_GAME_PAGE:
        result = gamePage.GAME_PAGE(windowInform['width'], windowInform['height'] - windowInform['head'],
                                         (mousePos[0], mousePos[1] - windowInform['head']), [MouseLeft, MouseRight], event, timeDis)

        tempSurface = result["surface"]
        Window.blit(tempSurface, (0, windowInform['head']))
        if result['boom']:
            IN_GAME_PAGE = False
            IN_RESULT_PAGE = True
            boomID = result['boomID']
    elif IN_RESULT_PAGE:
        result = gamePage.Result_page(windowInform['width'], windowInform['height'] - windowInform['head'],
                                           (mousePos[0], mousePos[1] - windowInform['head']), [MouseLeft, MouseRight],
                                           event, boomID)

        tempSurface = result['surface']
        if result['newGame']:
            IN_GAME_PAGE = True
            IN_RESULT_PAGE = False

        Window.blit(tempSurface, (0, windowInform['head']))

    pygame.display.update()
