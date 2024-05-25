import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QMenu
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QEvent
from PyQt6 import QtCore, QtGui
import PyQt6.QtCore as QtCore
from PIL import Image, ImageQt

from log import ConsoleLog as log

class ImageFilesWidget(QListWidget):
    file_selected = pyqtSignal(str)
    file_activated = pyqtSignal(str)
    # file_hovered = pyqtSignal(str, bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.files = {}
        self.currentItemChanged.connect(self._select_file)
        self.itemActivated.connect(self._activate_file)
        # self.itemEntered.connect(self.__showTooltip)
        # self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.installEventFilter(self)

    # @QtCore.pyqtSlot(QListWidgetItem)
    # def __showToolTip(self, item: QListWidgetItem):
    #     path = item.text()
    #     item.setToolTip(path)
        

    def eventFilter(self, object: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.Type.ContextMenu and object is self:
            pos = event.pos()
            item = self.itemAt(pos)
            # if item:
            #     menu = QMenu()
            #     text = item.text()
            #     log.info(f'menu: {item} pos={pos}')
            #     menu.addAction('Rescan').triggered.connect(lambda: self.rescanImage(text))
            #     action = menu.exec(self.mapToGlobal(pos))
            #     QtGui.QAction
            #     log.info(f'ret: {action}')
            #     return True
        return super().eventFilter(object, event)
    
    def open_folder(self, folder_path):
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tif', '.tiff')):
                    self.open_file(os.path.join(root, file))

    def open_file(self, file_path):
        item = QListWidgetItem(self)
        item_text = '/'.join([os.path.basename(os.path.dirname(file_path)), os.path.basename(file_path)])
        item.file_path = file_path
        item.setText(item_text)
        item.setToolTip(file_path)
        self.addItem(item)

    def select_file(self, file_path):
        for selected_item in self.selectedIndexes():
            selected_file_path = selected_item.data()
            if selected_file_path == file_path:
                return
        items = self.findItems(file_path, Qt.MatchFlag.MatchExactly)
        for item in items:
            self.setCurrentItem(item)

    @QtCore.pyqtSlot(QListWidgetItem)
    def _select_file(self, item):
        if item is not None:
            self.file_selected.emit(item.file_path)

    @QtCore.pyqtSlot(QListWidgetItem)
    def _activate_file(self, item):
        if item is not None:
            self.file_activated.emit(item.file_path)
