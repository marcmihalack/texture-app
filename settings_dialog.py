from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QDoubleSpinBox, 
                             QCheckBox, QRadioButton, QSlider, QPushButton, QHBoxLayout,
                             QFileDialog, QListWidget, QLineEdit, QStyle)
from PyQt6.QtCore import Qt, QPoint, QFile, QIODevice, QTextStream, QSettings, QStandardPaths
import json
import os

def deepcopy(value):
    if value is dict:
        copy = dict()
        for item,v in value.items():
            copy[item] = deepcopy(v)
        return copy
    if value is set:
        copy = set()
        for v in value.items():
            copy.add(deepcopy(v))
        return copy
    return value

class Settings:
    def __init__(self, defaults, settings_file):
        super().__init__()
        self._defaults = defaults
        self._path = settings_file
        if os.path.exists(settings_file):
            self._settings = Settings._load_from_file(settings_file)
        else:
            self._settings = deepcopy(defaults)

    def load_file(settings_file):
        defaults = json.load(settings_file)
        settings = Settings(defaults, settings_file)
        return settings

    def _load_from_file(settings_file):
        with open(settings_file, 'r') as f:
            return json.load(f)

    def get(self, path: str, default=None):
        parts = path.split('/')
        entry = self._settings
        last = len(parts) - 1
        for i, part in enumerate(parts):
            if i == last:
                return entry.get(part, default)
            entry = entry.get(part)
            if entry is None:
                return default
        return default
    
    def set(self, path: str, value):
        parts = path.split('/')
        entry = self._settings
        last = len(parts) - 1
        for i, part in enumerate(parts):
            if i == last:
                entry[part] = value
                return True
            entry = entry.get(part)
            if entry is None:
                return False
        return False
    
    def save(self):
        with open(self._path, 'w') as f:
            json.dump(self._settings, f, indent=2)

    def load(self):
        if os.path.exists(self._path):
            with open(self._path, 'r') as f:
                self._settings = json.load(f)
        else:
            self._settings = deepcopy(self._defaults)


class SettingsDialog(QDialog):
    settings_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data\\settings.json")

    def defaults():
        return {
            'last_dir': None,
            'directories': [],
            'confidence': 0.99,
            'distance': 0.3,
            'show_all_files': False,
            'dataset_file': os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data\\.json'),
            'dataset_files': []
            # 'radio_option': 0,
            # 'slider_value': 0
        }
    
    def getSettings():
        if os.path.exists(SettingsDialog.settings_file):
            with open(SettingsDialog.settings_file, 'r') as f:
                return json.load(f)
        return SettingsDialog.defaults()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Settings')

        layout = QVBoxLayout()

        # List of directories
        self.directory_label = QLabel('Directories:')
        layout.addWidget(self.directory_label)

        self.directories = []
        self.directories_list = QListWidget()
        self.directories_list.setFixedHeight(self.directories_list.sizeHintForRow(
            0) * 5 + 2 * self.directories_list.frameWidth())  # Set fixed height
        layout.addWidget(self.directories_list)

        # self.add_directory_button = QPushButton('Add Directory')
        # self.add_directory_button.clicked.connect(self.add_directory)
        # layout.addWidget(self.add_directory_button)
        # self.remove_directory_button = QPushButton('Remove')
        # self.remove_directory_button.clicked.connect(self.remove_directory)
        # layout.addWidget(self.remove_directory_button)

        # Confidence
        confidence_layout = QHBoxLayout()
        self.confidence_label = QLabel('Minimum Confidence:')
        confidence_layout.addWidget(self.confidence_label)
        self.confidence_spinbox = QDoubleSpinBox()
        self.confidence_spinbox.setMinimum(0.0)
        self.confidence_spinbox.setMaximum(1.0)
        self.confidence_spinbox.setSingleStep(0.001)
        self.confidence_spinbox.setDecimals(5)
        confidence_layout.addWidget(self.confidence_spinbox)

        # Distance
        self.distance_label = QLabel('Maximum Distance:')
        confidence_layout.addWidget(self.distance_label)
        self.distance_spinbox = QDoubleSpinBox()
        self.distance_spinbox.setMinimum(0.0)
        self.distance_spinbox.setMaximum(1.0)
        self.distance_spinbox.setSingleStep(0.001)
        self.distance_spinbox.setDecimals(5)
        confidence_layout.addWidget(self.distance_spinbox)

        layout.addLayout(confidence_layout)

        # label = QLabel('Dataset file')
        # layout.addWidget(label)

        # dataset_layout = QHBoxLayout()
        # self.dataset_file_textbox = QLineEdit(self)
        # browse_button = QPushButton("...", self)
        # browse_button.setToolTip('Browse dataset files')
        # #icon = browse_button.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload)
        # #browse_button.setIcon(icon)
        # browse_button.clicked.connect(self.open_dataset_file)
        # dataset_layout.addWidget(self.dataset_file_textbox)
        # dataset_layout.addWidget(browse_button)
        # layout.addLayout(dataset_layout)
        self.dataset_file_textbox = self.create_browse_layout(
            layout, 'Dataset file', self.open_dataset_file, 'Browse files for dataset file')

        # Checkbox
        self.show_all_files_checkbox = QCheckBox('Show all files')
        layout.addWidget(self.show_all_files_checkbox)

        # Radio buttons
        self.radio_button1 = QRadioButton('Option 1')
        self.radio_button2 = QRadioButton('Option 2')
        self.radio_button3 = QRadioButton('Option 3')
        self.radio_buttons = [self.radio_button1, self.radio_button2, self.radio_button3]
        layout.addWidget(self.radio_button1)
        layout.addWidget(self.radio_button2)
        layout.addWidget(self.radio_button3)

        # Slider
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 10)
        layout.addWidget(self.slider)

        self.slider_value_label = QLabel()
        self.slider_value_label.setText(f'{self.slider.value() / 10:.1f}')
        layout.addWidget(self.slider_value_label)
        
        self.slider.valueChanged.connect(self.update_slider_value_label)

        # Save button
        self.save_button = QPushButton('Save')
        self.save_button.clicked.connect(self.save_settings)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

        self.load_settings()

    def create_browse_layout(self, parent_layout, label, clicked, tooltip=''):
        label = QLabel(label)
        parent_layout.addWidget(label)

        dataset_layout = QHBoxLayout()
        dataset_file_textbox = QLineEdit(self)
        browse_button = QPushButton("...", self)
        browse_button.setToolTip(tooltip)
        #icon = browse_button.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload)
        #browse_button.setIcon(icon)
        browse_button.clicked.connect(clicked)
        dataset_layout.addWidget(dataset_file_textbox)
        dataset_layout.addWidget(browse_button)
        parent_layout.addLayout(dataset_layout)
        return dataset_file_textbox

    def open_dataset_file(self):
        #if self.settings
        # directory = os.path.dirname(self.settings['dataset_file']
        dataset_file = self.dataset_file_textbox.text()
        directory = os.path.dirname(dataset_file) if dataset_file else os.path.abspath(os.path.curdir)
        file_paths = QFileDialog.getOpenFileName(
            self, "Open Dataset file", directory=directory)
        if file_paths:
            self.dataset_file_textbox.setText(file_paths[0])

    def update_slider_value_label(self):
        self.slider_value_label.setText(f'{self.slider.value() / 10:.1f}')

    def add_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.directories.append(directory)
            new_directory_label = QLabel(directory)
            self.layout().insertWidget(self.layout().indexOf(
                self.add_directory_button), new_directory_label)

    def remove_directory(self):
        selected_items = self.directories_list.selectedItems()
        for item in selected_items:
            self.directories_list.takeItem(self.directories_list.row(item))

    def initializeSettings(self, settings):
        # dataset file
        self.dataset_file_textbox.setText(settings.get('dataset_file', ''))

        # Load directories
        for directory in settings.get('directories', []):
            self.directories_list.addItem(directory)

        # Load confidence and distance values
        self.confidence_spinbox.setValue(settings.get('confidence', 0.99))
        self.distance_spinbox.setValue(settings.get('distance', 0.3))

        # Load show_all_files checkbox
        self.show_all_files_checkbox.setChecked(
            settings.get('show_all_files', False))

        # Load radio buttons
        radio_button_value = settings.get('radio_button', 1)
        self.radio_buttons[radio_button_value - 1].setChecked(True)

        # Load slider value
        self.slider.setValue(int(settings.get('slider', 0.5) * 10))

    def load_settings(self):
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r') as f:
                settings = json.load(f)
                self.initializeSettings(settings)
        else:
            self.initializeSettings(SettingsDialog.defaults())

    def save_settings(self):
        settings = {
            'directories': self.directories,
            'confidence': self.confidence_spinbox.value(),
            'distance': self.distance_spinbox.value(),
            'show_all_files': self.show_all_files_checkbox.isChecked(),
            'dataset_file': self.dataset_file_textbox.text(),
            #'radio_option': self.get_radio_option(),
            #'slider_value': self.slider.value() / 10
        }

        #settings_path = os.path.join(QStandardPaths.writableLocation(
        #    QStandardPaths.StandardLocation.AppDataLocation), 'settings.json')
        #settings_path = os.path.join('settings.json')
        # os.makedirs(os.path.dirname(settings_path), exist_ok=True)

        with open(self.settings_file, 'w') as f:
            json.dump(settings, f, indent=2)

        self.accept()

    def get_radio_option(self):
        if self.radio_button1.isChecked():
            return 1
        elif self.radio_button2.isChecked():
            return 2
        elif self.radio_button3.isChecked():
            return 3
        return None
