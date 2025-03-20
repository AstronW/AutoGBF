#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging

from dataclasses import dataclass

from PySide6.QtCore import Qt, QRect, QSize, Signal, QEvent
from PySide6.QtWidgets import QWidget, QSizePolicy
from PySide6.QtGui import QPainter, QBrush, QColor, QPalette


def _left_thumb_adjuster(value, min_value):
    """调整左滑块值，确保不小于最小值"""
    value = max(value, min_value)


def _right_thumb_adjuster(value, max_value):
    """调整右滑块值，确保不大于最大值"""
    value = min(value, max_value)


def _set_painter_pen_color(painter, pen_color):
    """设置画笔颜色"""
    pen = painter.pen()
    pen.setColor(pen_color)
    painter.setPen(pen)


@dataclass
class Thumb:
    """滑块类，保存滑块的相关信息"""

    value: int  # 滑块的值
    rect: QRect  # 滑块的矩形区域
    pressed: bool  # 滑块是否被按下


class RangeSlider(QWidget):
    """
    双滑块范围选择器，实现一个带有两个滑块的滑动条。

    方法：
            * __init__ (self, QWidget parent, left_value, right_value, left_thumb_value=0, right_thumb_value=None)
            * set_left_thumb_value (self, int value): 设置左滑块的值
            * set_right_thumb_value (self, int value): 设置右滑块的值
            * (int) left (self): 获取左滑块的值
            * (int) right (self): 获取右滑块的值

    信号：
            * left_thumb_value_changed (int): 左滑块值改变信号
            * right_thumb_value_changed (int): 右滑块值改变信号
    """

    HEIGHT = 50  # 控件高度
    WIDTH = 120  # 控件宽度
    THUMB_WIDTH = 16  # 滑块宽度
    THUMB_HEIGHT = 16  # 滑块高度
    TRACK_HEIGHT = 3  # 轨道高度
    TRACK_COLOR = QColor(0xC7, 0xC7, 0xC7)  # 轨道颜色
    TRACK_FILL_COLOR = QColor(0x01, 0x81, 0xFF)  # 轨道填充颜色
    TRACK_PADDING = THUMB_WIDTH // 2 + 5  # 轨道内边距
    TICK_PADDING = 5  # 刻度内边距
    TEXT_PADDING = 5  # 文本内边距
    TEXT_HEIGHT = 5  # 文本高度

    # 定义信号
    left_thumb_value_changed = Signal("unsigned long long")
    right_thumb_value_changed = Signal("unsigned long long")

    def __init__(
        self,
        parent,
        min,
        max,
        left_thumb_value=0,
        right_thumb_value=None,
    ):
        """
        初始化范围滑动条

        参数：
            parent: 父控件
            min: 最小值
            max: 最大值
            left_thumb_value: 左滑块初始值
            right_thumb_value: 右滑块初始值
        """
        super().__init__(parent)

        # 设置尺寸策略和最小尺寸
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumWidth(self.WIDTH)
        self.setMinimumHeight(self.HEIGHT)

        # 设置范围值
        self._min = min
        self._max = max

        # 初始化左滑块
        self._left_thumb = Thumb(left_thumb_value, None, False)

        # 初始化右滑块，如果未指定则使用最大值
        _right_thumb_value = (
            right_thumb_value if right_thumb_value is not None else self._max
        )
        if _right_thumb_value < left_thumb_value + 1:
            raise ValueError("Right thumb value is less or equal left thumb value.")
        self._right_thumb = Thumb(_right_thumb_value, None, False)

        # 初始化画布尺寸
        self._canvas_width = None
        self._canvas_height = None

        # 初始化刻度数量
        self._ticks_count = 0

        # 更新调色板颜色
        self.update_palette_colors()

    def update_palette_colors(self):
        """更新调色板颜色"""
        parent_palette = self.parent().palette()
        self._background_color = parent_palette.color(QPalette.ColorRole.Window)
        self._base_color = parent_palette.color(QPalette.ColorRole.Base)
        self._button_color = parent_palette.color(QPalette.ColorRole.Button)
        self._border_color = parent_palette.color(QPalette.ColorRole.Mid)

    def changeEvent(self, event):
        """处理主题变化事件"""
        if event.type() == QEvent.Type.PaletteChange:
            self.update_palette_colors()
            self.update()
        super().changeEvent(event)

    def paintEvent(self, unused_e):
        """绘制事件处理函数"""
        logging.debug("paintEvent")
        del unused_e
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 绘制各个组件
        self.__draw_track(self._canvas_width, self._canvas_height, painter)
        self.__draw_track_fill(self._canvas_width, self._canvas_height, painter)
        self.__draw_ticks(
            self._canvas_width, self._canvas_height, painter, self._ticks_count
        )
        self.__draw_left_thumb(self._canvas_width, self._canvas_height, painter)
        self.__draw_right_thumb(self._canvas_width, self._canvas_height, painter)

        painter.end()

    def __get_track_y_position(self):
        """获取轨道的Y坐标位置"""
        return self._canvas_height // 2 - self.TRACK_HEIGHT // 2 + self.TEXT_HEIGHT

    def __draw_track(self, canvas_width, canvas_height, painter):
        """绘制轨道"""
        del canvas_height
        brush = QBrush()
        brush.setColor(self.TRACK_COLOR)
        brush.setStyle(Qt.BrushStyle.SolidPattern)

        rect = QRect(
            self.TRACK_PADDING,
            self.__get_track_y_position(),
            canvas_width - 2 * self.TRACK_PADDING,
            self.TRACK_HEIGHT,
        )
        painter.fillRect(rect, brush)

    def __draw_track_fill(self, canvas_width, canvas_height, painter):
        """绘制轨道填充部分（两个滑块之间的区域）"""
        del canvas_height
        brush = QBrush()
        brush.setColor(self.TRACK_FILL_COLOR)
        brush.setStyle(Qt.BrushStyle.SolidPattern)

        # 计算填充区域的位置和大小
        available_width = canvas_width - 2 * self.TRACK_PADDING
        x1 = self._left_thumb.value / self._max * available_width + self.TRACK_PADDING
        x2 = self._right_thumb.value / self._max * available_width + self.TRACK_PADDING
        rect = QRect(
            round(x1),
            self.__get_track_y_position(),
            round(x2) - round(x1),
            self.TRACK_HEIGHT,
        )
        painter.fillRect(rect, brush)

    def __draw_thumb(self, x, y, painter, thumb):
        """绘制滑块"""
        brush = QBrush(QColor(255, 255, 255))  # 纯白色，不透明

        painter.setBrush(brush)

        # 创建滑块矩形并绘制椭圆
        thumb_rect = QRect(
            round(x) - self.THUMB_WIDTH // 2 + self.TRACK_PADDING,
            y + self.TRACK_HEIGHT // 2 - self.THUMB_HEIGHT // 2,
            self.THUMB_WIDTH,
            self.THUMB_HEIGHT,
        )
        painter.drawEllipse(thumb_rect)

        # 绘制滑块值文本
        text = str(thumb.value)
        font = painter.font()
        font.setPointSize(9)
        painter.setFont(font)

        text_width = painter.fontMetrics().horizontalAdvance(text)
        text_x = thumb_rect.center().x() - text_width // 2
        text_y = thumb_rect.top() - self.TEXT_PADDING

        painter.drawText(text_x, text_y, text)

        return thumb_rect

    def __draw_right_thumb(self, canvas_width, canvas_height, painter):
        """绘制右滑块"""
        del canvas_height
        available_width = canvas_width - 2 * self.TRACK_PADDING
        x = self._right_thumb.value / self._max * available_width
        y = self.__get_track_y_position()
        self._right_thumb.rect = self.__draw_thumb(x, y, painter, self._right_thumb)

    def __draw_left_thumb(self, canvas_width, canvas_height, painter):
        """绘制左滑块"""
        del canvas_height
        available_width = canvas_width - 2 * self.TRACK_PADDING
        x = round(self._left_thumb.value / self._max * available_width)
        y = self.__get_track_y_position()
        self._left_thumb.rect = self.__draw_thumb(x, y, painter, self._left_thumb)

    def set_left_thumb_value(self, value):
        """设置左滑块的值"""
        if value < 0 or value > self._right_thumb.value - 1:
            return
        if value == self._left_thumb.value:
            # 值未变，无需更新
            return
        self._left_thumb.value = value
        # pylint: disable=logging-fstring-interpolation
        logging.debug(f"value before emit {value}")
        self.left_thumb_value_changed.emit(value)
        self.repaint()

    def set_right_thumb_value(self, value):
        """设置右滑块的值"""
        if value > self._max or value < self._left_thumb.value + 1:
            return
        if value == self._right_thumb.value:
            # 值未变，无需更新
            return
        self._right_thumb.value = value
        # pylint: disable=logging-fstring-interpolation
        logging.debug(f"value before emit {value}")
        self.right_thumb_value_changed.emit(value)
        self.repaint()

    # 重写Qt事件
    def mousePressEvent(self, event):
        """鼠标按下事件处理"""
        logging.debug("mousePressEvent")
        position = event.position()
        if self._left_thumb.rect.contains(int(position.x()), int(position.y())):
            self._left_thumb.pressed = True
        if self._right_thumb.rect.contains(int(position.x()), int(position.y())):
            self._right_thumb.pressed = True
        super().mousePressEvent(event)

    # 重写Qt事件
    def mouseReleaseEvent(self, event):
        """鼠标释放事件处理"""
        logging.debug("mouseReleaseEvent")
        self._left_thumb.pressed = False
        self._right_thumb.pressed = False
        super().mouseReleaseEvent(event)

    def __get_thumb_value(self, x, canvas_width, right_value):
        """根据鼠标位置计算滑块值"""
        # pylint: disable=logging-fstring-interpolation
        logging.debug(
            f"x {x} canvas_width {canvas_width} left_value {self._left_thumb.value} right_value {right_value}"
        )
        return round(x / canvas_width * right_value)

    # 重写Qt事件
    def mouseMoveEvent(self, event):
        """鼠标移动事件处理"""
        logging.debug("mouseMoveEvent")

        # 确定当前操作的是哪个滑块
        thumb = self._left_thumb if self._left_thumb.pressed else self._right_thumb

        if thumb.pressed:
            # 根据滑块类型选择不同的值设置器和调整器
            if thumb == self._left_thumb:
                value_setter = self.set_left_thumb_value

                def value_adjuster(val):
                    return _left_thumb_adjuster(val, 0)

            else:
                value_setter = self.set_right_thumb_value

                def value_adjuster(val):
                    return _right_thumb_adjuster(val, self._max)

            # 计算新值并应用
            new_val = self.__get_thumb_value(
                event.position().x(), self._canvas_width, self._max
            )
            value_adjuster(new_val)
            value_changed = new_val != thumb.value
            if value_changed:
                value_setter(new_val)

        super().mouseMoveEvent(event)

    def left(self):
        """获取左滑块的值"""
        return self._left_thumb.value

    def right(self):
        """获取右滑块的值"""
        return self._right_thumb.value

    def set_ticks_count(self, count):
        """设置刻度数量"""
        if count < 0:
            raise ValueError("Invalid ticks count.")
        self._ticks_count = count

    def __draw_ticks(self, canvas_width, canvas_height, painter, ticks_count):
        """绘制刻度线"""
        del canvas_height
        if not self._ticks_count:
            return

        _set_painter_pen_color(painter, self._border_color)

        # 计算刻度间距并绘制刻度线
        tick_step = (canvas_width - 2 * self.TRACK_PADDING) // ticks_count
        y1 = self.__get_track_y_position() - self.TICK_PADDING
        y2 = y1 - self.THUMB_HEIGHT // 2
        for x in range(0, ticks_count + 1):
            x = x * tick_step + self.TRACK_PADDING
            painter.drawLine(x, y1, x, y2)

    def resizeEvent(self, event):
        """调整大小事件处理"""
        logging.debug("resizeEvent")
        del event
        self._canvas_width = self.width()
        self._canvas_height = self.height()


from PySide6.QtWidgets import QApplication, QWidget


if __name__ == "__main__":
    # 示例代码：创建应用程序和窗口，展示范围滑动条的使用
    app = QApplication([])
    window = QWidget()
    range_slider = RangeSlider(
        window, 0, 100, 30, 70
    )  # 创建范围从0到100，初始值为30和70的滑动条
    range_slider.setFixedWidth(200)  # 设置固定宽度
    window.show()  # 显示窗口
    app.exec()  # 运行应用程序主循环
