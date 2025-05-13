import time

import pygame._sdl2
import random
import os
import sys
import threading
import ctypes
from tkinter import messagebox

import win32con
import win32gui
import win32api
import plyer
import pyautogui
import psutil

from filesPath import *
from const import *

pygame.init()
lastFocusTime = 0
focusFuncON = True

base_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.abspath(".")
get_file = lambda path: os.path.join(base_path, path)


def hide_console():
    whnd = ctypes.windll.kernel32.GetConsoleWindow()
    if whnd != 0:
        ctypes.windll.user32.ShowWindow(whnd, 0)


def toast(msg, time_out=0):
    def tempToast(msg, time_out):
        plyer.notification.notify(title="XiaoZhu", message=msg, app_icon=get_file(xiaoZhuIconPath), timeout=time_out)
    threading.Thread(target=tempToast, args=(msg, time_out)).start()


def getWindowInform(windowWidth=None, windowHeight=None):
    if (windowWidth is None) and (windowHeight is None):
        windowWidth = defaultWindowSize[0]
        windowHeight = defaultWindowSize[1]
    elif (windowWidth is None) and (windowHeight is not None):
        windowWidth = int((defaultWindowSize[0] / defaultWindowSize[1]) * windowHeight)
    elif (windowWidth is not None) and (windowHeight is None):
        windowHeight = int((defaultWindowSize[1] / defaultWindowSize[0]) * windowWidth)

    windowHead = (defaultWindowHead / defaultWindowSize[1]) * windowHeight

    return {
        "height":windowHeight,
        "width":windowWidth,
        "head":windowHead
    }


def moveWindow(hwnd, window_pos_x, window_pos_y, windowSize):
    # print(window_pos_x, window_pos_y)
    win32gui.MoveWindow(hwnd, window_pos_x, window_pos_y, windowSize[0], windowSize[1], True)


def minimize_window(hwnd):
    ctypes.windll.user32.ShowWindow(hwnd, 6)  # 6 是 SW_MINIMIZE 的值


def set_focus_to_window():
    global lastFocusTime, focusFuncON

    if time.time() - lastFocusTime < 0.6:
        focusFuncON = False

    if focusFuncON:
        lastFocusTime = time.time()
        pyautogui.click()
    else:
        if time.time() - lastFocusTime > 20:
            focusFuncON = True


class Game:
    def __init__(self, boom=None):
        if boom is None:
            self.Boom = random.randint(1, boomNum)
        else:
            self.Boom = boom

        self.clickSound = pygame.mixer.Sound(get_file(clickSoundPath))
        self.boomList = [(i + 1) for i in range(boomNum)]
        self.done = False
        self.boomY = 0

    def clickBoom(self, number):
        self.clickSound.play()

        # 削雷
        missing = []
        if number > self.Boom:
            for i in range(number, self.boomList[-1] + 1):
                missing.append(i)
        else:
            for i in range(self.boomList[0], number + 1):
                missing.append(i)
        for i in missing:
            self.boomList.remove(i)

        if self.Boom in missing:
            self.Boom = True
            return {"boom":True, "missing":missing}
        return {"boom":False, "missing":missing}

