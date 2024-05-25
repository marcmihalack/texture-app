import math
from PyQt6.QtWidgets import (QGraphicsView, QGraphicsScene, QGraphicsRectItem, QApplication, QGraphicsItem, QGraphicsEllipseItem, QAbstractGraphicsShapeItem)
from PyQt6.QtGui import QPixmap, QPen, QColor, QPainter, QCursor, QBrush, QImage
from PyQt6.QtCore import Qt, QPointF, QRectF, pyqtSignal, QSize, QSizeF
import numpy as np
import enum
import cv2
from PIL import Image
from skimage.color import rgb2gray
from skimage.io import imread,imsave
from skimage.util import img_as_float, img_as_ubyte
from skimage.restoration import inpaint

DRAW_NORMAL = 0
DRAW_HIGHLIGHT = 1
DRAW_SELECTED = 2

class ShapeType(enum.IntEnum):
    SQUARE = 0
    CIRCLE = 1
        
class ShapeRegion:
    def __init__(self, shape:ShapeType, center:QPointF, rect:QRectF, size:int) -> None:
        self._shape = shape
        self._size = size
        self._center = center
        self._rect = rect
    
    def size(self):
        return self._size
    
    def rect(self):
        return self._rect
    
    def setCenter(self, center:QPointF):
        self._center = center
    
    def shape(self):
        return self._shape
    
    def getCoords(self):
        return (self._center.x(), self._center.y(), self._size)

class SelectRegionWidget(QGraphicsView):
    def __init__(self, region_shape:ShapeType, region_size=(256, 256), parent=None):
        super().__init__(parent)
        self.image_path = None
        self._image_regions = None
        self._region_size = region_size
        self._region_shape = region_shape
        self.setMouseTracking(True)
        self._show_all_regions = True

        self.setScene(QGraphicsScene())
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._dragging = False
        self._selecting = False
        self._creating = False
        self._shadow_item = None
        self._drag_offset = QPointF()


    def setShowAllRegions(self, show_all):
        self._show_all_regions = show_all
        self._updateRegions()


    def getShowAllRegions(self):
        return self._show_all_regions


    def refreshImage(self, improveImage: bool):
        # if improveImage:
        #     image = cv2.imread(self.image_path)
        #     image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        #     lower_white = np.array([255, 255, 255])
        #     upper_white = np.array([255, 255, 255])
        #     #mask = cv2.inRange(image, lower_white, upper_white)
        #     white_intensity = 255
        #     _, mask = cv2.threshold(image, white_intensity-1, white_intensity, cv2.THRESH_BINARY)
        #     result = cv2.inpaint(image, mask, inpaintRadius=1, flags=cv2.INPAINT_NS)
        if improveImage:
            img = imread(self.image_path)
            height, width = img.shape
            #img = img_as_float(img)  # ensure the image is a float array
            # gray_img = rgb2gray(img)
            gray_img = img

            # Define the mask - white pixels are True, others are False
            #mask = gray_img >= 0.99
            mask = gray_img >= 250
            # mask = img_as_ubyte(mask)
            Image.fromarray(mask).convert('L').save(self.image_path+'-mask.jpg')
            # Perform image inpainting
            result = inpaint.inpaint_biharmonic(img, mask)
            result = Image.fromarray(result)
            result.convert('L').save(self.image_path+'-inpaint.jpg')
        else:
            #image = cv2.imread(self.image_path)
            #image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            result = imread(self.image_path)
            height, width = result.shape
        # result = Image.fromarray(result)
        bytesPerLine = 1 * width
        qImg = QImage(result.data, width, height, bytesPerLine, QImage.Format.Format_Grayscale8)
        pixmap = QPixmap.fromImage(qImg)
        # pixmap = QPixmap(self.image_path)
        if pixmap.width() != 1280:
            pixmap = pixmap.scaled(
                1280, 960, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
        self.scene().addPixmap(pixmap)
        return pixmap

    def loadImage(self, image_path, regions, improveImage: bool=True):
        scene = self.scene()
        for item in scene.items():
                scene.removeItem(item)
        self.image_path = image_path

        self._image_regions = {}
        if regions:
            for regionId, region in enumerate(regions):
                self._image_regions[regionId] = region

        pixmap = self.refreshImage(improveImage)
        self.setSceneRect(QRectF(pixmap.rect()))
        if regions:
            widget_region_size = QSizeF(self._region_size[0], self._region_size[1])
            for regionId, region in enumerate(regions):
                if self._show_all_regions or widget_region_size == region.size():
                    self._addRegionToScene(region, regionId)


    def setRegionSize(self, size):
        self._region_size = size
        self._updateRegions()

    def setRegionShape(self, shape: ShapeType):
        self._region_shape = shape
        self._updateRegions()
    
    def _updateRegions(self):
        scene = self.scene()
        for item in scene.items():
            if isinstance(item, QAbstractGraphicsShapeItem):
                scene.removeItem(item)
        if self._image_regions:
            widget_region_size = QSizeF(self._region_size[0], self._region_size[1])
            for regionId, region in self._image_regions.items():
                if self._show_all_regions or widget_region_size == region.size():
                    self._addRegionToScene(region, regionId)


    def deleteAllRegions(self):
        scene = self.scene()
        self._image_regions = {}
        for item in scene.items():
            if isinstance(item, QAbstractGraphicsShapeItem):
                scene.removeItem(item)

    def _createFittedRect(self, shape:ShapeType, center:QPointF, size):
        actualSize = size if shape == ShapeType.SQUARE else size * math.sqrt(2)
        halfSize = actualSize / 2
        x = center.x() - halfSize
        y = center.y() - halfSize
        if x < 0:
            x = 0
        if y < 0:
            y = 0
        selfRight = self.sceneRect().right()
        if x + actualSize >= selfRight:
            x = selfRight - actualSize - 1
        selfBottom = self.sceneRect().bottom()
        if y + actualSize >= selfBottom:
            y = selfBottom - actualSize - 1
        return QRectF(x, y, actualSize, actualSize)

    def _createShapeRegion(self, shape, center, size):
        rect = self._createFittedRect(shape, center, size)
        return ShapeRegion(shape, center, rect, size)

    def _getRegionColor(self, region_size:int):
        match region_size:
            case 256: return QColor(0, 255, 0)
            case 320: return QColor(255, 0, 0)
            case 384: return QColor(255, 255, 0)
        return QColor(128,128,128)
            
    def _addRegionToScene(self, region: ShapeRegion, regionId) -> QAbstractGraphicsShapeItem:
        region_rect = region.rect()
        if(region.shape() == ShapeType.CIRCLE):
            region_item = QGraphicsEllipseItem(region_rect)
        else:
            region_item = QGraphicsRectItem(region_rect)
        region_item.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
                             QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        region_item._regionId = regionId
        color = self._getRegionColor(region.size())
        region_item.setPen(QPen(color, 1))
        brush_color = color
        brush_color.setAlpha(50)
        region_item.setBrush(QBrush(brush_color))
        self.scene().addItem(region_item)
        return region_item

    def getRegions(self):
        regions = [r for r in self._image_regions.values()]
        # for item in self.scene().items():
        #     if isinstance(item, QGraphicsRectItem):
        #         regions.append(item.rect())
        return regions

    def mousePressEvent(self, event):
        item = self.itemAt(event.position().toPoint())
        modifiers = QApplication.keyboardModifiers()

        if event.button() == Qt.MouseButton.LeftButton:
            if item != self._shadow_item and item and isinstance(item, QAbstractGraphicsShapeItem):
                if modifiers == Qt.KeyboardModifier.NoModifier:
                    self._dragging = True
                    self._drag_offset = self.mapToScene(event.position().toPoint())
                    self.scene().clearSelection()
                    item.setSelected(True)
                elif modifiers == Qt.KeyboardModifier.ControlModifier:
                    item.setSelected(not item.isSelected())
                elif modifiers == (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier):
                    if item._regionId >= 0:
                        del self._image_regions[item._regionId]
                    self.scene().removeItem(item)
            # no item hit
            elif modifiers == Qt.KeyboardModifier.ShiftModifier:
                event_pos = event.position().toPoint()
                pos = self.mapToScene(event_pos)
                self.scene().clearSelection()
                regionId = len(self._image_regions.keys())
                #x = self._region_size[0] if self._region_shape == ShapeType.SQUARE else self._region_size[0] * math.sqrt(2)
                # region_rect = self._createFittedRect(pos.x() - x/2, pos.y() - x/2, x, x)
                ## region = ShapeRegion(self._region_shape, region_rect)
                region = self._createShapeRegion(self._region_shape, pos, self._region_size[0])
                self._image_regions[regionId] = region
                self._addRegionToScene(region, regionId).setSelected(True)
            elif modifiers == Qt.KeyboardModifier.NoModifier:
                self._dragging = True
                self._drag_offset = self.mapToScene(event.position().toPoint())
        # elif event.button() == Qt.MouseButton.LeftButton and modifiers == (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier):
        #     if item and isinstance(item, QGraphicsRectItem):
        #         self.scene().removeItem(item)

    def mouseMoveEvent(self, event):
        if self._dragging:
            for item in self.scene().selectedItems():
                new_pos = self.mapToScene(
                    event.position().toPoint())
                pt = new_pos - self._drag_offset
                item.moveBy(pt.x(), pt.y())
                self._drag_offset = new_pos
        if self._creating:
            if self._shadow_item:
                event_pos = event.position().toPoint()
                pos = self.mapToScene(event_pos)
                rect = self._createFittedRect(self._region_shape, pos, self._region_size[0])

                self._shadow_item.setRect(rect)
        elif self._shadow_item:
            self.scene().removeItem(self._shadow_item)
            self._shadow_item = None


    def mouseReleaseEvent(self, event):
        if self._dragging:
            self._dragging = False
            # if self._show_all_regions:
            #     regions = []
            #     size_to_remove = self._region_size[0]
            #     for r in self._image_regions:
            #         if r.width() != size_to_remove:
            #             regions.append(r)
            # else:
            #     regions = self._image_regions.copy()

            for item in self.scene().selectedItems():
                if isinstance(item, QAbstractGraphicsShapeItem):
                    regionId = item._regionId
                    if regionId >= 0:
                        rect = item.rect()
                        rect.moveTopLeft(rect.topLeft() + item.scenePos())
                        print('MOVED', regionId, rect)
                        self._image_regions[regionId].setCenter(rect.center())
            
        super().mouseReleaseEvent(event)

    def handleMoveSelected(self, event) -> bool:
        modifiers = event.modifiers()
        if (modifiers & Qt.KeyboardModifier.AltModifier) == Qt.KeyboardModifier.AltModifier:
            offset = 1
        elif (modifiers & Qt.KeyboardModifier.ControlModifier) == Qt.KeyboardModifier.ControlModifier:
            offset = 5
        else:
            offset = 20
        dx = 0
        dy = 0
        print('OFFSET', offset)
        if event.key() == Qt.Key.Key_Left:
            dx = -offset
        elif event.key() == Qt.Key.Key_Right:
            dx = offset
        elif event.key() == Qt.Key.Key_Up:
            dy = -offset
        elif event.key() == Qt.Key.Key_Down:
            dy = offset
        else:
            return False
        for item in self.scene().selectedItems():
            if isinstance(item, QAbstractGraphicsShapeItem):
                regionId = item._regionId
                if regionId >= 0:
                    item.moveBy(dx, dy)
                    rect = item.rect()
                    rect.moveTopLeft(rect.topLeft() + item.scenePos())
                    print('MOVED', regionId, rect)
                    self._image_regions[regionId].setCenter(rect.center())
        return True


    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Shift:
            if self.underMouse():
                self.setFocus()
                self._creating = True
                cursor_pos = self.mapFromGlobal(QCursor.pos())
                pos = self.mapToScene(cursor_pos)
                region_rect = self._createFittedRect(self._region_shape, pos, self._region_size[0])
                if self._region_shape == ShapeType.CIRCLE:
                    region_item = QGraphicsEllipseItem(region_rect)
                else:
                    region_item = QGraphicsRectItem(region_rect)
                region_item.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
                                    QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
                color = self._getRegionColor(self._region_size[0])
                color.setAlpha(50)
                region_item.setPen(QPen(color, 1))
                region_item.setBrush(QBrush(color))
                self._shadow_item = region_item
                self.scene().addItem(region_item)

            self.setCursor(QCursor(Qt.CursorShape.CrossCursor))
        
        elif event.key() == Qt.Key.Key_Left:
            self.handleMoveSelected(event)
        elif event.key() == Qt.Key.Key_Right:
            self.handleMoveSelected(event)
        elif event.key() == Qt.Key.Key_Up:
            self.handleMoveSelected(event)
        elif event.key() == Qt.Key.Key_Down:
            self.handleMoveSelected(event)

        elif event.key() == Qt.Key.Key_Delete:
            for item in self.scene().selectedItems():
                if isinstance(item, QAbstractGraphicsShapeItem):
                    if item._regionId >= 0:
                        del self._image_regions[item._regionId]
                    self.scene().removeItem(item)

        elif event.key() == Qt.Key.Key_N and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if self.underMouse():
                pos = self.mapFromGlobal(QCursor.pos())
                scene_pos = self.mapToScene(pos)
            else:
                scene_pos = QPointF(0, 0)
            x = self._region_size[0] if self._region_shape == ShapeType.SQUARE else self._region_size[0] * math.sqrt(2)
            regionId = len(self._image_regions.keys())
            #region_rect = self._createFittedRect(scene_pos.x(), scene_pos.y(), x, x)
            #self._image_regions[regionId] = ShapeRegion(self._region_shape, region_rect)
            self._image_regions[regionId] = self._createShapeRegion(self._region_shape, scene_pos, self._region_size[0])
            self._addRegionToScene(region_rect, regionId).setSelected(True)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key.Key_Shift:
            if self._shadow_item:
                self.scene().removeItem(self._shadow_item)
                self._shadow_item = None
            self._creating = False
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        super().keyReleaseEvent(event)


