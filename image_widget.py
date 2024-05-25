from PyQt6.QtWidgets import QLabel, QDialog
from PyQt6.QtGui import QPixmap, QFont
import PyQt6.QtCore as QtCore

from PyQt6.QtCore import QEvent, QObject, QRectF, QPointF, Qt, pyqtSignal, QLine, QPoint, QSize
from PyQt6.QtGui import QPainter, QPen, QColor, QTextOption, QPainterPath, QResizeEvent
from PIL import Image
from PIL.ImageQt import ImageQt

DRAW_NORMAL = 0
DRAW_INVALID = 1
DRAW_HIGHLIGHT = 2
DRAW_SELECTED = 4

class ImageWidget(QLabel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setScaledContents(False)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # self.setStyleSheet('background-color: black')
        self.file_path = None
        self.image_size = None
        self.image_scale = None
        self.image_offset = QPointF(0, 0)
        self.isResized = False
    
    @QtCore.pyqtSlot(str)
    def on_file_selected(self, file_path):
        self._load_image(file_path)

    @QtCore.pyqtSlot(str)
    def on_settings_changed(self, settings):
        self.settings = settings
        # settings = settings.get('image')
        # if settings is not None:
        #     self.drawBox = settings.get('drawbox', True)
        #     self.drawLandmarks = settings('drawlandmarks', False)
        # else:
        #     self.drawBox = True
        #     self.drawLandmarks = False
        self.update()

    def _load_image(self, image_path):
        self.file_path = image_path
        pixmap = QPixmap(image_path)
        self.image_size = pixmap.size()
        self.image_scale = self.imageScale()
        pixmap = pixmap.scaled(
            self.width(), self.height(),
            Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(pixmap)

        self.setMinimumSize(QSize(80, int(80 * self.image_size.height() / self.image_size.width())))
        self.update()

    def calculatePixmapOffset(self) -> QPointF:
        alignment = self.alignment()
        widget_size = self.size()
        image_size = self.pixmap().size()
        ha = alignment & Qt.AlignmentFlag.AlignHorizontal_Mask
        va = alignment & Qt.AlignmentFlag.AlignVertical_Mask
        if ha & Qt.AlignmentFlag.AlignHCenter:
            x = (widget_size.width() - image_size.width()) / 2.0
        elif ha & Qt.AlignmentFlag.AlignRight:
            x = widget_size.width() - image_size.width()
        else:
            x = 0
        if va & Qt.AlignmentFlag.AlignVCenter:
            y = (widget_size.height() - image_size.height()) / 2.0
        elif va & Qt.AlignmentFlag.AlignBottom:
            y = widget_size.height() - image_size.height()
        else:
            y = 0
        return QPointF(x,y)

    def resizeComplete(self):
        if self.isResized:
            pixmap = self.pixmap()
            if pixmap and not pixmap.isNull():
                pixmap = QPixmap(self.file_path).scaled(
                    self.width(), self.height(),
                    Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.setPixmap(pixmap)
            self.isResized = False
            self.image_scale = self.imageScale()

    def resizeEvent(self, event: QResizeEvent):
        pixmap = self.pixmap()
        if pixmap and not pixmap.isNull():
            pixmap = pixmap.scaled(
                self.width(), self.height(),
                Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.setPixmap(pixmap)
            self.isResized = True

    def imageScale(self):
        image_size = self.image_size
        widget_size = self.size()
        scale = min(widget_size.width() / image_size.width(), widget_size.height() / image_size.height()) # * self.current_zoom
        return scale

    def paintEvent(self, event):
        super().paintEvent(event)

        if not self.file_path:
            return

        painter = QPainter(self)
        self.image_offset = self.calculatePixmapOffset()

        pens = [
            QPen(QColor(192, 0, 0), 2) # normal
            , QPen(QColor(96, 96, 96), 2) # invalid
            , QPen(QColor(255, 0, 0), 2) # normal | highlight
            , QPen(QColor(192, 192, 192), 2) # invalid | hightlight
            , QPen(QColor(192, 192, 0), 2)  # normal | selected
            , QPen(QColor(255, 255, 255), 2)  # invalid | selected
            , QPen(QColor(255, 255, 0), 2)  # normal | highlight | selected
            , QPen(QColor(255, 255, 255), 2)  # invalid | hightlight | selected
        ]
        font = QFont()
        font.setFamily('Helvetica')
        font.setBold(True)
        font.setPointSize(10)
        painter.setFont(font)

        scale = self.imageScale()
        painter.end()

    def landmark_to_widget_points(self, landmark, scale: float):
        points = []
        for point in landmark:
            points.append(QPointF(point[0] * scale, point[1] * scale) + self.image_offset)
        return points

    def image_rect_to_widget_rect(self, image_rect: QRectF, scale: float):
        image_rect = QRectF(image_rect.topLeft() * scale + self.image_offset, image_rect.size() * scale)

        return image_rect
