import sys
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


def gameRecovery(boom=None):
    global game, displayBoomY, disappearBoom
    game = Game(boom)
    disappearBoom = []
    displayBoomY = 0
    toast("雷是{}".format(game.Boom))


# 注意：此处mousePress只支持左键右键(mousePress = [MouseLeft, MouseRight])
def GAME_PAGE(width, height, mousePos, mousePress, event, timeDis, DONT_MOVE=False):
    global displayBoomY, scroll_v, scroll_start_y, disappearBoom
    gameSurface = pygame.surface.Surface((width, height))
    gameSurface.blit(gamePageBackground, (0, 0))

    # 计算雷的间距\行数
    boomDistanceX = (width - boomLeftMargin - boomRightMargin - boomSize[0] * boomLine_num) / (boomLine_num - 1)
    boomDistanceY = (height - boomSize[1] * boomRow_num) / (boomRow_num - 1)
    displayLineNum = boomNum // boomLine_num
    if (boomNum - boomLine_num * displayLineNum > 0):
        displayLineNum += 1

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

    # 如果不止一页就可以滑动
    if (boomSize[1] + boomDistanceY) * displayLineNum > height:
        game.boomY += scroll_x * scroll_y

        # 限制滚动区间
        if game.boomY > 0:
            game.boomY = 0
        elif game.boomY < -(displayLineNum * boomSize[1] + displayLineNum * boomDistanceY - height):
            game.boomY = -(displayLineNum * boomSize[1] + displayLineNum * boomDistanceY - height)

    # 及时更新方向
    if scroll_start_y == game.boomY:
        scroll_start_y = displayBoomY

    # 由加速度计算速度
    if abs(displayBoomY - game.boomY) < scroll_v * (timeDis / 1000):
        displayBoomY = game.boomY
        scroll_v = scroll_min_v
        scroll_start_y = None
    else:
        if (scroll_start_y is not None) and (abs(displayBoomY - game.boomY) / abs(scroll_start_y - game.boomY) < 0.1):
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
    tempX = boomLeftMargin
    tempY = displayBoomY
    tempLineNum = 0
    mouseOnBoom = None
    for i in range(1, boomNum + 1):
        # 不在屏幕内不渲染
        Display = True
        if tempX < 0 - boomSize[0] or tempX > width:
            Display = False
        if tempY < 0 - boomSize[1] or tempY > height:
            Display = False

        # 显示常驻雷、计算鼠标所在雷
        if Display:
            if i in game.boomList:
                gameSurface.blit(boomImage, (tempX, tempY))
                tempNumText = numFont.render(str(i), True, numColor)
                gameSurface.blit(tempNumText, (tempX + boomImage.get_size()[0] / 2 - tempNumText.get_size()[0] * 0.6,
                                               tempY + boomImage.get_size()[1] / 2 - tempNumText.get_size()[1] * 0.4))
                if tempX < mousePos[0] < tempX + boomSize[0] and tempY < mousePos[1] < tempY + boomSize[1] and mousePos[
                    1] > 0:
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
                            tempBoomImage = pygame.transform.scale(tempBoomImage,
                                                                   (boomSize[0] * tempSize, boomSize[1] * tempSize))
                            tempBoomImage.set_colorkey((0, 0, 0))

                            # 把雷显示出来
                            gameSurface.blit(tempBoomImage, (tempX + boomSize[0] / 2 - tempBoomImage.get_size()[0] / 2,
                                                             tempY + boomSize[1] / 2 - tempBoomImage.get_size()[0] / 2))

        # 计算新坐标
        tempLineNum += 1
        tempX += (width - boomLeftMargin - boomRightMargin) / boomLine_num
        if tempLineNum >= boomLine_num:
            tempLineNum = 0
            tempX = boomLeftMargin
            tempY += boomSize[1] + boomDistanceY

    # 触发雷
    if DONT_MOVE:
        mouseClick = False
    BOOM = False
    boomID = None
    if mouseOnBoom is not None:
        if mouseClick and mousePress[0]:
            result = game.clickBoom(mouseOnBoom)
            for i in result['missing']:
                disappearBoom.append({
                    "boomID": i,
                    "boomTime": time.time()
                })

            BOOM = result['boom']
            boomID = mouseOnBoom

        # 右键强制爆炸
        elif mouseClick and mousePress[1]:
            game.clickSound.play()
            BOOM = True
            boomID = mouseOnBoom

    return {
        "surface": pygame.transform.smoothscale(gameSurface, (width, height)),
        "boom": BOOM,
        "boomID": boomID
    }


# 注意：此处mousePress只支持左键右键(mousePress = [MouseLeft, MouseRight])
def Result_page(width, height, mousePos, mousePress, event, boomID, DONT_MOVE=False):
    global resultButtonClick

    # resultSurface = pygame.surface.Surface((defaultWindowSize[0], defaultWindowSize[1] - defaultWindowHead))
    resultSurface = pygame.surface.Surface((width, height))
    resultSurface.blit(resultPageBackground, (0, 0))

    resultNumText = resultNumFont.render(str(boomID), True, resultNumFontColor)
    resultSurface.blit(resultNumText, (width / 2 - resultNumText.get_size()[0] / 2,
                                       (height - resultNumText.get_size()[1]) * 0.25))

    # 显示按钮
    resultSurface.blit(onceAgainButtonImage, (width / 2 - resultButtonSize[0] / 2,
                                              height - onceAgainButtonMargin_bottom - resultButtonSize[1]))
    resultSurface.blit(choosePunishmentButtonImage, (width / 2 - resultButtonSize[0] / 2,
                                                     height - choosePunishmentButtonMargin_bottom - resultButtonSize[
                                                         1]))
    resultSurface.blit(shareToFriendsButtonImage, (width / 2 - resultButtonSize[0] / 2,
                                                   height - shareToFriendsButtonMargin_bottom - resultButtonSize[1]))

    # 按钮功能
    newGame = False
    punishment = False
    if not DONT_MOVE:
        if width / 2 - resultButtonSize[0] / 2 < mousePos[0] < width / 2 - resultButtonSize[0] / 2 + resultButtonSize[
            0] and mousePress[0]:
            if height - onceAgainButtonMargin_bottom - resultButtonSize[1] < mousePos[
                1] < height - onceAgainButtonMargin_bottom and not resultButtonClick:
                gameRecovery()
                newGame = True
                resultButtonClick = True
            elif height - choosePunishmentButtonMargin_bottom - resultButtonSize[1] < mousePos[
                1] < height - choosePunishmentButtonMargin_bottom and not resultButtonClick:
                punishment = True
                resultButtonClick = True
            elif height - shareToFriendsButtonMargin_bottom - resultButtonSize[1] < mousePos[
                1] < height - shareToFriendsButtonMargin_bottom and not resultButtonClick:
                toast("诶呦，不是哥们儿？你分享啥啊？分享你咋输的嘛……")
                resultButtonClick = True
        else:
            resultButtonClick = False

    return {
        'surface': pygame.transform.smoothscale(resultSurface, (width, height)),
        'newGame': newGame,
        'punishment': punishment
    }


# 我操啊用户怎么这么坏啊还要真的选惩罚
# 我不想做了呜呜呜呜呜呜呜呜呜呜呜呜呜
# 哇啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊
# 惩罚功能狗都不
# 做！做的就是惩罚功能！
# 我精神状态挺好的啊哈哈哈哈哈哈哈哈哈哈
# 我好状态挺神精的啊啊啊啊啊啊啊啊啊啊啊
punishmentPageTitle = pygame.image.load(get_file("files\\PunishmentPage\\title.png"))  # 标题
punishment_button_background = pygame.image.load(get_file("files\\PunishmentPage\\BTN_BG.png"))  # 按钮
punishment_button_hongBao = pygame.image.load(get_file("files\\PunishmentPage\\1.png"))
punishment_button_heJiu = pygame.image.load(get_file("files\\PunishmentPage\\2.png"))
punishment_button_zhenXinHua = pygame.image.load(get_file("files\\PunishmentPage\\3.png"))
punishment_button_daMaoXian = pygame.image.load(get_file("files\\PunishmentPage\\4.png"))
punishment_window = pygame.image.load(get_file("files\\PunishmentPage\\Window.png"))
punishment_windowCloseButton = pygame.image.load(get_file("files\\PunishmentPage\\closeButton.png"))

punishmentFont = pygame.font.Font(punishmentFontPath, punishmentFontSize)

showPunishmentWindow = False
showPunishmentTime = 0
punishmentPath = ''
punishmentContant = ''


def Punishment_page(width, height, mousePos, mousePress, event, background_Alpha, DONT_MOVE=False):
    global showPunishmentTime, showPunishmentWindow, punishmentPath

    def button(pos, mouse_pos, background: pygame.Surface, Contents, events: list,
               surface: pygame.Surface, dont_move, common=False):
        head_height = defaultWindowHead
        # 显示按钮
        surface.blit(background, pos)  # 背景
        if Contents is not None:
            contentPos = (pos[0] + (background.get_width() - Contents.get_width()) // 2,
                          pos[1] + (background.get_height() - Contents.get_height()) // 2)
            surface.blit(Contents, contentPos)  # 内容

        # 如果禁止交互
        if dont_move:
            return False

        # 定义碰撞区域
        if not common:
            # 固定尺寸
            left = pos[0] + 12
            top = pos[1] + 12
            width = 120
            height = 160
        else:
            # 通用模式
            left = pos[0]
            top = pos[1]
            width = background.get_width()
            height = background.get_height()

        # 检查事件
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # 左键
                # 将event.pos转换为与mouse_pos相同的坐标系（减去head高度）
                adjusted_pos = (event.pos[0], event.pos[1] - head_height)

                # 检查点击是否在碰撞区域内
                if (left <= adjusted_pos[0] <= left + width and
                        top <= adjusted_pos[1] <= top + height):
                    return True

        return False

    # 随机惩罚弹窗
    def punishmentWindow(rate):
        result_surface = punishment_window.copy()

        # 显示文字
        text = create_advanced_text_surface(punishmentContant, punishmentFont, punishmentFontColor, (215, 95))
        result_surface.blit(text, (40, 60))

        # _______动效_______
        y = -1.1 * (rate ** 2) + 1.6 * rate + 0.5

        tmpSurface = pygame.transform.rotate(result_surface, -(90 * (1 - y)))
        tmpSurface.set_alpha(255 * rate)

        sizeRate = 0.1 * (rate ** 2) + 0.2 * rate + 0.7
        size = (tmpSurface.get_size()[0] * sizeRate, tmpSurface.get_size()[1] * sizeRate)
        tmpSurface = pygame.transform.smoothscale(tmpSurface, size)
        # _________________

        return tmpSurface

    def getPunishment():
        """获取随机惩罚内容，带错误处理"""
        global punishmentContant

        try:
            # 读取文件
            with open(punishmentPath, 'r', encoding="UTF-8") as f:
                lines = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]

            # 检查是否有内容
            if not lines:
                error_msg = "惩罚文件为空"
                punishmentContant = error_msg
                toast(error_msg)
                return error_msg

            # 选择惩罚
            if len(lines) == 1:
                result = lines[0]
            else:
                available = [item for item in lines if item != punishmentContant]
                result = random.choice(available if available else lines)

            # 更新全局变量
            punishmentContant = result

            # 可选：显示成功提示
            # toast(f"惩罚已更新: {len(lines)}个可用选项")

            return result

        except FileNotFoundError:
            error_msg = "找不到惩罚文件"
        except PermissionError:
            error_msg = "无文件读取权限"
        except Exception as e:
            error_msg = f"读取错误: {str(e)}"

        # 错误处理
        punishmentContant = error_msg
        toast(error_msg)
        return error_msg

    resultSurface = pygame.surface.Surface((width, height))
    resultSurface.blit(punishmentPageBackground, (0, 0))

    # 显示标题
    resultSurface.blit(punishmentPageTitle, (80, 135))

    btn_hongBao = button((65, 175), mousePos, punishment_button_background, punishment_button_hongBao, event,
                         resultSurface, (DONT_MOVE or showPunishmentWindow))
    btn_heJiu = button((210, 175), mousePos, punishment_button_background, punishment_button_heJiu, event,
                       resultSurface, (DONT_MOVE or showPunishmentWindow))
    btn_zhenXinHua = button((65, 355), mousePos, punishment_button_background, punishment_button_zhenXinHua, event,
                            resultSurface, (DONT_MOVE or showPunishmentWindow))
    btn_daMaoXian = button((210, 355), mousePos, punishment_button_background, punishment_button_daMaoXian, event,
                           resultSurface, (DONT_MOVE or showPunishmentWindow))

    # 触发弹窗按钮
    if btn_hongBao:
        showPunishmentTime = time.time()
        showPunishmentWindow = True
        punishmentPath = get_file("files\\PunishmentPage\\punishments\\hong_bao.txt")
        getPunishment()
    elif btn_heJiu:
        showPunishmentTime = time.time()
        showPunishmentWindow = True
        punishmentPath = get_file("files\\PunishmentPage\\punishments\\he_jiu.txt")
        getPunishment()
    elif btn_zhenXinHua:
        showPunishmentTime = time.time()
        showPunishmentWindow = True
        punishmentPath = get_file("files\\PunishmentPage\\punishments\\zhen_xin_hua.txt")
        getPunishment()
    elif btn_daMaoXian:
        showPunishmentTime = time.time()
        showPunishmentWindow = True
        punishmentPath = get_file("files\\PunishmentPage\\punishments\\da_mao_xian.txt")
        getPunishment()

    # 弹窗
    if showPunishmentWindow:
        # 黑色遮罩
        t = pygame.surface.Surface(resultSurface.get_size())
        t.set_alpha(200)
        resultSurface.blit(t, (0, 0))

        # 弹窗
        rate = (time.time() - showPunishmentTime) / punishmentWindowANI_Time
        if rate > 1:
            rate = 1

        t = punishmentWindow(rate)
        windowPos = (width / 2 - t.get_width() / 2, height / 2 - t.get_height() / 2 - 30 + (50 * (1 - rate)))
        resultSurface.blit(t, windowPos)

        # 换一个按钮功能
        if rate >= 1:  # 动效播放完毕 可以响应
            left = 100 + windowPos[0]
            top = 155 + windowPos[1]
            width = 100
            height = 45

            for e in event:
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:  # 按下左键
                    adjusted_pos = (e.pos[0], e.pos[1] - defaultWindowHead)

                    # 检查是否在区域内
                    if left <= adjusted_pos[0] <= left + width and top <= adjusted_pos[1] <= top + height:
                        getPunishment()

        # 关闭按钮
        btn_Close = button((190, 480), mousePos, punishment_windowCloseButton, None, event, resultSurface, False, True)
        if btn_Close:
            showPunishmentWindow = False

    return {
        'surface': resultSurface
    }


gameRecovery()
