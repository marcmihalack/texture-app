import json
import math
import os
from PyQt6.QtWidgets import (QListWidgetItem, QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton,
                             QComboBox, QCheckBox, QWidget)
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtCore import Qt, QRectF, QPointF
from select_regions import SelectRegionWidget, ShapeType, ShapeRegion


class CustomValidator(QRegularExpressionValidator):
    def validate(self, input, pos):
        # if input == "All":
        #    return QValidator.State.Acceptable, input, pos
        return super().validate(input, pos)


class SelectRegionsDialog(QDialog):
    def __init__(self, files, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self._widget = SelectRegionsWidget(files, self)
        layout.addWidget(self._widget, stretch=1)
        self.setLayout(layout)


class SelectRegionsWidget(QWidget):
    def __init__(self, files, parent=None):
        super().__init__(parent)
        self.files = files
        self._region_size = (256, 256)
        self._improveImage = True
        # self.regions_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "regions.json")
        self.init_ui()

        self._all_regions = self.load_regions()
        for file in self.files:
            item = QListWidgetItem(self.file_list)
            item.file_path = file['path'].replace('\\', '/')
            file_data = self._all_regions.get(item.file_path)
            if file_data:
                item.regions = file_data.get('regions')
            else:
                item.regions = []
            item.setText(file['name'])
            item.setToolTip(item.file_path)
            self.file_list.addItem(item)

    def formatFilePath(self):
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), f'data\\regions.json')

    def keyPressEvent(self, event):
        self.select_region_widget.keyPressEvent(event)

    def init_ui(self):
        left_layout = QVBoxLayout()

        self.file_list = QListWidget()
        self.file_list.currentItemChanged.connect(self.on_image_selected)

        self.select_region_widget = SelectRegionWidget(ShapeType.CIRCLE)

        main_layout = QHBoxLayout()
        #main_layout.addWidget(self.file_list, stretch=1)
        left_layout.addWidget(self.file_list, stretch=1)
        main_layout.addLayout(left_layout);

        main_layout.addWidget(self.select_region_widget, stretch=9)

        bottom_layout = QHBoxLayout()

        # label = QLabel('Region size')
        # self.size_input = QLineEdit(self)
        # self.size_input.setValidator(QIntValidator(100, 1000, self))
        # self.size_input.setMaximumWidth(220)
        # self.size_input.setText(f'{self.select_region_widget.region_size[0]}')
        # self.size_input.editingFinished.connect(self.update_region_size)
        # bottom_layout.addWidget(label)
        # bottom_layout.addWidget(self.size_input)
        self.shape_combobox = QComboBox(self)
        self.shape_combobox.addItems(["Circle", "Square"])
        self.shape_combobox.currentIndexChanged.connect(self.update_region_shape)
        bottom_layout.addWidget(self.shape_combobox)

        self.size_combobox = QComboBox(self)
        #self.size_combobox.setEditable(True)
        self.size_combobox.addItems(["256", "320"])

        # Regular expression to match "All" or numbers between 100 and 9999
        # reg_exp = QRegularExpression(r"All|([1-9]\d{2,3})")
        #reg_exp = QRegularExpression(r"^([1-9]\d{2,3})$")
        #self.size_combobox.setValidator(CustomValidator(reg_exp, self))
        #self.size_combobox.lineEdit().editingFinished.connect(self.update_region_size)
        self.size_combobox.currentIndexChanged.connect(self.update_region_size)
        bottom_layout.addWidget(self.size_combobox)

        show_all_regions_checkbox = QCheckBox("Show all regions", self)
        show_all_regions_checkbox.stateChanged.connect(
            lambda state: self.select_region_widget.setShowAllRegions(state == Qt.CheckState.Checked.value))
        show_all_regions_checkbox.setChecked(
            self.select_region_widget.getShowAllRegions())
        bottom_layout.addWidget(show_all_regions_checkbox)

        checkbox = QCheckBox("Improve", self)
        checkbox.setChecked(True)
        checkbox.stateChanged.connect(
            lambda state: self.setImproveImage(state == Qt.CheckState.Checked.value))
        bottom_layout.addWidget(checkbox)

        button = QPushButton("Clear")
        button.clicked.connect(
            lambda: self.select_region_widget.deleteAllRegions())
        bottom_layout.addWidget(button)

        # button = QPushButton("Reset")
        # button.clicked.connect(lambda: self.select_region_widget.reset_regions())
        # bottom_layout.addWidget(button)

        save_button = QPushButton("Save All")
        save_button.clicked.connect(self.save_regions)
        bottom_layout.addWidget(save_button)
        left_layout.addLayout(bottom_layout)

        #layout.addLayout(main_layout)
        #layout.addLayout(bottom_layout)

        self.setLayout(main_layout)
        self.setWindowFlags(self.windowFlags()
                            | Qt.WindowType.WindowMinimizeButtonHint | Qt.WindowType.WindowMaximizeButtonHint)

    def setImproveImage(self, flag):
        self.select_region_widget.refreshImage(flag)

    def update_region_shape(self):
        text = self.size_combobox.currentText()
        shape = ShapeType.CIRCLE if self.shape_combobox.currentText() == "Circle" else ShapeType.SQUARE
        self.select_region_widget.setRegionShape(shape)

    def update_region_size(self):
        # size = int(self.size_input.text())
        # self._region_size = (size, size)
        # self.select_region_widget.region_size = (size, size)

        size_text = self.size_combobox.currentText()
        # if size_text == "All":
        #     size = 0
        # else:
        #    size = int(size_text)
        size = int(size_text)
        self.select_region_widget.setRegionSize((size, size))

        # current = self.file_list.currentItem()
        # if current:
        #    self.select_region_widget.loadImage(current.file_path

    def updateCurrentRegions(self):
        item = self.file_list.currentItem()
        if item:
            if item.file_path == self.select_region_widget.image_path:
                item.regions = self.select_region_widget.getRegions()
            else:
                print('Selected item path', self.select_region_widget.image_path,
                      'does not match current item path', item.file_path)

    def on_image_selected(self, current, previous):
        if current:
            if previous:
                path = previous.file_path
                if path != self.select_region_widget.image_path:
                    print('Selected item path', self.select_region_widget.image_path,
                          'does not match previous item path', path)
                else:
                    previous.regions = self.select_region_widget.getRegions()
            self.select_region_widget.loadImage(
                current.file_path, current.regions, False)

    def load_regions_from_file(self, file_path):
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _createShapeRegion(self, shape, coords):
        if shape == ShapeType.CIRCLE:
            assert(len(coords) == 3)
            actualSize = coords[2] * math.sqrt(2)
            halfSize = actualSize / 2
            return ShapeRegion(shape, QPointF(coords[0], coords[1]),
                               QRectF(coords[0]-halfSize, coords[1]-halfSize, actualSize, actualSize), coords[2])
        elif shape == ShapeType.SQUARE:
            assert(len(coords) == 3)
            cx,cy,sz = coords
            halfSize = sz / 2
            return ShapeRegion(shape, QPointF(cx,cy), QRectF(float(cx-halfSize), float(cy-halfSize), sz, sz), sz)
        else:
            raise ValueError('Invalid shape type')

    def load_regions(self):
        regions = self.load_regions_from_file(self.formatFilePath())
        counts = {}
        total_count = 0
        result_regions = {}
        for file_path, value in regions.items():
            image_regions = value.get('regions')
            result_regions[file_path.replace('\\', '/')] = value
            if image_regions:
                rs = []
                for image_region in image_regions:
                    if 'shape' in image_region:
                        # r = image_region['coords']
                        # sr = ShapeRegion(ShapeType[image_region['shape']],
                        #     QRectF(float(r[0]), float(r[1]), float(r[2])-float(r[0]), float(r[3])-float(r[1])))
                        sr = self._createShapeRegion(ShapeType[image_region['shape']], image_region['coords'])
                        rs.append(sr)
                    else:
                        # r = image_region
                        # sr = ShapeRegion(ShapeType.SQUARE,
                        #     QRectF(float(r[0]), float(r[1]), float(r[2])-float(r[0]), float(r[3])-float(r[1])))
                        left,top,right,bottom = image_region['coords']
                        size = right - left
                        halfSize = size / 2
                        sr = self._createShapeRegion(ShapeType.SQUARE, (left-halfSize, top-halfSize, size))
                        rs.append(sr)
                        #rs = [(ShapeType.SQUARE, QRectF(float(r[0]), float(r[1]), float(
                        #    r[2])-float(r[0]), float(r[3])-float(r[1]))) for r in image_regions]
                value['regions'] = rs
                total_count += len(rs)
                for r in rs:
                    w = str(int(r.size()))
                    if w not in counts:
                        counts[w] = 1
                    else:
                        counts[w] += 1
            else:
                print('No regions found for', file_path)

        for id,count in counts.items():
            print('Counts', id, count)
        print('Total files', len(result_regions), 'regions', total_count)
        return result_regions

    def save_regions(self):
        self.updateCurrentRegions()
        all_regions = {}
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            if item:
                image_path = os.path.abspath(item.file_path).replace('\\', '/')
                regions = item.regions
                self._all_regions[image_path] = regions
                if regions:
                    regions = [{'shape':r.shape().name,'coords':r.getCoords()} for r in regions]
                # self.select_region_widget.image_path = image_path
                # self.select_region_widget.loadImage()
                all_regions[image_path] = {
                    'regions': regions
                }

        filePath = self.formatFilePath()
        try:
            with open(filePath+'.tmp', "w") as f:
                json.dump(all_regions, f)
        except Exception as e:
            print('Error saving regions', e)
            return
        
        if os.path.exists(filePath+'.bak'):
            os.remove(filePath+'.bak')
        os.rename(filePath, filePath + '.bak')
        os.rename(filePath+'.tmp', filePath)
        # os.rename(filePath + '.bak', filePath)
