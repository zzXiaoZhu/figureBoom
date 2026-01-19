import time
import math
import random
import os
import sys
import threading
import ctypes
from tkinter import messagebox

import pygame._sdl2
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
        # plyer.notification.notify(title="XiaoZhu", message=msg, app_icon=get_file(xiaoZhuIconPath), timeout=time_out)
        # messagebox.showinfo('XiaoZhu', msg)
        print(msg)
    threading.Thread(target=tempToast, args=(msg, time_out), daemon=True).start()


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


# 还要做动画哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈
def PageChangeAni(width, height, Surface_0, Surface_1, rate, reverse=False,
                  ani_type="slide", direction="right", easing="ease_in_out"):
    """
    支持多种动画效果和缓动函数的页面切换

    Args:
        width: 表面宽度
        height: 表面高度
        Surface_0: 背景表面
        Surface_1: 前景表面
        rate: 线性进度（0-1）
        reverse: 是否反向播放
        ani_type: "slide"滑动, "fade"淡入淡出, "push"推动, "zoom"缩放, "rotate"旋转
        direction: "right"从右侧, "left"从左侧, "top"从上侧, "bottom"从下侧
        easing: 缓动函数类型
            "linear": 线性
            "ease_in": 缓入（先慢后快）
            "ease_out": 缓出（先快后慢）
            "ease_in_out": 缓入缓出
            "bounce": 弹跳效果
            "elastic": 弹性效果
    """

    def apply_easing(t, easing_type="linear"):
        """
        应用缓动函数到线性进度t（0-1）
        返回应用缓动后的进度（0-1）
        """
        if easing_type == "linear":
            return t

        elif easing_type == "ease_in":
            # 二次缓入
            return t * t

        elif easing_type == "ease_out":
            # 二次缓出
            return t * (2 - t)

        elif easing_type == "ease_in_out":
            # 二次缓入缓出
            if t < 0.5:
                return 2 * t * t
            else:
                return -1 + (4 - 2 * t) * t

        elif easing_type == "ease_in_cubic":
            # 三次缓入
            return t * t * t

        elif easing_type == "ease_out_cubic":
            # 三次缓出
            t -= 1
            return t * t * t + 1

        elif easing_type == "bounce":
            # 弹跳效果
            if t < 1 / 2.75:
                return 7.5625 * t * t
            elif t < 2 / 2.75:
                t -= 1.5 / 2.75
                return 7.5625 * t * t + 0.75
            elif t < 2.5 / 2.75:
                t -= 2.25 / 2.75
                return 7.5625 * t * t + 0.9375
            else:
                t -= 2.625 / 2.75
                return 7.5625 * t * t + 0.984375

        elif easing_type == "elastic":
            # 弹性效果
            if t == 0 or t == 1:
                return t

            t -= 1
            return -math.pow(2, 10 * t) * math.sin((t - 0.075) * (2 * math.pi) / 0.3)

        elif easing_type == "back_in":
            # 回弹效果（缓入）
            s = 1.70158
            return t * t * ((s + 1) * t - s)

        elif easing_type == "back_out":
            # 回弹效果（缓出）
            s = 1.70158
            t -= 1
            return t * t * ((s + 1) * t + s) + 1

        elif easing_type == "circular_in":
            # 圆形缓入
            return 1 - math.sqrt(1 - t * t)

        elif easing_type == "circular_out":
            # 圆形缓出
            t -= 1
            return math.sqrt(1 - t * t)

        # 默认返回线性
        return t

    # 应用缓动函数
    eased_rate = apply_easing(rate, easing)

    # 根据reverse参数调整
    current_rate = 1 - eased_rate if reverse else eased_rate

    resultSurface = pygame.surface.Surface((width, height), pygame.SRCALPHA)

    if ani_type == "slide":
        # 滑动效果
        if direction == "right":
            x_offset = int(width * (1 - current_rate))
            y_offset = 0
        elif direction == "left":
            x_offset = int(-width * (1 - current_rate))
            y_offset = 0
        elif direction == "top":
            x_offset = 0
            y_offset = int(-height * (1 - current_rate))
        elif direction == "bottom":
            x_offset = 0
            y_offset = int(height * (1 - current_rate))

        resultSurface.blit(Surface_0, (0, 0))
        resultSurface.blit(Surface_1, (x_offset, y_offset))

    elif ani_type == "fade":
        # 淡入淡出效果
        resultSurface.blit(Surface_0, (0, 0))

        # 创建带有透明度的Surface_1副本
        fade_surface = Surface_1.copy()
        alpha = int(255 * current_rate)
        fade_surface.set_alpha(alpha)

        resultSurface.blit(fade_surface, (0, 0))

    elif ani_type == "push":
        # 推动效果（两个Surface同时移动）
        if direction == "right":
            offset_0 = int(-width * current_rate)  # Surface_0向左移出
            offset_1 = int(width * (1 - current_rate))  # Surface_1从右侧滑入
        elif direction == "left":
            offset_0 = int(width * current_rate)
            offset_1 = int(-width * (1 - current_rate))
        elif direction == "top":
            offset_0 = int(height * current_rate)
            offset_1 = int(-height * (1 - current_rate))
        elif direction == "bottom":
            offset_0 = int(-height * current_rate)
            offset_1 = int(height * (1 - current_rate))

        resultSurface.blit(Surface_0, (offset_0, 0))
        resultSurface.blit(Surface_1, (offset_1, 0))

    elif ani_type == "zoom":
        # 缩放效果
        resultSurface.blit(Surface_0, (0, 0))

        # 计算缩放比例和位置
        scale = 0.5 + current_rate * 0.5  # 从50%缩放到100%
        scaled_width = int(width * scale)
        scaled_height = int(height * scale)

        # 缩放Surface_1
        # 创建带有透明度的Surface_1副本
        fade_surface = Surface_1.copy()
        alpha = int(255 * current_rate)
        fade_surface.set_alpha(alpha)
        scaled_surface = pygame.transform.scale(fade_surface, (scaled_width, scaled_height))

        # 居中显示
        x_offset = (width - scaled_width) // 2
        y_offset = (height - scaled_height) // 2

        resultSurface.blit(scaled_surface, (x_offset, y_offset))

    elif ani_type == "rotate":
        # 旋转效果（从右侧旋转进入）
        resultSurface.blit(Surface_0, (0, 0))

        # 计算旋转角度（0-90度）
        angle = 90 * (1 - current_rate)

        # 旋转Surface_1
        rotated_surface = pygame.transform.rotate(Surface_1, angle)

        # 计算位置，使其从右侧旋转进入
        x_offset = width * (1 - current_rate)
        y_offset = (height - rotated_surface.get_height()) // 2

        resultSurface.blit(rotated_surface, (x_offset, y_offset))

    return resultSurface


def create_advanced_text_surface(text, font, color, size, bg_color=None, align='center',
                                 max_lines=None, ellipsis='...'):
    """
    高级文字渲染函数

    Args:
        text: 要显示的文字
        font: pygame.font.Font对象
        color: 文字颜色
        size: Surface尺寸 (width, height)
        bg_color: 背景颜色，None表示透明
        align: 对齐方式 'left', 'center', 'right'
        max_lines: 最大行数，超过显示省略号
        ellipsis: 省略号字符串

    Returns:
        pygame.Surface: 渲染好的Surface
    """
    width, height = size

    # 创建Surface
    if bg_color:
        if len(bg_color) == 4:
            surface = pygame.Surface((width, height), pygame.SRCALPHA)
            surface.fill(bg_color)
        else:
            surface = pygame.Surface((width, height))
            surface.fill(bg_color)
            surface = surface.convert_alpha()
    else:
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        surface.fill((0, 0, 0, 0))

    # 如果文本为空，直接返回
    if not text:
        return surface

    # 分割文本为单词
    words = text.split()
    lines = []
    current_line = []

    # 计算省略号宽度
    ellipsis_width = font.size(ellipsis)[0]
    available_width = width - 20  # 留出边距

    # 自动换行
    for word in words:
        # 测试当前行添加单词后的宽度
        test_line = ' '.join(current_line + [word])
        test_width = font.size(test_line)[0]

        if test_width <= available_width:
            current_line.append(word)
        else:
            # 如果当前行不为空，保存当前行
            if current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                # 单个单词就超过宽度，按字符拆分
                chars = list(word)
                current_word = ''

                for char in chars:
                    test_word = current_word + char
                    if font.size(test_word)[0] <= available_width:
                        current_word = test_word
                    else:
                        if current_word:
                            lines.append(current_word)
                            current_word = char
                        else:
                            # 单个字符就超过宽度，强制添加
                            lines.append(char)

                if current_word:
                    current_line = [current_word]

    # 添加最后一行
    if current_line:
        lines.append(' '.join(current_line))

    # 处理最大行数限制
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
        # 调整最后一行，确保有空间显示省略号
        last_line = lines[-1]
        while font.size(last_line + ellipsis)[0] > available_width and last_line:
            last_line = last_line[:-1]
        lines[-1] = last_line + ellipsis

    # 计算总高度
    line_height = font.get_linesize()
    total_height = len(lines) * line_height

    # 计算起始y坐标
    y_start = (height - total_height) // 2

    # 绘制每一行
    for i, line in enumerate(lines):
        text_surface = font.render(line, True, color)
        text_rect = text_surface.get_rect()

        # 设置y坐标
        text_rect.y = y_start + i * line_height

        # 设置x坐标根据对齐方式
        if align == 'left':
            text_rect.x = 10
        elif align == 'center':
            text_rect.centerx = width // 2
        elif align == 'right':
            text_rect.right = width - 10

        surface.blit(text_surface, text_rect)

    return surface


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

