import os
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, 
                             QPushButton, QFileDialog, QCheckBox, QStyle, QDialog, QTabWidget)
from PyQt6.QtCore import Qt, pyqtSignal
from imagecrossing_widget import ImageCrossingWidget
from select_regions_dialog import SelectRegionsDialog, SelectRegionsWidget
from image_widget import ImageWidget
from image_files_widget import ImageFilesWidget
from pipeline_widget import PipelineWidget
from settings_dialog import Settings, SettingsDialog
import PyQt6.QtCore as QtCore
import qdarktheme
import filters as filters
import image_filters as ifilters
import data_filters as dfilters
from skimage import io, feature, color

class MainWindow(QMainWindow):
    settings_changed = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.settings = Settings({
            'last_directory': None
        }, os.path.join(o.path.dirname(os.path.realpath(__file__)),'data\\settings.json'))

        self.setToolTipDuration(5000)
        self.setStyleSheet("""QToolTip {
                        background-color: black;
                        color: white;
                        border: black solid 1px
                        }""")

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # ----- left layout -----
        left_panel = QWidget(self)
        left_layout = QVBoxLayout(left_panel)

        buttons_layout = QHBoxLayout()

        open_folder_button = self.createPushButton(
            left_panel, 'Open folder', 'Open folder', QStyle.StandardPixmap.SP_DialogOpenButton, self.open_folder)
        buttons_layout.addWidget(open_folder_button)

        refresh_button = self.createPushButton(
            left_panel, 'Open file', 'Open file', QStyle.StandardPixmap.SP_BrowserReload, self.open_file)
        buttons_layout.addWidget(refresh_button)

        settings_button = self.createPushButton(
            left_panel, 'Regions', 'Edit image regions', QStyle.StandardPixmap.SP_CommandLink, self.edit_regions)
        buttons_layout.addWidget(settings_button)

        plot_button = self.createPushButton(
            left_panel, 'Plot', 'Plot', QStyle.StandardPixmap.SP_DirHomeIcon, self.show_plot)
        buttons_layout.addWidget(plot_button)

        settings_button = self.createPushButton(
            left_panel, 'Settings', 'Settings', QStyle.StandardPixmap.SP_VistaShield, self.edit_settings)
        buttons_layout.addWidget(settings_button)

        left_layout.addLayout(buttons_layout)

        # ----- files -----
        self.files_widget = ImageFilesWidget(self)
        left_layout.addWidget(self.files_widget, stretch=1)

        self.left_panel = left_panel
        layout.addWidget(left_panel, stretch=1)

        # ----- right layout -----
        self._tabPanel = QTabWidget(self)
        self._tabPanel.setContentsMargins(0,0,0,0)
        # layout.addWidget(self._tabPanel)
        # right_panel = QWidget(self)
        #right_layout = QVBoxLayout(right_panel)
        # self._tabPanel.addTab(right_panel, 'Pipeline')

        # ----- pipeline -----
        self.pipeline_widget = PipelineWidget(self)
        self._fileActivatedTabConnection = self.files_widget.file_activated.connect(
            self.pipeline_widget.activate_file)
        self._tabPanel.addTab(self.pipeline_widget, "Pipeline")

        # self.regions_widget = SelectRegionsWidget(self)
        self.imagecrossing_widget = ImageCrossingWidget(self)
        self.files_widget.file_activated.connect(self.imagecrossing_widget.loadFile)
        self._tabPanel.addTab(self.imagecrossing_widget, 'Crossing')
        self._tabPanel.currentChanged.connect(self._tabChanged)
        # self.pipeline_widget.setStyleSheet('background-color: #501010')

        # self.pipeline_table_widget = PipelineWidget(self)
        # self.files_widget.file_activated.connect(self.pipeline_table_widget.activate_file)
        # right_layout.addWidget(self.pipeline_table_widget)
        # self.pipeline_table_widget.setStyleSheet('background-color: #101050')

        # ----- layout -----
        # margins = right_layout.contentsMargins()
        # margins.setLeft(0)
        # right_layout.setContentsMargins(margins)
        margins = left_layout.contentsMargins()
        margins.setRight(0)
        left_layout.setContentsMargins(margins)

        # layout.addWidget(right_panel, stretch=3)
        layout.addWidget(self._tabPanel, stretch=3)

        self.last_directory = self.settings.get('last_directory')
        if not self.last_directory:
            self.last_directory = os.path.abspath(os.curdir)

    def _tabChanged(self, index):
        self._tabPanel.currentWidget()


    def show_plot(self):
        pass
        
    def edit_regions(self):
        items = [self.files_widget.item(x)
                 for x in range(self.files_widget.count())]
        if items:
            items = [{'name': i.text(), 'path': i.file_path} for i in items]
            self.dialog = SelectRegionsDialog(items)
            self.dialog.showMaximized()

    def eventFilter(self, object: QtCore.QObject, event: QtCore.QEvent) -> bool:
        print(f'{event.type().name}')
        if (object is self and 
            (event.type() == QtCore.QEvent.Type.NonClientAreaMouseButtonRelease
             or event.type() == QtCore.QEvent.Type.WindowStateChange)):
            self.image_widget.resizeComplete()
        return super().eventFilter(object, event)

    def edit_settings(self):
        settings_dialog = SettingsDialog(self)
        result = settings_dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            self.settings = SettingsDialog.getSettings()
            self.settings_changed.emit(self.settings)

    def createPushButton(self, parent, text, tooltip=None, icon=None, clicked=None):
        button = QPushButton(text, parent)
        if icon is not None:
            icon = button.style().standardIcon(icon)
            button.setIcon(icon)
        if tooltip is not None:
            button.setToolTip(tooltip)
        if clicked is not None:
            button.clicked.connect(clicked)
        return button

    def open_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Open Folder", directory=self.last_directory)
        if folder_path:
            self.files_widget.open_folder(folder_path)
            self.last_directory = folder_path
            self.settings.set('last_directory', self.last_directory)
            self.settings.save()

    def open_file(self):
        file_path_tuple = QFileDialog.getOpenFileName(self, "Open file", directory=self.last_directory)
        if file_path_tuple[0]: # (file_path, file_filter)
            self.files_widget.open_file(file_path_tuple[0])
            self.last_directory = os.path.dirname(file_path_tuple[0])
            self.settings.set('last_directory', self.last_directory)
            self.settings.save()

    def refresh(self):
        pass

if __name__ == "__main__":

    app = QApplication(sys.argv)

    qdarktheme.setup_theme()
    main_window = MainWindow()
    main_window.setWindowTitle("Tex App")
    # main_window.resize(800, 600)
    main_window.showMaximized()

    sys.exit(app.exec())
