import pygame

from filesPath import *

pygame.init()

numFontPath = HeavyFontPath
resultNumFontPath = SemiboldFontPath

boomNum = 100

defaultWindowSize = (415, 780)
defaultWindowHead = 70

titleColor = (255, 255, 255)

headLineColor = (255, 255, 255)
headLineSize = 0


headButtonHeight = 40
headButtonWidth = 128
headSingleButtonWidth = 43
headButtonPosX = -138  # 右侧对齐 (非精确像素，是按照按钮大小相比的，按钮大小会被强制缩放到Head高度的一半)
headButtonPosY = -50  # 下侧对齐, 同上

boomLeftMargin = 25
boomRightMargin = 25
boomLine_num = 5
boomRow_num = 9.6
boomSize = [70, 70]
boomAniTime = 0.6

numColor = (255, 255, 255)
numFontSize = 18

gamePageBackground = pygame.surface.Surface(defaultWindowSize)
gamePageBackground.fill((14, 3, 18))
headBackground = gamePageBackground
resultPageBackground = pygame.surface.Surface(defaultWindowSize)
resultPageBackground.fill((23, 8, 9))

scroll_a = 3800
scroll_max_v = None
scroll_min_v = 300
scroll_x = 100

resultNumFontSize = 170
resultNumFontColor = (237, 201, 70)

onceAgainButtonMargin_bottom = 280
choosePunishmentButtonMargin_bottom = 210
shareToFriendsButtonMargin_bottom = 140
resultButtonSize = [210, 50]