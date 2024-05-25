from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QListWidget,
                             QListWidgetItem, QListView, QLineEdit, QGridLayout, QSizePolicy, QTableWidget)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
import PyQt6.QtCore as QtCore
from PyQt6 import QtGui
from PIL import Image, ImageQt
from histogram_widget import HistogramWidget, HistogramOrientation, GlcmWidget
import filters as f
import image_filters as fi
import data_filters as di

class PipelineItemWidget(QWidget):
    item_selected = pyqtSignal(str)
    item_activated = pyqtSignal(str)

    def __init__(self, parent=None, filter:f.Filter=None):
        super().__init__(parent)
        layout = QVBoxLayout()

        self.name_textbox = QLineEdit(self)
        self.name_textbox.setText(filter.name())
        self.name_textbox.setFixedHeight(20)
        self.name_textbox.setToolTip('Filter name')
        self.name_textbox.setReadOnly(True)
        layout.addWidget(self.name_textbox)

        self.list_widget = QListWidget()
        self.list_widget.setFlow(QListView.Flow.TopToBottom)
        #self.list_widget.setStyleSheet('background-color: #404005')
        layout.addWidget(self.list_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.setLayout(layout)

    # def addItemToView(self, frame:f.Frame):
    #     item_widget = ImageItemWidget(self, image, image_name)
    #     item = QListWidgetItem(self.list_widget)
    #     item.setSizeHint(QSize(200, 220))
    #     self.list_widget.addItem(item)
    #     self.list_widget.setItemWidget(item, item_widget)


class FilterItemWidget(QWidget):
    button1_clicked = pyqtSignal()
    button2_clicked = pyqtSignal()
    button3_clicked = pyqtSignal()
    button4_clicked = pyqtSignal()

    def __init__(self, parent=None, widget:QWidget=None, filter: f.Filter=None, frame: f.Frame=None):
        super().__init__(parent)

        layout = QVBoxLayout()

        # self.setStyleSheet('background-color: #500010')
        layout.addStretch()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self._main_label = widget

        layout.addWidget(
            self._main_label, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)

        self.name_textbox = QLineEdit(self)
        self.name_textbox.setText(f'{filter.name()}')
        self.name_textbox.setFixedHeight(20)
        # self.name_textbox.setToolTip('')
        self.name_textbox.setReadOnly(True)
        layout.addWidget(self.name_textbox)

        self.setLayout(layout)

class PipelineWidget(QScrollArea):
    item_selected = pyqtSignal(str)
    item_activated = pyqtSignal(str)

    def __init__(self, parent=None, pipeline:f.Pipeline=None, settings=None):
        super().__init__(parent)
        # layout = QVBoxLayout()
        #scroll = QScrollArea(self)
        self.setWidgetResizable(True)
        self.main_widget = QWidget()
        layout = QGridLayout()
        self.main_widget.setLayout(layout)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding))
        #self.list_widget = QListWidget()
        #self.list_widget.setFlow(QListView.Flow.LeftToRight)
        # self.setStyleSheet('background-color: #104040')
        #self.list_widget.setWrapping(True)
        #layout.addWidget(self.list_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)

        self.setWidget(self.main_widget)
        #self.setLayout(layout)
        self._layout = layout

        self.settings = settings

        self.pipeline = defaultPipeline(self) if pipeline is None else pipeline
        self._columnRows = []
        # self.layout = QHBoxLayout()
        # self.list_widget.setLayout(self.layout)
        #self.list_widget.currentItemChanged.connect(self.on_item_selected)
        #self.list_widget.itemActivated.connect(self.on_item_activated)

    def _on_filter_executing(self, filter: f.Filter, inputFrame: f.Frame):
        # self._addItemToView(filter)
        self._addFilterView(filter)

    def _on_histogram_filter_executed(self, filter:f.Filter, outputFrame:f.Frame):
        self._addHistogramFilterOutputView(filter, outputFrame)

    def _on_glcm_filter_executed(self, filter:f.Filter, outputFrame:f.Frame):
        self._addGlcmFilterOutputView(filter, outputFrame)

    def _on_image_filter_executed(self, filter:f.Filter, outputFrame:f.Frame):
        self._addImageFilterOutputView(filter, outputFrame)
        #last_item = self.list_widget.item(row)
        #last_widget = self.list_widget.itemWidget(last_item)
        #self._addImageFrameToView(last_widget.list_widget, outputFrame)
        #last_item.list_widget.addImage

        #self._addImageToView(outputFrame.value(), filter.name())
        # item = QListWidgetItem(self.list_widget)
        # item.setSizeHint(QSize(100,100))
        # self.list_widget.addItem(item)
        # widget = ImageItemWidget(self, image, f'{filter.name()}')
        # self.list_widget.setItemWidget(item, widget)

    def _clearItems(self):
        pass
        # while self._layout.cou
        #     item = self._layout.removeWidget(
        #     self.list_widget.removeItemWidget(item)

    @QtCore.pyqtSlot(dict)
    def on_settings_changed(self, settings):
        self.settings = settings

    @QtCore.pyqtSlot(str)
    def activate_file(self, file_path):
        #widget = self.list_widget.itemWidget(item)
        # self.item_activated.emit(widget.image_name)
        self._clearItems()
        if self.pipeline is not None:
            self.pipeline.exec([file_path])

    @QtCore.pyqtSlot(QListWidgetItem)
    def on_item_activated(self, item):
        widget = self.list_widget.itemWidget(item)
        self.item_activated.emit(widget.image_name)
        if self.pipeline is not None:
            self.pipeline.exec([item])

    @QtCore.pyqtSlot(str)
    def on_file_selected(self, file_path):
        if self.pipeline is not None:
            self.pipeline.exec([file_path])

    @QtCore.pyqtSlot(QListWidgetItem)
    def on_item_selected(self, item):
        # if self.pipeline is not None:
        #    self.pipeline.exec()
        pass

    # def _addItemToView(self, filter:f.Filter):
    #     pipeline_widget = PipelineItemWidget(self, filter)
    #     item = QListWidgetItem(self.list_widget)
    #     item.setSizeHint(QSize(200, 220))
    #     self.list_widget.addItem(item)
    #     self.list_widget.setItemWidget(item, pipeline_widget)

    def _addFilterView(self, filter: f.Filter):
        # item_widget = FilterItemWidget(self, filter)
        item_widget = QLabel()
        # item_widget.setFixedSize(200,20)
        item_widget.setText(filter.name())
        # col = len(self._columnRows)
        col = self._layout.columnCount()
        self._layout.addWidget(item_widget, 0, col-1)
        print(f'{self._layout.columnCount()} {col-1}')
        self._layout.setColumnMinimumWidth(col, 300)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeading)
        self._columnRows.append(1)

    def _addHistogramFilterOutputView(self, filter: f.Filter, frame: f.Frame):
        # item_widget = FilterItemWidget(self, filter)
        widget = HistogramWidget(self, orientation=HistogramOrientation.LeftBottom)
        widget.setHistogram(frame.value())
        widget.setMinimumSize(300, 300)
        item_widget = FilterItemWidget(self, widget, filter, frame)
        item_widget.setMinimumSize(300, 300)
        self._addFilterOutputView(item_widget)

    def _addGlcmFilterOutputView(self, filter: f.Filter, frame: f.Frame):
        # item_widget = FilterItemWidget(self, filter)
        widget = GlcmWidget(self)
        widget.setData(frame.value())
        widget.setMinimumSize(300, 300)
        item_widget = FilterItemWidget(self, widget, filter, frame)
        item_widget.setMinimumSize(300, 300)
        self._addFilterOutputView(item_widget)

    def _addImageFilterOutputView(self, filter: f.Filter, frame: f.Frame):
        widget = QLabel(self)
        name = f'{filter.name()}'
        thumb_image = frame.value()
        qimage = ImageQt.ImageQt(thumb_image)
        pixmap = QtGui.QPixmap.fromImage(qimage)
        pixmap = pixmap.scaled(
            300, 300, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
        widget.setPixmap(pixmap)
        widget.setToolTip(name)
        item_widget = FilterItemWidget(self, widget, filter, frame)
        item_widget.setMinimumSize(300,300)
        self._addFilterOutputView(item_widget)

    def _addFilterOutputView(self, item_widget):
        col = len(self._columnRows) - 1
        row = self._columnRows[col]
        self._columnRows[col] += 1
        self._layout.addWidget(item_widget, row, col, Qt.AlignmentFlag.AlignCenter)

# class PipelineTableWidget(QTableWidget):
#     item_selected = pyqtSignal(str)
#     item_activated = pyqtSignal(str)

#     def __init__(self, parent=None, pipeline:f.Pipeline=None, settings=None):
#         super().__init__(parent)
#         self.pipeline = pipeline
#         self.settings = settings
#         self.pipeline = defaultPipeline(self) if pipeline is None else pipeline
#         self._columnRows = []
#         self.horizontalHeader().setStretchLastSection(True)
#         # self.setSizePolicy(QSizePolicy(
#         #     QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding))
#         # layout.setContentsMargins(0, 0, 0, 0)
#         #layout.setSpacing(1)
    
#     @QtCore.pyqtSlot(str)
#     def activate_file(self, file_path):
#         # self._clearItems()
#         if self.pipeline is not None:
#             self.pipeline.exec([file_path])

#     def _on_filter_executing(self, filter: f.Filter, inputFrame: f.Frame):
#         # self._addItemToView(filter)
#         self._addFilterView(filter)

#     def _on_image_filter_executed(self, filter: f.Filter, outputFrame: f.Frame):
#         self._addFilterOutputView(filter, outputFrame)

#     def _addFilterView(self, filter: f.Filter):
#         # item_widget = FilterItemWidget(self, filter)
#         item_widget = QLabel()
#         item_widget.setStyleSheet('background-color: #000000')
#         # item_widget.setFixedSize(200,20)
#         item_widget.setText(filter.name())
#         #col = self.columnCount()
#         col = len(self._columnRows)
#         self.setColumnCount(col+1)
#         self.setHorizontalHeaderItem(col, item_widget)
#         self.setColumnWidth(col, 300)

#         # self.setItem(0, col, QTableWidget(item_widget))
#         self._columnRows.append(1)

#     def _addFilterOutputView(self, filter: f.Filter, frame: f.Frame):
#         # item_widget = FilterItemWidget(self, filter)
#         item_widget = FilterItemWidget(self, filter, frame)
#         # item = QListWidgetItem(list_widget)
#         # item.setSizeHint(QSize(200, 220))
#         # list_widget.addItem(item)
#         # list_widget.setItemWidget(item, item_widget)
#         col = len(self._columnRows) - 1
#         row = self._columnRows[col]
#         if row >= self.rowCount():
#             self.setRowCount(self.rowCount()+1)
#         self._columnRows[col] += 1
#         self.setCellWidget(row, col, item_widget)
#         # self.setFixedSize(self._layout.columnCount() * 200, (self._layout.rowCount()-1) * 220 + 20)


def defaultPipeline(self: PipelineWidget):
    source = f.Source()
    loader = fi.LoadImage()
    inprint = fi.ImageInpaint()
    resize = fi.ResizeImage((1280, 960), True, False)
    # crop = fi.CropImage((400, 300, 800, 700))
    crop = fi.CropImage((160, 0, 960, 960))
    # sobel = fi.SobelEdge()
    histogram = fi.Histogram()
    glcm = di.GlcmFilter()

    # pipeline.connect(source.output(), loader.input())
    # pipeline.connect(loader.output(), crop.input())
    # pipeline.connect(crop.output(0), histogram.input())
    # pipeline.connect(crop.output(1), glcm.input())
    # pipeline.connect(glcm.output(0), ) # glcm.output[0] => image
    # pipeline.connect(glcm.output(1), somefilter.input()) # glcm.output[1] => glcm

    source.output().connect(loader.input())
    loader.output().connect(inprint.input())
    inprint.output().connect(resize.input())
    resize.output().connect(crop.input())
    crop.addOutput()
    # crop.output(0).connect(sobel.input())
    crop.output(0).connect(histogram.input())
    crop.output(1).connect(glcm.input())
    crop.filter_executing.connect(self._on_filter_executing)
    crop.filter_executed.connect(self._on_image_filter_executed)
    # sobel.filter_executing.connect(self._on_filter_executing)
    # sobel.filter_executed.connect(self._on_image_filter_executed)
    histogram.filter_executing.connect(self._on_filter_executing)
    histogram.filter_executed.connect(self._on_histogram_filter_executed)
    glcm.filter_executed.connect(self._on_glcm_filter_executed)

    pipeline = f.Pipeline(source)
    return pipeline
