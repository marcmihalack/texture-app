import math
import sys
import numpy as np
from enum import Flag
from PyQt6 import QtCore
from PyQt6.QtCore import Qt, QRect, QPoint
from PyQt6.QtGui import QImage, QColor, QPainter, QPen, QFontMetrics, QMouseEvent
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog, QSpinBox, QComboBox, QGridLayout, QLabel, QHBoxLayout


class HistogramOrientation(Flag):
    LeftTop = 0
    LeftBottom = 1
    RightTop = 2
    RightBottom = 3
    TopLeft = 4
    TopRight = 5
    BottomLeft = 6
    BottomRight = 7

def isVertical(orientation: HistogramOrientation):
    return orientation & HistogramOrientation.TopLeft

class HistogramWidget(QWidget):
    def __init__(self, parent=None, bin_size=1, orientation=HistogramOrientation.LeftBottom):
        super().__init__(parent)

        self.histogram = None
        self.bin_size = bin_size
        self.orientation = orientation
        self.hovered_bin = -1
        self.logarithmic = False

        self.setMouseTracking(True)

    def setHistogram(self, histogram):
        self.histogram = histogram
        self.update()
    
    def setImage(self, image:QImage):
        self.histogram = self.calculateHistogram(image)
        self.update()

    def setLogarithmic(self, isLogarithmic:bool):
        self.logarithmic = isLogarithmic
        self.update()

    def calculateHistogram(self, image:QImage):
        histogram = [0] * 256

        for x in range(image.width()):
            for y in range(image.height()):
                color = QColor(image.pixel(x, y))
                gray_value = int(0.2126 * color.red() + 0.7152 *
                                 color.green() + 0.0722 * color.blue())
                histogram[gray_value] += 1

        return histogram

    def setBinSize(self, bin_size):
        self.bin_size = bin_size
        self.update()

    def setOrientation(self, orientation: HistogramOrientation):
        self.orientation = orientation
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.histogram is not None:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            #max_value = max(self.histogram)
            num_bins = (256 + self.bin_size - 1) // self.bin_size
            bin_sums = [sum(self.histogram[i * self.bin_size:min((i + 1) * self.bin_size, 256)]) for i in range(num_bins)]
            max_bin_sum = max(bin_sums)

            if isVertical(self.orientation):
                bar_width = max(1, self.height() // num_bins, 20)
                bin_height = self.width()
            else:
                bar_width = max(1, self.width() // num_bins)
                bin_height = self.height()

            if max_bin_sum > 0:
                for i, bin_sum in enumerate(bin_sums):
                    bin_start = i * self.bin_size
                    bin_end = min(bin_start + self.bin_size, 256)
                    bin_sum = sum(self.histogram[bin_start:bin_end])
                    if self.logarithmic:
                        value = (math.log(bin_sum + 1) / math.log(max_bin_sum + 1))
                    else:
                        value = (bin_sum / max_bin_sum)

                    if self.orientation == HistogramOrientation.LeftBottom:
                        x = i * bar_width
                        y = bin_height - value * bin_height
                    elif self.orientation == HistogramOrientation.LeftTop:
                        x = i * bar_width
                        y = value * bin_height
                    elif self.orientation == HistogramOrientation.TopLeft:
                        x = value * bin_height
                        y = i * bar_width
                    elif self.orientation == HistogramOrientation.TopRight:
                        x = bin_height - value * bin_height
                        y = i * bar_width
                    elif self.orientation == HistogramOrientation.BottomRight:
                        x = (num_bins - i - 1) * bar_width
                        y = value * bin_height
                    elif self.orientation == HistogramOrientation.RightBottom:
                        x = bin_height - value * bin_height
                        y = (num_bins - i - 1) * bar_width

                    rect = QRect(QPoint(int(x), int(y)), QPoint(int(x + bar_width - 1), int(bin_height)))
                    if i == self.hovered_bin:
                        painter.setBrush(Qt.GlobalColor.yellow)
                        painter.setPen(Qt.GlobalColor.yellow)
                    else:
                        painter.setBrush(Qt.GlobalColor.darkGreen)
                        painter.setPen(Qt.GlobalColor.darkGreen)
                    painter.drawRect(rect)

            if self.hovered_bin != -1:
                bin_start = self.hovered_bin * self.bin_size
                bin_end = min(bin_start + self.bin_size, 256)
                bin_sum = sum(self.histogram[bin_start:bin_end])

                if bin_start == bin_end - 1:
                    text = f"[{bin_start}]={bin_sum}"
                else:
                    text = f"[{bin_start}-{bin_end - 1}]={bin_sum}"
                font_metrics = QFontMetrics(painter.font())
                text_rect = font_metrics.boundingRect(
                    QRect(0, 0, self.width(), self.height()), Qt.TextFlag.TextWordWrap, text)

                painter.setPen(Qt.GlobalColor.black)
                painter.setBrush(Qt.GlobalColor.black)
                painter.drawRect(text_rect)

                painter.setPen(Qt.GlobalColor.white)
                painter.drawText(text_rect, Qt.TextFlag.TextWordWrap, text)
        painter.end()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.histogram is not None:
            num_bins = (256 + self.bin_size - 1) // self.bin_size
            bar_width = max(1, min(self.width() // num_bins, 20))
            bin_height = self.height() - 20

            if self.orientation in [HistogramOrientation.LeftBottom, HistogramOrientation.LeftTop]:
                self.hovered_bin = event.pos().x() // bar_width
            elif self.orientation in [HistogramOrientation.TopRight, HistogramOrientation.BottomRight]:
                self.hovered_bin = num_bins - event.pos().y() // bar_width - 1
            elif self.orientation == HistogramOrientation.TopLeft:
                self.hovered_bin = event.pos().y() // bar_width
            elif self.orientation == HistogramOrientation.RightBottom:
                self.hovered_bin = event.pos().x() // bar_width

            if 0 <= self.hovered_bin < num_bins:
                self.update()
            else:
                self.hovered_bin = -1

class GlcmWidget(QWidget):
    keys = ['contrast', 'dissimilarity', 'homogeneity', 'energy']
    def __init__(self, parent: QWidget | None = ...) -> None:
        super().__init__(parent)
        self._selectedChannel = 0 # contrast
        self._gridLayout = None
        self._setupUi()
    
    def _setupUi(self):
        if self._gridLayout is not None:
            self.deleteLater()
        mainLayout = QVBoxLayout()
        gridLayout = QGridLayout()
        mainLayout.addLayout(gridLayout)
        buttonsLayout = QHBoxLayout()
        self._buttons = [self._createRadioPushButton('C', 'Contrast', self._selectedChannel==0, self._setContrast),
            self._createRadioPushButton('D', 'Dissimilarity', self._selectedChannel==1, self._setDissimilarity),
            self._createRadioPushButton('H', 'Homogeneity', self._selectedChannel==2, self._setHomogeneity),
            self._createRadioPushButton('E', 'Energy', self._selectedChannel==3, self._setEnergy)]
        for button in self._buttons:
            buttonsLayout.addWidget(button)
        mainLayout.addLayout(buttonsLayout)
        self.setLayout(mainLayout)
        self._gridLayout = gridLayout
        

    def _createRadioPushButton(self, text, tooltip, isSelected, callback):
        button = QPushButton(text)
        button.setToolTip(tooltip)
        button.setCheckable(True)
        button.setChecked(isSelected)
        button.setAutoExclusive(True)
        button.toggled.connect(callback)
        return button

    def setData(self, data): # see data_filters.calcGlsm() for data format
        self._data = data
        self._updateData()
    
    def _updateData(self):
        key = self.keys[self._selectedChannel]
        distances = self._data[key]
        w = QLabel(key[0:1].upper())
        w.setMaximumHeight(20)
        w.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        ow = self._gridLayout.itemAtPosition(0, 0)
        if ow is None:
            self._gridLayout.addWidget(w, 0, 0)
        else:
            ow = self._gridLayout.replaceWidget(ow.widget(), w)
            ow.widget().deleteLater()

        values = []
        coords = []
        minValue = sys.float_info.max
        maxValue = 0.0
        for j, (distance, angles) in enumerate(distances.items()):
            w = QLabel(f'{distance}')
            w.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            w.setMaximumHeight(20)
            ow = self._gridLayout.itemAtPosition(0, j+1)
            if ow is None:
                self._gridLayout.addWidget(w, 0, j+1)
            else:
                ow = self._gridLayout.replaceWidget(ow.widget(), w)
                ow.widget().deleteLater()
            for i, (angle, value) in enumerate(angles.items()):
                if j == 0:
                    w = QLabel(f'{math.degrees(angle):g}°')
                    w.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
                    w.setMaximumHeight(20)
                    # self._gridLayout.addWidget(w, i+1, 0)
                    ow = self._gridLayout.itemAtPosition(i+1, 0)
                    if ow is None:
                        self._gridLayout.addWidget(w, i+1, 0)
                    else:
                        ow = self._gridLayout.replaceWidget(ow.widget(), w)
                        ow.widget().deleteLater()

                value = value[0]
                w = QLabel(f'{value:.2f}')
                w.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
                w.setMaximumHeight(20)
                w.setToolTip(f'{value}')
                #self._gridLayout.addWidget(w, i+1, j+1)
                ow = self._gridLayout.itemAtPosition(i+1, j+1)
                if ow is None:
                    self._gridLayout.addWidget(w, i+1, j+1)
                else:
                    ow = self._gridLayout.replaceWidget(ow.widget(), w)
                    ow.widget().deleteLater()
                coords.append((i+1, j+1))
                values.append(value)
                if maxValue < value:
                    maxValue = value
                if minValue > value:
                    minValue = value
        indices = np.argsort(values)
        spread = maxValue - minValue
        if spread < 0.2:
            spread *= 3
        elif spread < 0.5:
            spread *= 2
        for index in indices:
            pos = coords[index]
            value = values[index]
            value = (value - minValue) / spread
            c1 = int(value * 192)
            # c2 = int((1.0 - value) * 192)
            c2 = 0
            self._gridLayout.itemAtPosition(pos[0],pos[1]).widget().setStyleSheet(f'background-color: #{c1:02x}00{c2:02x}')

    def _setContrast(self, isChecked):
        if isChecked:
            self._selectedChannel = 0
            self._updateData()

    def _setDissimilarity(self, isChecked):
        if isChecked:
            self._selectedChannel = 1
            self._updateData()

    def _setHomogeneity(self, isChecked):
        if isChecked:
            self._selectedChannel = 2
            self._updateData()

    def _setEnergy(self, isChecked):
        if isChecked:
            self._selectedChannel = 3
            self._updateData()
