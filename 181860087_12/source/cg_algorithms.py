#!/usr/bin/env python
# -*- coding:utf-8 -*-

# 本文件只允许依赖math库
import math


def draw_line(p_list, algorithm):
    """绘制线段

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'，此处的'Naive'仅作为示例，测试时不会出现
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    result = []
    if algorithm == 'Naive':
        if x0 == x1:
            for y in range(y0, y1 + 1):
                result.append((x0, y))
        else:
            if x0 > x1:
                x0, y0, x1, y1 = x1, y1, x0, y0
            k = (y1 - y0) / (x1 - x0)
            for x in range(x0, x1 + 1):
                result.append((x, int(y0 + k * (x - x0))))
    elif algorithm == 'DDA':
        x_, y_ = x1 - x0, y1 - y0
        length = max(abs(x_), abs(y_))
        if length == 0:
            result.append((x0, y0))
        else:
            dx, dy = x_ / length, y_ / length
            x, y = x0, y0
            i = 0
            while i <= length:
                result.append((int(x), int(y)))
                x += dx
                y += dy
                i += 1
    elif algorithm == 'Bresenham':
        x, y = x0, y0
        dx, dy = int(abs(x1 - x0)), int(abs(y1 - y0))
        if x1 - x0 > 0:
            sx = 1
        elif x1 - x0 < 0:
            sx = -1
        else:
            sx = 0
        if y1 - y0 > 0:
            sy = 1
        elif y1 - y0 < 0:
            sy = -1
        else:
            sy = 0
        flag = dy > dx
        if flag:
            dx, dy = dy, dx
        p = 2 * dy - dx
        for i in range(int(dx)):
            result.append((int(x), int(y)))
            if p > 0:
                if flag:
                    x += sx
                else:
                    y += sy
                p = p - 2 * dx
            if flag:
                y = y + sy
            else:
                x = x + sx
            p = p + 2 * dy
        result.append((int(x1), int(y1)))
    return result


def draw_polygon(p_list, algorithm):
    """绘制多边形

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 多边形的顶点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    result = []
    for i in range(len(p_list)):
        line = draw_line([p_list[i - 1], p_list[i]], algorithm)
        result += line
    return result


def draw_ellipse(p_list):
    """绘制椭圆（采用中点圆生成算法）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 椭圆的矩形包围框左上角和右下角顶点坐标
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    result = []
    tempx0, tempy0 = p_list[0]
    tempx1, tempy1 = p_list[1]
    x0 = min(tempx0, tempx1)
    y0 = max(tempy0, tempy1)
    x1 = max(tempx0, tempx1)
    y1 = min(tempy0, tempy1)
    if x0 == x1 and y0 == y1:
        result.append((x0, y0))
    elif y0 == y1:
        result = draw_line([[x0, y0], [x1, y1]], "DDA")
    else:
        rx, ry = abs(x1 - x0) / 2, abs(y1 - y0) / 2
        rx2, ry2 = rx * rx, ry * ry
        px, py = 0, ry
        p = ry2 - rx2 * ry + 0.25 * rx2
        tmp = [(px, py)]
        while 2 * ry2 * px < 2 * rx2 * py:
            if p >= 0:
                px += 1
                py -= 1
                p = p + 2 * ry2 * px - 2 * rx2 * py + ry2
            else:
                px += 1
                p = p + 2 * ry2 * px + ry2
            tmp.append((px, py))
        p = ry2 * (px + 0.5) * (px + 0.5) + rx2 * (py - 1) * (py - 1) - rx2 * ry2
        while True:
            if py <= 0:
                break
            if p <= 0:
                px += 1
                py -= 1
                p = p + 2 * ry2 * px - 2 * rx2 * py + rx2
            else:
                py -= 1
                p = p - 2 * rx2 * py + rx2
            tmp.append((px, py))
        cx, cy = x0 + rx, y0 - ry
        for i in range(len(tmp)):
            dx, dy = tmp[i]
            result.append((int(cx + dx), int(cy + dy)))
            result.append((int(cx + dx), int(cy - dy)))
            result.append((int(cx - dx), int(cy + dy)))
            result.append((int(cx - dx), int(cy - dy)))
    return result


def func1(arr, i, n, t):
    if abs(arr[i + 4 - n] - arr[i]) <= 1e-7:
        return 0
    else:
        return (t - arr[i]) / (arr[i + 4 - n] - arr[i])


def x_transverse(arr, p_list, i, n, t):
    x, y = p_list[i]
    if n == 0:
        return x
    else:
        lam = func1(arr, i, n, t)
        return lam * x_transverse(arr, p_list, i, n - 1, t) + (1 - lam) * x_transverse(arr, p_list, i - 1, n - 1, t)


def y_transverse(arr, p_list, i, n, t):
    x, y = p_list[i]
    if n == 0:
        return y
    else:
        lam = func1(arr, i, n, t)
        return lam * y_transverse(arr, p_list, i, n - 1, t) + (1 - lam) * y_transverse(arr, p_list, i - 1, n - 1, t)


def draw_curve(p_list, algorithm):
    """绘制曲线

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 曲线的控制点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'Bezier'和'B-spline'（三次均匀B样条曲线，曲线不必经过首末控制点）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    result = []
    if algorithm == "Bezier":
        n = len(p_list)
        x_arr, y_arr = [0 for i in range(n)], [0 for i in range(n)]
        x, y = p_list[0]
        tmp = []
        for a in range(0, 100 * n + 1, 1):
            step = (a / 100) / n
            for k in range(1, n, 1):
                for i in range(0, n - k, 1):
                    if k == 1:
                        x_arr[i] = p_list[i][0] * (1 - step) + p_list[i + 1][0] * step
                        y_arr[i] = p_list[i][1] * (1 - step) + p_list[i + 1][1] * step
                    else:
                        x_arr[i] = x_arr[i] * (1 - step) + x_arr[i + 1] * step
                        y_arr[i] = y_arr[i] * (1 - step) + y_arr[i + 1] * step
            tmp.append((x, y))
            x = x_arr[0]
            y = y_arr[0]
        for i in range(len(tmp) - 1):
            x0, y0 = tmp[i]
            x1, y1 = tmp[i + 1]
            result += draw_line([(x0, y0), (x1, y1)], "Bresenham")
    elif algorithm == "B-spline":
        n = len(p_list)
        k = 3
        tmp = []
        list_ = []
        for i in range(n + k + 2):
            tmp.append(i)
        step = 0.01
        for i in range(k, n, 1):
            a = tmp[i]
            while a <= tmp[i + 1]:
                x = x_transverse(tmp, p_list, i, k, a)
                y = y_transverse(tmp, p_list, i, k, a)
                # print(x, y)
                list_.append((x, y))
                a += step
        for i in range(len(list_) - 1):
            x0, y0 = list_[i]
            x1, y1 = list_[i + 1]
            result += draw_line([(x0, y0), (x1, y1)], "Bresenham")
    return result


def translate(p_list, dx, dy):
    """平移变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param dx: (int) 水平方向平移量
    :param dy: (int) 垂直方向平移量
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    result = []
    for tmp in p_list:
        x0, y0 = tmp[0], tmp[1]
        x_, y_ = x0 + dx, y0 + dy
        result.append((x_, y_))
    return result


def rotate(p_list, x, y, r):
    """旋转变换（除椭圆外）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 旋转中心x坐标
    :param y: (int) 旋转中心y坐标
    :param r: (int) 顺时针旋转角度（°）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    result = []
    rad = math.radians(r)
    cos = math.cos(rad)
    sin = math.sin(rad)
    for tmp in p_list:
        x0, y0 = tmp[0], tmp[1]
        x_, y_ = x + (x0 - x) * cos - (y0 - y) * sin, y + (x0 - x) * sin + (
                y0 - y) * cos
        result.append((x_, y_))
    return result


def scale(p_list, x, y, s):
    """缩放变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 缩放中心x坐标
    :param y: (int) 缩放中心y坐标
    :param s: (float) 缩放倍数
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    result = []
    for tmp in p_list:
        x0, y0 = tmp[0], tmp[1]
        x_, y_ = x + (x0 - x) * s, y + (y0 - y) * s
        result.append((x_, y_))
    return result


def encode(x, y, x_min, y_min, x_max, y_max):
    res = 0b0000
    inside, left, right, down, up = 0b0000, 0b0001, 0b0010, 0b0100, 0b1000
    if x < x_min:
        res |= left
    elif x > x_max:
        res |= right
    if y < y_min:
        res |= down
    elif y > y_max:
        res |= up
    return res


def clip(p_list, x_min, y_min, x_max, y_max, algorithm):
    """线段裁剪

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param x_min: 裁剪窗口左上角x坐标
    :param y_min: 裁剪窗口左上角y坐标
    :param x_max: 裁剪窗口右下角x坐标
    :param y_max: 裁剪窗口右下角y坐标
    :param algorithm: (string) 使用的裁剪算法，包括'Cohen-Sutherland'和'Liang-Barsky'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1]]) 裁剪后线段的起点和终点坐标
    """
    result = []
    if algorithm == "Cohen-Sutherland":
        # define code
        inside, left, right, down, up = 0b0000, 0b0001, 0b0010, 0b0100, 0b1000
        x0, y0 = p_list[0]
        x1, y1 = p_list[1]
        # print(x0, y0)
        # print(x1, y1)
        if x_min > x_max:
            x_min, x_max = x_max, x_min
        if y_min > y_max:
            y_min, y_max = y_max, y_min
        # print(x_min, y_min, x_max, y_max)
        c0 = encode(x0, y0, x_min, y_min, x_max, y_max)
        c1 = encode(x1, y1, x_min, y_min, x_max, y_max)
        while 1:
            # print(c0, c1)
            # p0, p1 all outside
            if bool(c0 & c1) == 1:
                flag = 1
                break
            elif bool(c0 | c1) == 0:
                flag = 0
                break
            else:
                x, y = 0, 0
                k0, k1 = (x1 - x0) / (y1 - y0), (y1 - y0) / (x1 - x0)
                if c0 == 0:
                    c = c1
                else:
                    c = c0
                if c & up:
                    y = y_max
                    x = x0 + k0 * (y - y0)
                elif c & down:
                    y = y_min
                    x = x0 + k0 * (y - y0)
                elif c & right:
                    x = x_max
                    y = y0 + k1 * (x - x0)
                elif c & left:
                    x = x_min
                    y = y0 + k1 * (x - x0)
                if c == c0:
                    x0, y0 = x, y
                    c0 = encode(x0, y0, x_min, y_min, x_max, y_max)
                else:
                    x1, y1 = x, y
                    c1 = encode(x1, y1, x_min, y_min, x_max, y_max)
        # print(flag)
        if flag:
            result = [(0, 0), (0, 0)]
        else:
            result = [(x0, y0), (x1, y1)]
    elif algorithm == "Liang-Barsky":
        x0, y0 = p_list[0]
        x1, y1 = p_list[1]
        delta_x, delta_y = x1 - x0, y1 - y0
        if x_min > x_max:
            x_min, x_max = x_max, x_min
        if y_min > y_max:
            y_min, y_max = y_max, y_min
        p = [0, -delta_x, delta_x, -delta_y, delta_y]
        q = [0, x0 - x_min, x_max - x0, y0 - y_min, y_max - y0]
        u1, u2 = 0, 1
        flag = 0
        for i in range(1, 5, 1):
            if p[i] < 0:
                u1 = max(u1, q[i] / p[i])
            elif p[i] > 0:
                u2 = min(u2, q[i] / p[i])
            elif p[i] == 0 and q[i] < 0:
                flag = 1
            if u1 > u2:
                flag = 1
        if flag:
            result = [(0, 0), (0, 0)]
        else:
            x0_ = x0 + u1 * delta_x
            x1_ = x0 + u2 * delta_x
            y0_ = y0 + u1 * delta_y
            y1_ = y0 + u2 * delta_y
            result = [(x0_, y0_), (x1_, y1_)]
    return result
