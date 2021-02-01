#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import time
import cg_algorithms as alg
import numpy as np
from typing import Optional
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    qApp,
    QGraphicsScene,
    QGraphicsView,
    QGraphicsItem,
    QListWidget,
    QHBoxLayout,
    QWidget,
    QStyleOptionGraphicsItem,
    QFileDialog,
    QSpinBox,
    QColorDialog,
    QToolBar,
    QLabel,
    QPushButton,
    QFrame,
    QAction,
    QInputDialog,
    QMessageBox,
    QSplashScreen,
    QDockWidget,
    QMenu,
    QToolButton,
    QGridLayout)
from PyQt5.QtGui import QPainter, QMouseEvent, QColor, QPen, QPixmap, QPalette, QIcon, QWheelEvent, QFont, QKeyEvent, \
    QCloseEvent
from PyQt5.QtCore import QRectF
from PyQt5.QtCore import *


def get_angle(x0, y0, x1, y1, x2, y2):
    a1 = np.array([x0 - x1, y0 - y1])
    a2 = np.array([x2 - x1, y2 - y1])
    cos = a1.dot(a2) / (np.sqrt(a1.dot(a1)) * np.sqrt(a2.dot(a2)))
    r = np.degrees(np.arccos(cos))
    # print(r)
    return -r


def get_point(item):
    tmp_list = item.p_list
    x_l, y_l = [], []
    for tmp in tmp_list:
        x_l.append(tmp[0])
        y_l.append(tmp[1])
    x, y = min(x_l), min(y_l)
    w, h = max(x_l) - x, max(y_l) - y
    return [x + w / 2, y + h / 2]


def get_scale(x0, y0, x1, y1, x2, y2):
    a1 = np.array([x0 - x1, y0 - y1])
    a2 = np.array([x0 - x2, y0 - y2])
    s = float(np.sqrt(a2.dot(a2)) / np.sqrt(a1.dot(a1)))
    return s


class MyCanvas(QGraphicsView):
    """
    画布窗体类，继承自QGraphicsView，采用QGraphicsView、QGraphicsScene、QGraphicsItem的绘图框架
    """

    def __init__(self, *args):
        super().__init__(*args)
        self.main_window = None
        self.list_widget = None
        self.item_dict = {}
        self.selected_id = ''

        self.status = ''
        self.temp_algorithm = ''
        self.temp_id = ''
        self.temp_item = None

        self.pen_color = Qt.black
        self.pen_width = 2

        self.x_center = 0
        self.y_center = 0
        self.x_old = 0
        self.y_old = 0
        self.current_id = 0

        self.draw_item = None
        self.changed_point_id = -1
        self.flag = 0
        self.mode = 0

    def start_draw_line(self, algorithm, item_id):
        self.finish_draw(1)
        self.status = 'line'
        self.temp_algorithm = algorithm
        self.temp_id = item_id

    # with bug line 195 and line 305
    # debug
    def start_draw_polygon(self, algorithm, item_id):
        self.finish_draw(1)
        self.status = 'polygon'
        self.temp_algorithm = algorithm
        self.temp_id = item_id

    def start_draw_ellipse(self, item_id):
        self.finish_draw(1)
        self.status = 'ellipse'
        self.temp_id = item_id

    def start_draw_curve(self, algorithm, item_id):
        self.finish_draw(1)
        self.status = 'curve'
        self.temp_algorithm = algorithm
        self.temp_id = item_id

    def start_translate(self):
        self.finish_draw(1)
        self.status = 'translate'
        self.setCursor(Qt.SizeAllCursor)
        self.temp_id = self.selected_id

    def start_rotate_a(self):
        self.finish_draw(1)
        self.status = 'rotate_a'
        self.temp_id = self.selected_id

    def start_rotate_b(self):
        self.finish_draw(1)
        self.status = 'rotate_b'
        self.temp_id = self.selected_id
        self.mode = 0

    def start_scale_a(self):
        self.finish_draw(1)
        self.status = 'scale_a'
        self.setCursor(Qt.SizeFDiagCursor)
        self.temp_id = self.selected_id

    def start_scale_b(self):
        self.finish_draw(1)
        self.status = 'scale_b'
        self.temp_id = self.selected_id
        self.mode = 0

    def start_clip(self, algorithm):
        self.finish_draw(1)
        self.status = 'clip'
        self.temp_algorithm = algorithm
        self.temp_id = self.selected_id

    def select_primitive(self):
        if (self.status == 'ellipse' or self.status == 'curve' or self.status == 'polygon') \
                and self.temp_item is not None:
            self.item_dict[self.temp_id] = self.temp_item
            self.list_widget.addItem(self.temp_id)
        self.status = "selection"
        self.finish_draw()

    def change_xy(self):
        self.finish_draw(1)
        self.status = "change"
        self.temp_id = self.selected_id

    def finish_draw(self, flag: int = 0):
        if (self.status == 'line' or self.status == 'ellipse' or self.status == 'polygon' or self.status == 'curve') \
                and self.temp_item is not None:
            self.item_dict[self.temp_id] = self.temp_item
            self.list_widget.addItem(self.temp_id)
        if self.status == 'translate' \
                or self.status == 'rotate_a' \
                or self.status == 'rotate_b' \
                or self.status == 'scale_a' \
                or self.status == 'scale_b' \
                or self.status == 'clip' \
                or self.status == 'change' \
                or self.status == 'selection' \
                or flag == 1:
            self.temp_id = self.selected_id
        else:
            if self.temp_item is not None:
                self.temp_id = self.main_window.add_id()
        self.temp_item = None
        self.updateScene([self.sceneRect()])
        if (self.status != 'translate' and self.status != 'scale_a') or flag == 1:
            self.setCursor(Qt.ArrowCursor)

    def clear_selection(self):
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.selected_id = ''

    def selection_changed(self, selected):
        if selected == -1:
            return
        if self.temp_item is not None:
            self.finish_draw()
        self.main_window.statusBar().showMessage('图元选择： %s' % selected)
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.item_dict[self.selected_id].update()
        self.selected_id = selected
        self.item_dict[selected].selected = True
        self.item_dict[selected].update()
        self.status = ''
        self.updateScene([self.sceneRect()])

    def mousePressEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line' or self.status == 'ellipse':
            self.temp_item = MyItem(self.temp_id,
                                    self.status,
                                    [[x, y], [x, y]],
                                    self.pen_color,
                                    self.pen_width,
                                    self.temp_algorithm)
            self.scene().addItem(self.temp_item)
        if self.status == 'polygon' or self.status == 'curve':
            if self.temp_item is None:
                self.temp_item = MyItem(self.temp_id,
                                        self.status,
                                        [[x, y], [x, y]],
                                        self.pen_color,
                                        self.pen_width,
                                        self.temp_algorithm)
                self.scene().addItem(self.temp_item)
            else:
                if event.button() != Qt.RightButton:
                    if self.check_polygon(x, y):
                        if self.flag == 1:
                            self.temp_item.p_list.append((x, y))
                        else:
                            self.temp_item.p_list[1] = (x, y)
                            self.flag = 1
                    else:
                        self.finish_draw()
                        self.flag = 0
                        self.temp_item = None
                else:
                    self.finish_draw()
                    self.flag = 0
                    self.temp_item = None
        if self.status == 'translate' or self.status == 'rotate_a' or self.status == 'scale_a':
            if self.temp_id not in self.item_dict:
                self.status = ''
            elif self.temp_item is None:
                self.temp_item = self.item_dict[self.temp_id]
                self.x_center, self.y_center = get_point(self.temp_item)
                self.x_old, self.y_old = x, y
        if self.status == 'clip':
            if self.temp_id not in self.item_dict:
                self.status = ''
            elif self.temp_item is None:
                self.temp_item = self.item_dict[self.temp_id]
                self.x_old, self.y_old = x, y
                self.draw_item = MyItem('-1',
                                        'rectangle',
                                        [[x, y], [x, y]],
                                        Qt.green,
                                        1,
                                        self.temp_algorithm)
                self.scene().addItem(self.draw_item)
        if self.status == 'selection':
            tmp = self.itemAt(x, y)
            select = -1
            for i, item in self.item_dict.items():
                if item == tmp:
                    select = i
            self.current_id = select
        if self.status == 'rotate_b' or self.status == 'scale_b':
            self.x_center, self.y_center = x, y
            self.mode = 1
        if self.status == 'change':
            if self.temp_id not in self.item_dict:
                self.status = ''
            elif self.temp_item is None:
                self.temp_item = self.item_dict[self.temp_id]
            i = 0
            if self.temp_item is not None:
                for tmp in self.temp_item.p_list:
                    x0, y0 = tmp[0], tmp[1]
                    dis = np.sqrt(np.power(x - x0, 2) + np.power(y - y0, 2))
                    if dis <= 4:
                        # print(dis, i)
                        self.changed_point_id = i
                        break
                    i += 1
                if i == len(self.temp_item.p_list):
                    self.changed_point_id = -1
        self.updateScene([self.sceneRect()])
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line' or self.status == 'ellipse':
            if self.temp_item is not None:
                self.temp_item.p_list[1] = [x, y]
        if self.status == 'polygon' or self.status == 'curve':
            if self.temp_item is not None:
                self.temp_item.p_list[len(self.temp_item.p_list) - 1] = [x, y]
        if self.status == 'translate':
            self.temp_item.translate(x - self.x_center, y - self.y_center)
            self.x_center, self.y_center = get_point(self.temp_item)
        if self.status == 'rotate_a':
            r = get_angle(self.x_old, self.y_old, self.x_center, self.y_center, x, y)
            self.temp_item.rotate(self.x_center, self.y_center, r)
            self.x_center, self.y_center = get_point(self.temp_item)
            self.x_old, self.y_old = x, y
        if self.status == 'scale_a':
            s = get_scale(self.x_center, self.y_center, self.x_old, self.y_old, x, y)
            self.temp_item.scale_(self.x_center, self.y_center, s)
            self.x_old, self.y_old = x, y
        if self.status == 'clip':
            x_, y_ = self.x_old, self.y_old
            x_min, y_min = min(x, x_), min(y, y_)
            x_max, y_max = max(x, x_), max(y, y_)
            self.draw_item.p_list[0] = (x_min, y_min)
            self.draw_item.p_list[1] = (x_max, y_max)
        if self.status == 'change':
            if self.changed_point_id != -1 and self.temp_item is not None:
                self.temp_item.p_list[self.changed_point_id] = [x, y]
        self.updateScene([self.sceneRect()])
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if x > 600:
            x = 600
        elif x < 0:
            x = 0
        if y > 600:
            y = 600
        elif y < 0:
            y = 0
        if self.status == 'line':
            self.finish_draw()
        if self.status == 'ellipse' and self.temp_item is not None:
            # self.temp_item.p_list[1] = (x, y)
            self.updateScene([self.sceneRect()])
            self.finish_draw()
        if self.status == 'translate' or self.status == 'rotate_a' or self.status == 'scale_a':
            self.item_dict[self.temp_id] = self.temp_item
            self.finish_draw()
        if self.status == 'clip':
            self.temp_item.clip(self.x_old, self.y_old, x, y, self.temp_algorithm)
            self.scene().removeItem(self.draw_item)
            self.item_dict[self.temp_id] = self.temp_item
            x0, y0 = self.temp_item.p_list[0]
            x1, y1 = self.temp_item.p_list[1]
            if x0 == 0 and y0 == 0 and x1 == 0 and y1 == 0:
                self.scene().removeItem(self.temp_item)
                self.temp_item = None
                self.selected_id = ''
                self.status = ''
            self.finish_draw()
        if self.status == 'selection':
            self.selection_changed(self.current_id)
            self.status = 'selection'
        if self.status == 'rotate_b' or self.status == 'scale_b':
            self.mode = 0
        if self.status == 'change':
            self.changed_point_id = -1
            self.finish_draw()
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if self.status == 'polygon' or self.status == 'curve':
            self.finish_draw()
            self.temp_item = None
        if self.status == 'line' or self.status == 'ellipse':
            pass
        super().mouseDoubleClickEvent(event)

    def wheelEvent(self, event: QWheelEvent) -> None:
        if self.status == 'rotate_b' and self.temp_id is not None:
            self.temp_item = self.item_dict[self.temp_id]
            angle = event.angleDelta() / 8
            r = angle.y() / 10
            if self.mode == 0:
                self.x_center, self.y_center = get_point(self.temp_item)
                self.mode = 1
            self.temp_item.rotate(self.x_center, self.y_center, r)
        if self.status == 'scale_b' and self.temp_id is not None:
            self.temp_item = self.item_dict[self.temp_id]
            angle = event.angleDelta() / 8
            s = 1 + angle.y() / 150
            if self.mode == 0:
                self.x_center, self.y_center = get_point(self.temp_item)
                self.mode = 1
            self.temp_item.scale_(self.x_center, self.y_center, s)
        self.finish_draw()
        self.updateScene([self.sceneRect()])

    def keyPressEvent(self, event: QKeyEvent) -> None:
        key = event.key()
        if self.selected_id != '':
            if key == Qt.Key_Escape:
                self.item_dict[self.selected_id].selected = False
                self.selected_id = ''
                self.status = ''
                self.updateScene([self.sceneRect()])
            else:
                QWidget.keyPressEvent(self, event)

    def resetCanvas(self):
        self.status = ''
        self.temp_algorithm = ''
        self.temp_id = ''
        self.temp_item = None
        self.item_dict = {}
        self.selected_id = ''

    def setPen_Color(self, color: QColor):
        self.pen_color = color

    def setPen_Width(self, width: int):
        self.pen_width = width

    def check_polygon(self, x, y):
        if self.temp_item is not None:
            tmp_list = self.temp_item.p_list
            for tmp in tmp_list:
                if (tmp[0] - x) * (tmp[0] - x) + (tmp[1] - y) * (tmp[1] - y) < 1:
                    return False
        return True


class MyItem(QGraphicsItem):
    """
    自定义图元类，继承自QGraphicsItem
    """

    def __init__(self, item_id: str, item_type: str, p_list: list, color: QColor, width: int = 2, algorithm: str = '',
                 parent: QGraphicsItem = None):
        """

        :param item_id: 图元ID
        :param item_type: 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        :param p_list: 图元参数
        :param algorithm: 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        :param parent:
        """
        super().__init__(parent)
        self.id = item_id  # 图元ID
        self.item_type = item_type  # 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        self.p_list = p_list  # 图元参数
        self.algorithm = algorithm  # 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        self.selected = False
        self.color = color
        self.width = width
        self.pencil = QPen()
        self.pencil.setColor(self.color)
        self.pencil.setWidth(self.width)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = ...) -> None:
        painter.setPen(self.pencil)
        if self.item_type == 'line':
            item_pixels = alg.draw_line(self.p_list, self.algorithm)
            for p in item_pixels:
                painter.drawPoint(*p)
        elif self.item_type == 'polygon':
            if len(self.p_list) >= 2:
                item_pixels = alg.draw_polygon(self.p_list, self.algorithm)
                for p in item_pixels:
                    painter.drawPoint(*p)
        elif self.item_type == 'ellipse':
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            if x0 > x1:
                x0, x1 = x1, x0
            if y0 < y1:
                y0, y1 = y1, y0
            tmp_list = [(x0, y0), (x1, y1)]
            # print(tmp_list)
            item_pixels = alg.draw_ellipse(tmp_list)
            for p in item_pixels:
                painter.drawPoint(*p)
        elif self.item_type == 'curve':
            if len(self.p_list) >= 2:
                item_pixels = alg.draw_curve(self.p_list, self.algorithm)
                for p in item_pixels:
                    painter.drawPoint(*p)
                if self.selected:
                    painter.setPen(QPen(Qt.darkCyan, 1, Qt.DotLine))
                    for i in range(1, len(self.p_list)):
                        painter.drawLine(self.p_list[i - 1][0], self.p_list[i - 1][1], self.p_list[i][0],
                                         self.p_list[i][1])

        elif self.item_type == 'rectangle':
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            p_list = [(x0, y0), (x0, y1), (x1, y1), (x1, y0)]
            item_pixels = alg.draw_polygon(p_list, "DDA")
            for p in item_pixels:
                painter.drawPoint(*p)
        else:
            pass
        if self.selected:
            painter.setPen(QPen(Qt.darkCyan, 1, Qt.DotLine))
            painter.drawRect(self.boundingRect())
            painter.setPen(QColor(0, 0, 255))
            for tmp in self.p_list:
                painter.drawRect(tmp[0] - 3, tmp[1] - 3, 6, 6)

    def boundingRect(self) -> QRectF:
        if self.item_type == 'line' or self.item_type == 'ellipse' or self.item_type == 'rectangle':
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            x = min(x0, x1)
            y = min(y0, y1)
            w = max(x0, x1) - x
            h = max(y0, y1) - y
            return QRectF(x - 1, y - 1, w + 2, h + 2)
        elif self.item_type == 'polygon' or self.item_type == 'curve':
            if len(self.p_list) == 0:
                return QRectF(0, 0, 0, 0)
            elif len(self.p_list) == 1:
                x, y = self.p_list[0]
                return QRectF(x - 1, y - 1, x + 1, y + 1)
            else:
                x_l, y_l = [], []
                for tmp in self.p_list:
                    x_l.append(tmp[0])
                    y_l.append(tmp[1])
                x, y = min(x_l), min(y_l)
                w, h = max(x_l) - x, max(y_l) - y
                return QRectF(x - 1, y - 1, w + 2, h + 2)
        ...

    def translate(self, dx, dy):
        self.p_list = alg.translate(self.p_list, dx, dy)

    def rotate(self, x, y, r):
        if self.item_type != "ellipse":
            self.p_list = alg.rotate(self.p_list, x, y, -r)

    def scale_(self, x, y, s):
        self.p_list = alg.scale(self.p_list, x, y, s)

    def clip(self, x0, y0, x1, y1, algorithm):
        if self.item_type == "line":
            self.p_list = alg.clip(self.p_list, x0, y0, x1, y1, algorithm)


class MainWindow(QMainWindow):
    """
    主窗口类
    """

    def __init__(self):
        super().__init__()
        self.color_choose = QFrame(self)
        self.pen_width = QSpinBox()
        self.pen_color = QPushButton("Pen Color")
        self.item_cnt = 0
        self.canvas_cnt = 0
        self.copy_item: MyItem = None
        self.tool_dock = QDockWidget("工具栏")
        self.canvas_dock = QDockWidget("绘制区域")
        self.list_dock = QDockWidget("图元列表")
        # 使用QListWidget来记录已有的图元，并用于选择图元。注：这是图元选择的简单实现方法，更好的实现是在画布中直接用鼠标选择图元
        self.list_widget = QListWidget(self.list_dock)
        self.list_widget.setFixedSize(200, 600)

        # 使用QGraphicsView作为画布
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, 600, 600)
        self.canvas_widget = MyCanvas(self.scene, self)
        self.canvas_widget.setFixedSize(600 + 2, 600 + 2)
        self.canvas_widget.main_window = self
        self.canvas_widget.list_widget = self.list_widget
        self.canvas_dock.setWidget(self.canvas_widget)

        # 设置文件菜单栏
        menubar = self.menuBar()
        file_menu = menubar.addMenu('文件')
        file_toolbar = QToolBar('File')
        file_toolbar.setMovable(False)
        self.addToolBar(file_toolbar)
        reset_canvas_act = QAction(QIcon('../icon/reset.png'), '重置画布', self)
        save_canvas_act = QAction(QIcon('../icon/save.png'), '保存画布', self)
        export_canvas_act = QAction(QIcon('../icon/export.png'), '导出画布命令', self)
        copy_act = QAction(QIcon('../icon/copy.png'), '复制', self)
        self.paste_act = QAction(QIcon('../icon/paste.png'), '粘贴', self)
        exit_act = QAction(QIcon('../icon/exit.png'), '退出', self)
        file_menu.addAction(reset_canvas_act)
        file_menu.addAction(save_canvas_act)
        file_menu.addAction(export_canvas_act)
        file_menu.addAction(copy_act)
        file_menu.addAction(self.paste_act)
        file_menu.addAction(exit_act)
        file_toolbar.addAction(reset_canvas_act)
        file_toolbar.addAction(save_canvas_act)
        file_toolbar.addAction(export_canvas_act)
        file_toolbar.addAction(copy_act)
        file_toolbar.addAction(self.paste_act)
        # 设置绘制菜单栏
        draw_menu = menubar.addMenu('绘制')
        # 直线菜单/按钮
        line_menu = QMenu('线段', self)
        draw_menu.addMenu(line_menu)
        line_naive_act = QAction(QIcon('../icon/line.png'), 'Naive', self)
        line_dda_act = QAction(QIcon('../icon/line.png'), 'DDA', self)
        line_bresenham_act = QAction(QIcon('../icon/line.png'), 'Bresenham', self)
        line_menu.addAction(line_naive_act)
        line_menu.addAction(line_dda_act)
        line_menu.addAction(line_bresenham_act)
        line_button = QToolButton(self)
        line_button.setPopupMode(QToolButton.MenuButtonPopup)
        line_button.setMenu(line_menu)
        line_button.setDefaultAction(line_dda_act)
        line_toolbar = QToolBar(self)
        line_toolbar.addWidget(line_button)
        # 多边形菜单/按钮
        polygon_menu = QMenu('多边形', self)
        draw_menu.addMenu(polygon_menu)
        polygon_dda_act = QAction(QIcon('../icon/polygon.png'), 'DDA', self)
        polygon_bresenham_act = QAction(QIcon('../icon/polygon.png'), 'Bresenham', self)
        polygon_menu.addAction(polygon_dda_act)
        polygon_menu.addAction(polygon_bresenham_act)
        polygon_button = QToolButton(self)
        polygon_button.setPopupMode(QToolButton.MenuButtonPopup)
        polygon_button.setMenu(polygon_menu)
        polygon_button.setDefaultAction(polygon_dda_act)
        polygon_toolbar = QToolBar(self)
        polygon_toolbar.addWidget(polygon_button)
        # 椭圆菜单/按钮
        ellipse_act = QAction(QIcon('../icon/ellipse.png'), '椭圆', self)
        draw_menu.addAction(ellipse_act)
        ellipse_button = QToolButton(self)
        ellipse_button.setDefaultAction(ellipse_act)
        ellipse_toolbar = QToolBar(self)
        ellipse_toolbar.addWidget(ellipse_button)
        # 曲线菜单/按钮
        curve_menu = QMenu('曲线', self)
        draw_menu.addMenu(curve_menu)
        curve_bezier_act = QAction(QIcon('../icon/curve1.png'), 'Bezier', self)
        curve_b_spline_act = QAction(QIcon('../icon/curve1.png'), 'B-spline', self)
        curve_menu.addAction(curve_bezier_act)
        curve_menu.addAction(curve_b_spline_act)
        curve_button = QToolButton(self)
        curve_button.setPopupMode(QToolButton.MenuButtonPopup)
        curve_button.setMenu(curve_menu)
        curve_button.setDefaultAction(curve_bezier_act)
        curve_toolbar = QToolBar(self)
        curve_toolbar.addWidget(curve_button)
        # 设置编辑菜单栏
        edit_menu = menubar.addMenu('编辑')
        # 选择菜单/按钮
        selection_act = QAction(QIcon('../icon/selection.png'), '选择', self)
        edit_menu.addAction(selection_act)
        selection_button = QToolButton(self)
        selection_button.setDefaultAction(selection_act)
        selection_toolbar = QToolBar(self)
        selection_toolbar.addWidget(selection_button)
        # 平移菜单/按钮
        translate_act = QAction(QIcon('../icon/translate.png'), '平移', self)
        edit_menu.addAction(translate_act)
        translate_button = QToolButton(self)
        translate_button.setDefaultAction(translate_act)
        translate_toolbar = QToolBar(self)
        translate_toolbar.addWidget(translate_button)
        # 旋转菜单/按钮
        rotate_menu = QMenu('旋转', self)
        edit_menu.addMenu(rotate_menu)
        rotate_a_act = QAction(QIcon('../icon/rotate.png'), '旋转A', self)
        rotate_b_act = QAction(QIcon('../icon/rotate.png'), '旋转B', self)
        rotate_menu.addAction(rotate_a_act)
        rotate_menu.addAction(rotate_b_act)
        rotate_button = QToolButton(self)
        rotate_button.setPopupMode(QToolButton.MenuButtonPopup)
        rotate_button.setMenu(rotate_menu)
        rotate_button.setDefaultAction(rotate_a_act)
        rotate_toolbar = QToolBar(self)
        rotate_toolbar.addWidget(rotate_button)
        # 缩放菜单/按钮
        scale_menu = QMenu('缩放', self)
        edit_menu.addMenu(scale_menu)
        scale_a_act = QAction(QIcon('../icon/scale.png'), '缩放A', self)
        scale_b_act = QAction(QIcon('../icon/scale.png'), '缩放B', self)
        scale_menu.addAction(scale_a_act)
        scale_menu.addAction(scale_b_act)
        scale_button = QToolButton(self)
        scale_button.setPopupMode(QToolButton.MenuButtonPopup)
        scale_button.setMenu(scale_menu)
        scale_button.setDefaultAction(scale_a_act)
        scale_toolbar = QToolBar(self)
        scale_toolbar.addWidget(scale_button)
        # 裁剪菜单/按钮
        clip_menu = QMenu('裁剪', self)
        edit_menu.addMenu(clip_menu)
        clip_cohen_sutherland_act = QAction(QIcon('../icon/clip.png'), 'Cohen-Sutherland', self)
        clip_liang_barsky_act = QAction(QIcon('../icon/clip.png'), 'Liang-Barsky', self)
        clip_menu.addAction(clip_cohen_sutherland_act)
        clip_menu.addAction(clip_liang_barsky_act)
        clip_button = QToolButton(self)
        clip_button.setPopupMode(QToolButton.MenuButtonPopup)
        clip_button.setMenu(clip_menu)
        clip_button.setDefaultAction(clip_cohen_sutherland_act)
        clip_toolbar = QToolBar(self)
        clip_toolbar.addWidget(clip_button)
        # 变换坐标菜单/按钮
        change_act = QAction(QIcon('../icon/change.png'), '变换坐标', self)
        edit_menu.addAction(change_act)
        change_button = QToolButton(self)
        change_button.setDefaultAction(change_act)
        change_toolbar = QToolBar(self)
        change_toolbar.addWidget(change_button)
        theme_menu = menubar.addMenu('主题')
        theme_1_act = theme_menu.addAction('Sky')
        theme_2_act = theme_menu.addAction('Sunray')
        theme_3_act = theme_menu.addAction('Wood')

        # 连接信号和槽函数
        reset_canvas_act.triggered.connect(self.reset_canvas_action)
        save_canvas_act.triggered.connect(self.save_canvas_action)
        export_canvas_act.triggered.connect(self.export_canvas_action)
        copy_act.triggered.connect(self.copy_action)
        self.paste_act.triggered.connect(self.paste_action)
        exit_act.triggered.connect(self.exit_action)
        line_naive_act.triggered.connect(self.line_naive_action)
        line_dda_act.triggered.connect(self.line_dda_action)
        line_bresenham_act.triggered.connect(self.line_bresenham_action)
        polygon_dda_act.triggered.connect(self.polygon_dda_action)
        polygon_bresenham_act.triggered.connect(self.polygon_bresenham_action)
        ellipse_act.triggered.connect(self.ellipse_action)
        curve_bezier_act.triggered.connect(self.curve_bezier_action)
        curve_b_spline_act.triggered.connect(self.curve_b_spline_action)
        translate_act.triggered.connect(self.translate_action)
        rotate_a_act.triggered.connect(self.rotate_a_action)
        rotate_b_act.triggered.connect(self.rotate_b_action)
        scale_a_act.triggered.connect(self.scale_a_action)
        scale_b_act.triggered.connect(self.scale_b_action)
        clip_cohen_sutherland_act.triggered.connect(self.clip_cohen_sutherland_action)
        clip_liang_barsky_act.triggered.connect(self.clip_liang_barsky_action)
        selection_act.triggered.connect(self.selection_action)
        change_act.triggered.connect(self.change_action)
        theme_1_act.triggered.connect(self.theme_1_action)
        theme_2_act.triggered.connect(self.theme_2_action)
        theme_3_act.triggered.connect(self.theme_3_action)
        self.list_widget.currentTextChanged.connect(self.canvas_widget.selection_changed)
        self.pen_width.valueChanged[int].connect(self.set_pen_width_action)
        self.pen_color.clicked.connect(self.set_pen_color_action)

        # 设置画笔设置栏
        color_toolbar = QToolBar("Color")
        color_toolbar.setMovable(False)
        self.addToolBar(color_toolbar)
        label1 = QLabel("Pen Width")
        self.pen_width.setRange(1, 20)
        self.pen_width.setValue(1)
        self.color_choose.setFrameShape(QFrame.Box)
        self.color_choose.setPalette(QPalette(Qt.black))
        self.color_choose.setAutoFillBackground(True)
        self.color_choose.setFixedSize(20, 20)
        self.color_choose.setStyleSheet("QFrame{background-color:rgba(0,0,0,1);border:none}")
        color_layout = QHBoxLayout()
        color_layout.setAlignment(Qt.AlignLeft)
        color_layout.addWidget(self.pen_color)
        color_layout.addWidget(self.color_choose)
        color_layout.addWidget(label1)
        color_layout.addWidget(self.pen_width)
        color_widget = QWidget()
        color_widget.setLayout(color_layout)
        color_toolbar.addWidget(color_widget)
        # 设置工具栏
        tool_layout = QGridLayout()
        tool_layout.setAlignment(Qt.AlignLeft)
        tool_layout.addWidget(line_toolbar, 0, 0)
        tool_layout.addWidget(polygon_toolbar, 1, 0)
        tool_layout.addWidget(ellipse_toolbar, 2, 0)
        tool_layout.addWidget(curve_toolbar, 3, 0)
        tool_layout.addWidget(selection_toolbar, 4, 0)
        tool_layout.addWidget(translate_toolbar, 5, 0)
        tool_layout.addWidget(rotate_toolbar, 6, 0)
        tool_layout.addWidget(scale_toolbar, 7, 0)
        tool_layout.addWidget(clip_toolbar, 8, 0)
        tool_layout.addWidget(change_toolbar, 9, 0)
        tool_widget = QWidget(self.tool_dock)
        tool_widget.setFixedWidth(70)
        tool_widget.setLayout(tool_layout)
        # 设置主窗口的布局
        self.statusBar().showMessage('空闲')
        self.resize(610, 610)
        self.setWindowTitle('CG_Ty_181860087')
        self.setWindowIcon(QIcon('../icon/icon1.png'))
        self.setDockNestingEnabled(True)
        self.canvas_dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.canvas_dock.setMinimumSize(603, 603)
        self.canvas_widget.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(self.canvas_dock)
        self.list_dock.setFeatures(QDockWidget.DockWidgetClosable)
        self.list_dock.setWidget(self.list_widget)
        self.tool_dock.setWidget(tool_widget)
        self.tool_dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable
                                   | QDockWidget.DockWidgetClosable)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.tool_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.list_dock)
        try:
            with open("../qss/sunshine.qss") as f:
                qss = f.read()
                self.setStyleSheet(qss)
        except FileNotFoundError:
            print("enter the correct path")

    def closeEvent(self, event: QCloseEvent) -> None:
        # print(len(self.canvas_widget.item_dict))
        if len(self.canvas_widget.item_dict) != 0:
            if QMessageBox.question(self, '退出', '确认退出？\n检测到有未保存的修改，退出后所有未保存的修改将永久丢失',
                                    QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        key = event.key()
        if key == Qt.Key_Escape:
            self.copy_item = None
        else:
            QWidget.keyPressEvent(self, event)
        self.update_button()

    # bug fixed: fix the problem of id when changing the mode
    def add_id(self):
        _id = str(self.item_cnt + 1)
        self.item_cnt += 1
        return _id

    def get_id(self):
        _id = str(self.item_cnt)
        return _id

    def reset_canvas_action(self):
        text, flag = QInputDialog.getText(self, '重置画布', '确认重置画布？\n如要继续，请在下方输入新的画布尺寸，“宽 高”',
                                          text='%d %d' % (self.scene.width(), self.scene.height()))
        if flag:
            try:
                tmp_list = text.split(' ', 1)
                w, h = int(tmp_list[0]), int(tmp_list[1])
                if w > 1000 or h > 1000 or w <= 0 or h <= 0:
                    QMessageBox.critical(self, '操作失败', '请检查输入，修改后重试')
                    return
                self.item_cnt = 0
                self.canvas_widget.resetCanvas()
                self.list_widget.currentTextChanged.disconnect(self.canvas_widget.selection_changed)
                self.list_widget.clear()
                self.list_widget.currentTextChanged.connect(self.canvas_widget.selection_changed)
                self.scene = QGraphicsScene(self)
                self.scene.setSceneRect(0, 0, w, h)
                self.canvas_dock.setMinimumSize(w + 3, h + 3)
                self.canvas_widget.setScene(self.scene)
                self.canvas_widget.setFixedSize(w + 2, h + 2)
            except BaseException:
                QMessageBox.critical(self, '操作失败', '请检查输入，修改后重试')

    def save_canvas_action(self):
        dialog = QFileDialog()
        filename = dialog.getSaveFileName(self, "SAVE", QDir.currentPath(), "BMP(*.bmp);;JPEG("
                                                                            "*.jpeg);;PNG(*.png);;ALL FILES(*)")
        if filename[0]:
            self.canvas_widget.clear_selection()
            tmp_map = self.canvas_widget.grab(self.canvas_widget.sceneRect().toRect())
            tmp_map.save(filename[0])

    def export_canvas_action(self):
        dialog = QFileDialog()
        filename = dialog.getSaveFileName(self, "EXPORT", QDir.currentPath())
        if filename[0]:
            line = 'resetCanvas %d %d\n' % (self.scene.width(), self.scene.height())
            with open(filename[0], 'wt') as f:
                for tmp in self.canvas_widget.item_dict.values():
                    line += 'setColor %d %d %d\n' % (
                        QColor(tmp.color).red(), QColor(tmp.color).green(), QColor(tmp.color).blue())
                    line += 'draw' + tmp.item_type.capitalize() + ' '
                    line += tmp.id + ' '
                    for p in tmp.p_list:
                        line += '%d %d ' % (p[0], p[1])
                    line += tmp.algorithm + '\n'
                line += 'saveCanvas' + ' EXPORT' + '%d' % self.canvas_cnt
                self.canvas_cnt += 1
                f.write(line)

    def exit_action(self):
        # print(len(self.canvas_widget.item_dict))
        if len(self.canvas_widget.item_dict):
            if QMessageBox.question(self, '退出', '确认退出？\n检测到有未保存的修改，退出后所有未保存的修改将永久丢失',
                                    QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                qApp.quit()
        else:
            qApp.quit()

    def line_naive_action(self):
        if self.canvas_widget.temp_item is None:
            self.canvas_widget.start_draw_line('Naive', self.get_id())
        else:
            self.canvas_widget.start_draw_line('Naive', self.add_id())
        self.update_button()
        self.statusBar().showMessage('Naive算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def line_dda_action(self):
        if self.canvas_widget.temp_item is None:
            self.canvas_widget.start_draw_line('DDA', self.get_id())
        else:
            self.canvas_widget.start_draw_line('DDA', self.add_id())
        self.update_button()
        self.statusBar().showMessage('DDA算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def line_bresenham_action(self):
        if self.canvas_widget.temp_item is None:
            self.canvas_widget.start_draw_line('Bresenham', self.get_id())
        else:
            self.canvas_widget.start_draw_line('Bresenham', self.add_id())
        self.update_button()
        self.statusBar().showMessage('Bresenham算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def polygon_dda_action(self):
        if self.canvas_widget.temp_item is None:
            self.canvas_widget.start_draw_polygon('DDA', self.get_id())
        else:
            self.canvas_widget.start_draw_polygon('DDA', self.add_id())
        self.update_button()
        self.statusBar().showMessage('DDA算法绘制多边形')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def polygon_bresenham_action(self):
        if self.canvas_widget.temp_item is None:
            self.canvas_widget.start_draw_polygon('Bresenham', self.get_id())
        else:
            self.canvas_widget.start_draw_polygon('Bresenham', self.add_id())
        self.update_button()
        self.statusBar().showMessage('Bresenham算法绘制多边形')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def ellipse_action(self):
        if self.canvas_widget.temp_item is None:
            self.canvas_widget.start_draw_ellipse(self.get_id())
        else:
            self.canvas_widget.start_draw_ellipse(self.add_id())
        self.update_button()
        self.statusBar().showMessage('中点圆算法绘制椭圆')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def curve_bezier_action(self):
        if self.canvas_widget.temp_item is None:
            self.canvas_widget.start_draw_curve('Bezier', self.get_id())
        else:
            self.canvas_widget.start_draw_curve('Bezier', self.add_id())
        self.update_button()
        self.statusBar().showMessage('Bezier算法绘制曲线')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def curve_b_spline_action(self):
        if self.canvas_widget.temp_item is None:
            self.canvas_widget.start_draw_curve('B-spline', self.get_id())
        else:
            self.canvas_widget.start_draw_curve('B-spline', self.add_id())
        self.update_button()
        self.statusBar().showMessage('B-spline算法绘制曲线')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def translate_action(self):
        flag = 0
        if self.canvas_widget.temp_item is not None:
            flag = 1
        self.canvas_widget.start_translate()
        if flag == 1:
            self.add_id()
        self.update_button()
        self.statusBar().showMessage('左键拖动进行平移')

    def rotate_a_action(self):
        flag = 0
        if self.canvas_widget.temp_item is not None:
            flag = 1
        self.canvas_widget.start_rotate_a()
        if flag == 1:
            self.add_id()
        self.update_button()
        self.statusBar().showMessage('左键拖动进行旋转，旋转中心为图元中心')

    def rotate_b_action(self):
        flag = 0
        if self.canvas_widget.temp_item is not None:
            flag = 1
        self.canvas_widget.start_rotate_b()
        if flag == 1:
            self.add_id()
        self.update_button()
        self.statusBar().showMessage('滚轮进行旋转，默认旋转中心为图元中心，左键点击选择旋转中心')

    def scale_a_action(self):
        flag = 0
        if self.canvas_widget.temp_item is not None:
            flag = 1
        self.canvas_widget.start_scale_a()
        if flag == 1:
            self.add_id()
        self.update_button()
        self.statusBar().showMessage('左键拖动进行缩放，缩放中心为图元中心')

    def scale_b_action(self):
        flag = 0
        if self.canvas_widget.temp_item is not None:
            flag = 1
        self.canvas_widget.start_scale_b()
        if flag == 1:
            self.add_id()
        self.update_button()
        self.statusBar().showMessage('滚轮进行缩放，默认缩放中心为图元中心，左键点击选择缩放中心')

    def clip_cohen_sutherland_action(self):
        flag = 0
        if self.canvas_widget.temp_item is not None:
            flag = 1
        self.canvas_widget.start_clip('Cohen-Sutherland')
        if flag == 1:
            self.add_id()
        self.update_button()
        self.statusBar().showMessage('Cohen-Sutherland算法裁剪直线')

    def clip_liang_barsky_action(self):
        flag = 0
        if self.canvas_widget.temp_item is not None:
            flag = 1
        self.canvas_widget.start_clip('Liang-Barsky')
        if flag == 1:
            self.add_id()
        self.update_button()
        self.statusBar().showMessage('Liang-Barsky算法裁剪直线')

    def selection_action(self):
        flag = 0
        if self.canvas_widget.temp_item is not None:
            flag = 1
        self.canvas_widget.select_primitive()
        if flag == 1:
            self.add_id()
        self.update_button()
        self.statusBar().showMessage('左键选择任意图元')

    def change_action(self):
        flag = 0
        if self.canvas_widget.temp_item is not None:
            flag = 1
        self.canvas_widget.change_xy()
        if flag == 1:
            self.add_id()
        self.update_button()
        self.statusBar().showMessage('左键选择任意一个参数点，拖动点进行坐标更改')

    def set_pen_width_action(self):
        w = self.pen_width.text()
        self.canvas_widget.setPen_Width(int(w))
        # self.statusBar().showMessage('左键点击Pen Width的SpinBox选择画笔宽度')

    def set_pen_color_action(self):
        # self.statusBar().showMessage('左键点击Pen Color按钮选择画笔颜色')
        flag = 0
        c = QColorDialog.getColor()
        self.canvas_widget.setPen_Color(c)
        self.color_choose.setPalette(QPalette(c))
        self.color_choose.setStyleSheet("QWidget{background-color: %s}" % c.name())

    def theme_1_action(self):
        try:
            with open("../qss/sky.qss") as f:
                qss = f.read()
                self.setStyleSheet(qss)
        except FileNotFoundError:
            print("enter the correct path")

    def theme_2_action(self):
        try:
            with open("../qss/sunshine.qss") as f:
                qss = f.read()
                self.setStyleSheet(qss)
        except FileNotFoundError:
            print("enter the correct path")

    def theme_3_action(self):
        try:
            with open("../qss/wood.qss") as f:
                qss = f.read()
                self.setStyleSheet(qss)
        except FileNotFoundError:
            print("enter the correct path")

    def copy_action(self):
        if self.canvas_widget.selected_id != '':
            tmp_item = self.canvas_widget.item_dict[self.canvas_widget.selected_id]
            self.copy_item = MyItem(tmp_item.id,
                                    tmp_item.item_type,
                                    tmp_item.p_list.copy(),
                                    tmp_item.color,
                                    tmp_item.width,
                                    tmp_item.algorithm)
        else:
            pass
        self.update_button()

    def paste_action(self):
        if self.copy_item:
            new_list = []
            for p in self.copy_item.p_list:
                new_list.append((p[0]+30, p[1]+30))
            tmp_item = MyItem(self.get_id(),
                              self.copy_item.item_type,
                              new_list,
                              self.copy_item.color,
                              self.copy_item.width,
                              self.copy_item.algorithm)
            tmp_item.selected = False
            self.canvas_widget.scene().addItem(tmp_item)
            self.canvas_widget.item_dict[tmp_item.id] = tmp_item
            self.canvas_widget.scene().update()
            self.list_widget.addItem(tmp_item.id)
            self.add_id()
            self.copy_item = MyItem(tmp_item.id,
                                    tmp_item.item_type,
                                    tmp_item.p_list.copy(),
                                    tmp_item.color,
                                    tmp_item.width,
                                    tmp_item.algorithm)
        else:
            pass

    def update_button(self):
        if self.copy_item is None \
                or self.canvas_widget.status == 'line'\
                or self.canvas_widget.status == 'ellipse'\
                or self.canvas_widget.status == 'polygon'\
                or self.canvas_widget.status == 'curve':
            self.paste_act.setEnabled(False)
        else:
            self.paste_act.setEnabled(True)


class MySplashScreen(QSplashScreen):
    def __init__(self):
        super(MySplashScreen, self).__init__()
        message_font = QFont()
        message_font.setBold(True)
        message_font.setPointSize(12)
        self.setFont(message_font)
        pixmap = QPixmap("../icon/start.jpg")
        self.setPixmap(pixmap)
        self.show()
        for i in range(1, 7):
            self.showMessage('MyPainter By Ty--NJU_CG_Project\n正在加载文件资源{}'.format('.' * i), alignment=Qt.AlignBottom,
                             color=Qt.white)
            time.sleep(0.3)

    def mousePressEvent(self, evt):
        pass

    def mouseDoubleClickEvent(self, *args, **kwargs):
        pass

    def enterEvent(self, *args, **kwargs):
        pass


if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        splash = MySplashScreen()
        app.processEvents()
        mw = MainWindow()
        mw.show()
        mw.update_button()
        splash.finish(mw)
        splash.deleteLater()
        sys.exit(app.exec_())
    except(KeyError, AttributeError):
        print("select the wrong id")