import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QGraphicsScene,
                             QGraphicsView, QGraphicsItem, QGraphicsLineItem, QGraphicsPixmapItem)
from PyQt6.QtGui import (QImage, QPixmap, QPainter, QPen, QColor, QCursor, QMouseEvent, QKeyEvent,
                         QPainterPath, QPainterPathStroker)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QPointF, QLineF
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PIL import Image
import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt


class ImageViewer(QGraphicsView):
    crossingModified = pyqtSignal(bool, bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setScene(QGraphicsScene(self))
        self.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        self.lineA = None
        self.lineB = None
        self.image_arr = None
        self.draggingLines = [0, 0]

    def is_on_line(self, point, line) -> bool:
        if line is None:
            return False
        else:
            path = QPainterPath()
            path.moveTo(line.line().p1())
            path.lineTo(line.line().p2())
            stroker = QPainterPathStroker()
            stroker.setWidth(self.mouseSensitivity)  # line vicinity in pixels
            return stroker.createStroke(path).contains(point)

    mouseSensitivity = 10
    def mousePressEvent(self, event: QMouseEvent):
        if self.image_arr is not None:
            pos = self.mapToScene(event.position().toPoint())
            if abs(pos.y() - self.lineA.line().p1().y()) <= 5 and abs(pos.x() - self.lineA.line().p1().x()) <= self.mouseSensitivity:
                self.draggingLines[0] = 1
            elif abs(pos.y() - self.lineA.line().p2().y()) <= 5 and abs(pos.x() - self.lineA.line().p2().x()) <= self.mouseSensitivity:
                self.draggingLines[0] = 2
            elif self.is_on_line(pos, self.lineA):
                self.draggingLines[0] = 3
            else:
                self.draggingLines[0] = 0

            if abs(pos.x() - self.lineB.line().p1().x()) <= 5 and abs(pos.y() - self.lineB.line().p1().y()) <= self.mouseSensitivity:
                self.draggingLines[1] = 1
            elif abs(pos.x() - self.lineB.line().p2().x()) <= 5 and abs(pos.y() - self.lineB.line().p2().y()) <= self.mouseSensitivity:
                self.draggingLines[1] = 2
            elif self.is_on_line(pos, self.lineB):
                self.draggingLines[1] = 3
            else:
                self.draggingLines[1] = 0
        self.previousMousePos = self.mapToScene(event.position().toPoint())

        super().mousePressEvent(event)

    def _boundX(self, x:float):
        if x < 0:
            return 0
        elif x > self._imageWidth:
            return self._imageWidth
        return x

    def _boundY(self, y:float):
        if y < 0:
            return 0
        elif y > self._imageHeight:
            return self._imageHeight
        return y

    def _boundXY(self, point:QPointF):
        return QPointF(self._boundX(point.x()), self._boundY(point.y()))

    def resizeEvent(self, event):
        self.fitInView(self.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        super().resizeEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        new_pos = self.mapToScene(event.position().toPoint())

        if self.draggingLines[0] in [1, 2, 3]:
            line = self.lineA.line()
            new_y = np.clip(new_pos.y(), 0, self.imageHeight())
            if self.draggingLines[0] == 1:
                line.setP1(QPointF(0, new_y))
            elif self.draggingLines[0] == 2:
                line.setP2(QPointF(self.imageWidth(), new_y))
            elif self.draggingLines[0] == 3:
                line = self.lineA.line()
                delta_y = new_pos.y() - self.previousMousePos.y()
                new_p1_y = np.clip(line.p1().y() + delta_y, 0, self.image_arr.shape[0])
                new_p2_y = np.clip(line.p2().y() + delta_y, 0, self.image_arr.shape[0])
                line.setP1(QPointF(0, new_p1_y))
                line.setP2(QPointF(self.image_arr.shape[1], new_p2_y))
                self.lineA.setLine(line)
            # elif self.draggingLines[0] == 3:
            #     delta_y = new_y - self.previousMousePos.y()
            #     p1 = QPointF(0, np.clip(line.p1().y() + delta_y, 0, self.imageHeight()))
            #     p2 = QPointF(self.imageWidth(), np.clip(line.p2().y() + delta_y, 0, self.imageHeight()))
            #     line.setP1(p1)
            #     line.setP2(p2)
                #delta_y = new_y - self.previousMousePos.y()
                #line.translate(0, delta_y)
            self.lineA.setLine(line)
            lineAmodified = True
        else:
            lineAmodified = False

        if self.draggingLines[1] in [1, 2, 3]:
            line = self.lineB.line()
            new_x = np.clip(new_pos.x(), 0, self.imageWidth())
            if self.draggingLines[1] == 1:
                line.setP1(QPointF(new_x, 0))
            elif self.draggingLines[1] == 2:
                line.setP2(QPointF(new_x, self.imageHeight()))
            elif self.draggingLines[1] == 3:
                line = self.lineB.line()
                delta_x = new_pos.x() - self.previousMousePos.x()
                new_p1_x = np.clip(line.p1().x() + delta_x, 0, self.image_arr.shape[1])
                new_p2_x = np.clip(line.p2().x() + delta_x, 0, self.image_arr.shape[1])
                line.setP1(QPointF(new_p1_x, 0))
                line.setP2(QPointF(new_p2_x, self.image_arr.shape[0]))
                self.lineB.setLine(line)                
            # elif self.draggingLines[1] == 3:
            #     delta_x = new_x - self.previousMousePos.x()
            #     line.translate(delta_x, 0)
            self.lineB.setLine(line)
            lineBmodified = True
        else:
            lineBmodified = False

        self.previousMousePos = new_pos
        if lineAmodified or lineBmodified:
            self.crossingModified.emit(lineAmodified, lineBmodified)
        super().mouseMoveEvent(event)
        self.update()

    def imageWidth(self):
        return self.image_arr.shape[1] if self.image_arr is not None else 0

    def imageHeight(self):
        return self.image_arr.shape[0] if self.image_arr is not None else 0

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.draggingLines = [0, 0]
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event: QKeyEvent):
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent):
        super().keyReleaseEvent(event)

    def set_image(self, imagePath: str):
        self.scene().clear()

        image_arr = Image.open(imagePath).convert('RGB')
        data = image_arr.tobytes("raw", "RGB")
        qimage = QImage(data, image_arr.width,
                        image_arr.height, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
        self.scene().addItem(QGraphicsPixmapItem(pixmap))
        midpoint = QPointF(image_arr.width / 2, image_arr.height / 2)
        self.lineA = self.scene().addLine(QLineF(QPointF(0, midpoint.y()), QPointF(image_arr.width, midpoint.y())), QPen(Qt.GlobalColor.red, 2))
        self.lineB = self.scene().addLine(QLineF(QPointF(midpoint.x(), 0), QPointF(midpoint.x(), image_arr.height)), QPen(Qt.GlobalColor.green, 2))
        self.image_arr = np.array(image_arr)
        
        self.draggingLines = [0, 0]
        self.previousMousePos = QPointF()

        self.fitInView(self.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
    
    def _get_line_pixel_values(self, line: QLineF, vertical=False):
        if vertical:  # Interpolate along y-axis for lineB
            y = np.arange(self.imageHeight())
            slope = (line.p2().x() - line.p1().x()) / (line.p2().y() - line.p1().y())
            x = slope * (y - line.p1().y()) + line.p1().x()
        else:  # Interpolate along x-axis for lineA
            x = np.arange(self.imageWidth())
            slope = (line.p2().y() - line.p1().y()) / (line.p2().x() - line.p1().x())
            y = slope * (x - line.p1().x()) + line.p1().y()

        # Collect the pixel values along the line
        pixel_values = []
        for x_val, y_val in zip(x, y):
            if (0 <= x_val < self.imageWidth()) and (0 <= y_val < self.imageHeight()):
                pixel_values.append(self.image_arr[int(y_val), int(x_val)])

        return pixel_values

    def get_line_pixel_values(self):
        lineA_values = self._get_line_pixel_values(self.lineA.line())
        lineB_values = self._get_line_pixel_values(self.lineB.line(), vertical=True)
        return lineA_values, lineB_values

class ImageCrossingWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.image_viewer = ImageViewer()
        plt.style.use('dark_background')
        plt.rcParams['font.size'] = 8
        # Create the figure and two subplots for Matplotlib
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(6, 4))
        self.ax1.figure.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
        self.ax2.figure.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
        #self.ax1.figure.tight_layout()
        #self.ax2.figure.tight_layout()
        #self.ax1.set_title('LineA Pixel Values')
        #self.ax2.set_title('LineB Pixel Values')

        # Create a FigureCanvas to display the Matplotlib figure
        self.canvas = FigureCanvas(self.fig)
        # self.toolbar = NavigationToolbar(self.canvas, self)

        layout = QVBoxLayout()
        layout.addWidget(self.image_viewer)
        layout.addWidget(self.canvas)
        
        self.setLayout(layout)
        
        self.image_viewer.crossingModified.connect(self.update_plots)

    def update_plots1(self, updateAx1: bool=True, updateAx2: bool=True):
        self.ax1.clear()
        self.ax2.clear()

        lineA = self.image_viewer.lineA.line()
        lineB = self.image_viewer.lineB.line()

        # Bresenham's line algorithm to extract pixel values along the line
        # Plot lineA
        y_values_lineA = []
        for x in range(self.image_viewer.image_arr.shape[1]):
            y = int(lineA.pointAt(x / self.image_viewer.image_arr.shape[1]).y())
            y_values_lineA.append(self.image_viewer.image_arr[y, x])
        self.ax1.plot(y_values_lineA, color='white')

        # Plot lineB
        x_values_lineB = []
        for y in range(self.image_viewer.image_arr.shape[0]):
            x = int(lineB.pointAt(y / self.image_viewer.image_arr.shape[0]).x())
            x_values_lineB.append(self.image_viewer.image_arr[y, x])
        self.ax2.plot(x_values_lineB, color='white')

        # Styling plots
        self.ax1.xaxis.tick_top()
        self.ax2.xaxis.tick_bottom()
        for ax in (self.ax1, self.ax2):
            ax.set_facecolor('black')
            ax.tick_params(axis='x', colors='white')
            ax.tick_params(axis='y', colors='white')
            ax.spines['bottom'].set_color('white')
            ax.spines['top'].set_color('white')
            ax.spines['right'].set_color('white')
            ax.spines['left'].set_color('white')
            ax.label.set_color('white')
            ax.title.set_color('white')
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')
            ax.tick_params(axis='both', which='major', labelsize=6)
            ax.grid(False)

        self.canvas.draw()
        
    def update_plots(self, updateAx1: bool=True, updateAx2: bool=True):
        self.ax1.clear()
        self.ax2.clear()
        
        # Get the pixel values along the lines from the image viewer
        lineA_values, lineB_values = self.image_viewer.get_line_pixel_values()
        
        # Plot the pixel values along each line
        self.ax1.plot(lineA_values, color='#FF8080', lw=0.1)
        self.ax2.plot(lineB_values, color='lightgreen', lw=0.1)
        
        self.canvas.draw()
        
    @pyqtSlot(str)
    def loadFile(self, imagePath):
        #image = Image.open(imagePath).convert('RGB')
        #self.image_viewer.set_image(image)
        self.image_viewer.set_image(imagePath)
        self._imagePath = imagePath
        self.update_plots()


class ImageCrossingWidget1(QWidget):
    def __init__(self, image=None, parent=None):
        super().__init__(parent)

        plt.style.use('dark_background')
        plt.rcParams['font.size'] = 8

        self.image_viewer = ImageViewer(self)
        self.image_viewer.crossingModified.connect(self.crossingModified)

        self.h_layout = QHBoxLayout(self)
        self.v_layout = QVBoxLayout()

        self.ax1 = FigureCanvas(Figure())
        self.ax2 = FigureCanvas(Figure())

        self.h_layout.addWidget(self.image_viewer)
        self.h_layout.addLayout(self.v_layout)
        self.v_layout.addWidget(self.ax1)
        self.v_layout.addWidget(self.ax2)

    @pyqtSlot(bool, bool)
    def crossingModified(self, aModified, bModified):
        self.update_plots()

    @pyqtSlot(str)
    def loadFile(self, imagePath):
        #image = Image.open(imagePath).convert('RGB')
        #self.image_viewer.set_image(image)
        self.image_viewer.set_image(imagePath)
        self._imagePath = imagePath
        self.update_plots()

    def update_plots(self):
        self.ax1.figure.clear()
        self.ax2.figure.clear()

        lineA = self.image_viewer.lineA.line()
        lineB = self.image_viewer.lineB.line()

        # Bresenham's line algorithm
        # Plot lineA
        y_values_lineA = []
        for x in range(self.image_viewer.image_arr.shape[1]):
            y = int(lineA.pointAt(x / self.image_viewer.image_arr.shape[1]).y())
            y_values_lineA.append(self.image_viewer.image_arr[y, x])
        self.ax1.plot(y_values_lineA, color='white')

        # Plot lineB
        x_values_lineB = []
        for y in range(self.image_viewer.image_arr.shape[0]):
            x = int(lineB.pointAt(y / self.image_viewer.image_arr.shape[0]).x())
            x_values_lineB.append(self.image_viewer.image_arr[y, x])
        self.ax2.plot(x_values_lineB, color='white')

        # Styling
        self.ax1.xaxis.tick_top()
        self.ax2.xaxis.tick_bottom()
        for ax in (self.ax1, self.ax2):
            ax.set_facecolor('black')
            ax.tick_params(axis='x', colors='white')
            ax.tick_params(axis='y', colors='white')
            ax.spines['bottom'].set_color('white')
            ax.spines['top'].set_color('white')
            ax.spines['right'].set_color('white')
            ax.spines['left'].set_color('white')
            ax.label.set_color('white')
            ax.title.set_color('white')
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')
            ax.tick_params(axis='both', which='major', labelsize=6)
            ax.grid(False)

        self.canvas.draw()
