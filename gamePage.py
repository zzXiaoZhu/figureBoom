import time

import pygame

from const import *
from functions import *
from filesPath import *

boomImage = pygame.transform.smoothscale(pygame.image.load(get_file(boomImagePath)), boomSize)
onceAgainButtonImage = pygame.image.load(get_file(onceAgainButtonPath))
choosePunishmentButtonImage = pygame.image.load(get_file(choosePunishmentButtonPath))
shareToFriendsButtonImage = pygame.image.load(get_file(shareToFriendsButtonPath))
numFont = pygame.font.Font(get_file(numFontPath), numFontSize)
resultNumFont = pygame.font.Font(get_file(resultNumFontPath), resultNumFontSize)
scroll_v = scroll_min_v
scroll_start_y = None
resultButtonClick = False


def gameRecovery():
    global game, displayBoomY, disappearBoom
    game = Game()
    disappearBoom = []
    displayBoomY = 0
    toast("雷是{}".format(game.Boom))


# 注意：此处mousePress只支持左键右键(mousePress = [MouseLeft, MouseRight])
def GAME_PAGE(width, height, mousePos, mousePress, event, timeDis):
    global displayBoomY, scroll_v, scroll_start_y, disappearBoom
    gameSurface = pygame.surface.Surface((defaultWindowSize[0], defaultWindowSize[1] - defaultWindowHead))
    gameSurface.blit(gamePageBackground, (0, 0))

    # 处理事件
    mouseClick = False
    scroll_y = 0
    for e in event:
        if e.type == pygame.MOUSEWHEEL:
            scroll_y = e.y
            if scroll_start_y is None:
                scroll_start_y = displayBoomY
        elif e.type == pygame.MOUSEBUTTONDOWN:
            if mousePos[1] > 0:
                mouseClick = True

    game.boomY += scroll_x * scroll_y

    # 限制滚动区间
    displayLineNum = boomNum // boomLine_num
    if (boomNum - boomLine_num * displayLineNum > 0):
        displayLineNum += 1

    if game.boomY > 0:
        game.boomY = 0
    elif game.boomY < -(displayLineNum * boomSize[1] - height + boomSize[1] * 1.2):
        game.boomY = -(displayLineNum * boomSize[1] - height + boomSize[1] * 1.2)

    # 及时更新方向
    if scroll_start_y == game.boomY:
        scroll_start_y = displayBoomY

    # 由加速度计算速度
    if abs(displayBoomY - game.boomY) < scroll_v * (timeDis / 1000):
        displayBoomY = game.boomY
        scroll_v = scroll_min_v
        scroll_start_y = None
    else:
        if (scroll_start_y is not None) and (abs(displayBoomY - game.boomY) / abs(scroll_start_y - game.boomY) < 0.5):
            scroll_v -= scroll_a * (timeDis / 1000)
            if scroll_min_v is not None:
                if scroll_v < scroll_min_v:
                    scroll_v = scroll_min_v
        else:
            scroll_v += scroll_a * (timeDis / 1000)
            if scroll_max_v is not None:
                if scroll_v > scroll_max_v:
                    scroll_v = scroll_max_v

    # 由速度计算位移
    if displayBoomY > game.boomY:
        displayBoomY -= scroll_v * (timeDis / 1000)
    elif displayBoomY < game.boomY:
        displayBoomY += scroll_v * (timeDis / 1000)

    # 显示雷\获取鼠标所在的雷
    boomDistanceX = (width - boomLeftMargin - boomRightMargin - boomSize[0] * boomLine_num) / (boomLine_num - 1)
    boomDistanceY = (height - boomSize[1] * boomRow_num) / (boomRow_num - 1)
    tempX = boomLeftMargin
    tempY = displayBoomY
    mouseOnBoom = None
    for i in range(1, boomNum + 1):
        # 显示常驻雷、计算鼠标所在雷
        if i in game.boomList:
            gameSurface.blit(boomImage, (tempX, tempY))
            tempNumText = numFont.render(str(i), True, numColor)
            gameSurface.blit(tempNumText, (tempX + boomImage.get_size()[0] / 2 - tempNumText.get_size()[0] * 0.6,
                                           tempY + boomImage.get_size()[1] / 2 - tempNumText.get_size()[1] * 0.4))
            if tempX < mousePos[0] < tempX + boomSize[0] and tempY < mousePos[1] < tempY + boomSize[1] and mousePos[1] > 0:
                mouseOnBoom = i
        else:
            for j in disappearBoom:
                if i == j['boomID']:
                    # 计算函数关系
                    temp = (time.time() - j['boomTime']) / boomAniTime
                    tempSize = (-2.3 * (temp ** 2)) + (1.3 * temp) + 1
                    if 0 < tempSize < 1:
                        tempSize = tempSize ** 2

                    if tempSize > 2:
                        sys.exit()

                    # Size为0不用画
                    if tempSize > 0:
                        # 创建雷的surface
                        tempBoomImage = pygame.surface.Surface(boomSize)
                        tempBoomImage.fill((0, 0, 0))
                        tempBoomImage.set_colorkey((0, 0, 0))
                        tempBoomImage.blit(boomImage, (0, 0))
                        tempNumText = numFont.render(str(i), True, numColor)
                        tempBoomImage.blit(tempNumText, (boomSize[0] / 2 - tempNumText.get_size()[0] * 0.6,
                                                         boomSize[1] / 2 - tempNumText.get_size()[1] * 0.4))
                        tempBoomImage = pygame.transform.scale(tempBoomImage, (boomSize[0] * tempSize, boomSize[1] * tempSize))
                        tempBoomImage.set_colorkey((0, 0, 0))

                        # 把雷显示出来
                        gameSurface.blit(tempBoomImage, (tempX + boomSize[0] / 2 - tempBoomImage.get_size()[0] / 2,
                                                         tempY + boomSize[1] / 2 - tempBoomImage.get_size()[0] / 2))

        # 计算新坐标
        tempX += boomSize[0] + boomDistanceX
        if tempX + boomSize[0] > width - boomRightMargin:
            tempX = boomLeftMargin
            tempY += boomSize[1] + boomDistanceY

    # 触发雷


    BOOM = False
    boomID = None
    if mouseOnBoom is not None:
        if mouseClick and mousePress[0]:
            result = game.clickBoom(mouseOnBoom)
            for i in result['missing']:
                disappearBoom.append({
                    "boomID":i,
                    "boomTime":time.time()
                })

            BOOM = result['boom']
            boomID = mouseOnBoom

        # 右键强制爆炸
        elif mouseClick and mousePress[1]:
            game.clickSound.play()
            BOOM = True
            boomID = mouseOnBoom

    return {
        "surface":pygame.transform.smoothscale(gameSurface, (width, height)),
        "boom":BOOM,
        "boomID":boomID
        }


# 注意：此处mousePress只支持左键右键(mousePress = [MouseLeft, MouseRight])
def Result_page(width, height, mousePos, mousePress, event, boomID):
    global resultButtonClick

    resultSurface = pygame.surface.Surface((defaultWindowSize[0], defaultWindowSize[1] - defaultWindowHead))
    resultSurface.blit(resultPageBackground, (0, 0))

    resultNumText = resultNumFont.render(str(boomID), True, resultNumFontColor)
    resultSurface.blit(resultNumText, (width / 2 - resultNumText.get_size()[0] / 2,
                                       (height - resultNumText.get_size()[1]) * 0.25))

    # 显示按钮
    resultSurface.blit(onceAgainButtonImage, (width / 2 - resultButtonSize[0] / 2,
                                              height - onceAgainButtonMargin_bottom - resultButtonSize[1]))
    resultSurface.blit(choosePunishmentButtonImage, (width / 2 - resultButtonSize[0] / 2,
                                              height - choosePunishmentButtonMargin_bottom - resultButtonSize[1]))
    resultSurface.blit(shareToFriendsButtonImage, (width / 2 - resultButtonSize[0] / 2,
                                              height - shareToFriendsButtonMargin_bottom - resultButtonSize[1]))

    # 按钮功能
    newGame = False
    if width / 2 - resultButtonSize[0] / 2 < mousePos[0] < width / 2 - resultButtonSize[0] / 2 + resultButtonSize[0] and mousePress[0]:
        if height - onceAgainButtonMargin_bottom - resultButtonSize[1] < mousePos[1] < height - onceAgainButtonMargin_bottom and not resultButtonClick:
            gameRecovery()
            newGame = True
            resultButtonClick = True
        elif height - choosePunishmentButtonMargin_bottom - resultButtonSize[1] < mousePos[1] < height - choosePunishmentButtonMargin_bottom and not resultButtonClick:
            toast("自罚三杯叭，你干了，我随意")
            resultButtonClick = True
        elif height - shareToFriendsButtonMargin_bottom - resultButtonSize[1] < mousePos[1] < height - shareToFriendsButtonMargin_bottom and not resultButtonClick:
            toast("诶呦，不是哥们儿？你分享啥啊？分享你咋输的嘛……")
            resultButtonClick = True
    else:
        resultButtonClick = False



    return {
        'surface':pygame.transform.smoothscale(resultSurface, (width, height)),
        'newGame':newGame
    }


gameRecovery()
