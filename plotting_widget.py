from PyQt6 import QtWidgets, QtCore, QtGui
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
import matplotlib.transforms as mtransforms
from PIL import Image
from skimage import io, feature, color

class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.x, self.y = np.arange(0, 10, 0.1), np.sin(np.arange(0, 10, 0.1))
        self.plot_type = "line"
        self.line = Line2D([0], [0], color='red')
        self.axes.add_line(self.line)
        self.mpl_connect('motion_notify_event', self.update_line)  # Add this line
        super(PlotCanvas, self).__init__(self.fig)

    def plot(self, scatter=False):
        self.axes.clear()
        if scatter:
            self.axes.scatter(self.x, self.y)
        else:
            self.axes.plot(self.x, self.y)
        self.axes.set_xlabel('X-axis', labelpad=5)
        self.axes.set_ylabel('Y-axis', labelpad=20, rotation=0)
        self.axes.set_xticks(np.linspace(min(self.x), max(self.x), 5))
        self.axes.set_yticks(np.linspace(min(self.y), max(self.y), 5))
        self.draw()

    def update_line(self, event):
        if event.xdata is not None and event.ydata is not None:
            nearest_index = np.abs(self.x-event.xdata).argmin()
            self.line.set_ydata(self.y[nearest_index])
            self.line.set_xdata(self.x[nearest_index])
            self.draw()

    def change_plot_type(self):
        if self.plot_type == "line":
            self.plot_type = "scatter"
        else:
            self.plot_type = "line"
        self.plot(scatter=self.plot_type == "scatter")

class PlotWidget(QtWidgets.QWidget):
    def __init__(self, images):
        super(PlotWidget, self).__init__()

        # Store images
        self.images = images
        distance = 1
        angle = 0.0
        self.contrasts = {distance: {}}
        self.dissimilarities = {distance: {}}
        self.homogeneities = {distance: {}}
        self.energies = {distance: {}}
        contrasts = []
        dissimilarities = []
        homogeneities = []
        energies = []
        for image in images:
            glcm = feature.graycomatrix(image, [distance], [angle], levels=256)
            contrasts.append(feature.graycoprops(glcm, 'contrast'))
            dissimilarities.append(feature.graycoprops(glcm, 'dissimilarity'))
            homogeneities.append(feature.graycoprops(glcm, 'homogeneity'))
            energies.append(feature.graycoprops(glcm, 'energy'))

        self.contrasts[distance][angle] = contrasts
        self.dissimilarities[distance][angle] = dissimilarities
        self.homogeneities[distance][angle] = homogeneities
        self.energies[distance][angle] = energies

        # Create UI elements
        self.bins_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.bins_slider.setRange(2, 100)
        self.bins_slider.setValue(10)

        self.distance_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.distance_slider.setRange(1, 20)
        self.distance_slider.setValue(1)

        self.angle_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.angle_slider.setRange(0, 180)
        self.angle_slider.setSingleStep(15)

        self.contrast_checkbox = QtWidgets.QCheckBox("Contrast")
        self.dissimilarity_checkbox = QtWidgets.QCheckBox("Dissimilarity")
        self.homogeneity_checkbox = QtWidgets.QCheckBox("Homogeneity")
        self.energy_checkbox = QtWidgets.QCheckBox("Energy")

        # Create plot
        # self.figure = plt.figure()
        self.canvas = PlotCanvas(self, width=5, height=4)

        # Arrange UI elements in a layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.bins_slider)
        layout.addWidget(self.distance_slider)
        layout.addWidget(self.angle_slider)
        layout.addWidget(self.contrast_checkbox)
        layout.addWidget(self.dissimilarity_checkbox)
        layout.addWidget(self.homogeneity_checkbox)
        layout.addWidget(self.energy_checkbox)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        # Connect signals and slots
        self.bins_slider.valueChanged.connect(self.update_plot)
        self.distance_slider.valueChanged.connect(self.update_plot)
        self.angle_slider.valueChanged.connect(self.update_plot)
        self.contrast_checkbox.stateChanged.connect(self.update_plot)
        self.dissimilarity_checkbox.stateChanged.connect(self.update_plot)
        self.homogeneity_checkbox.stateChanged.connect(self.update_plot)
        self.energy_checkbox.stateChanged.connect(self.update_plot)

    def getProps(self, distance: int, angle: float):
        if distance not in self.contrasts:
            self.contrasts[distance] = {}
            self.dissimilarities = {distance: {}}
            self.homogeneities = {distance: {}}
            self.energies = {distance: {}}
            contrasts = []
            dissimilarities = []
            homogeneities = []
            energies = []
            for image in self.images:
                glcm = feature.graycomatrix(image, [distance], [angle], levels=256)
                contrasts.append(feature.graycoprops(glcm, 'contrast'))
                dissimilarities.append(feature.graycoprops(glcm, 'dissimilarity'))
                homogeneities.append(feature.graycoprops(glcm, 'homogeneity'))
                energies.append(feature.graycoprops(glcm, 'energy'))

        self.contrasts[distance][angle] = contrasts
        self.dissimilarities[distance][angle] = dissimilarities
        self.homogeneities[distance][angle] = homogeneities
        self.energies[distance][angle] = energies

    def update_plot(self):
        # Clear the previous plot
        # self.figure.clear()

        # Calculate GLCM properties and create a new plot
        # ... (this part is omitted for brevity) ...

        # Draw the new plot
        self.canvas.draw()
