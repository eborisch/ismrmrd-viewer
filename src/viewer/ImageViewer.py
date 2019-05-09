import logging
import numpy
import pdb
import matplotlib.pyplot

from PySide2 import QtWidgets, QtCore

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class ImageViewer(QtWidgets.QWidget):

    def __init__(self, container):
        super().__init__()

        self.container = container
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(2,2,2,2)
        self.fig = Figure(figsize=(self.width(), self.height()), dpi=72, facecolor=(1,1,1), edgecolor=(0,0,0))
        self.ax = self.fig.add_subplot(111)
        logging.info("Image constructor.")
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        layout.addWidget(self.canvas) 
        
        # Window/Level support
        self.min = None
        self.max = None
        self.range = None
        self.window = 1.0
        self.level = 0.5
        self.mloc = None

        self.update_image()

        #pdb.set_trace()

    def mouseMoveEvent(self, event):
        newx = event.x()
        newy = event.y()
        if self.mloc is None:
            self.mloc = (newx, newy)
            return 
        
        self.window = self.window - (newx - self.mloc[0]) * 0.01
        self.level = self.level - (newy - self.mloc[1]) * 0.01
        if self.window < 0:
            self.window = 0.0
        if self.window > 2:
            self.window = 2.0
        if self.level < 0:
            self.level = 0.0
        if self.level > 1:
            self.level = 1.0
        print("{},{}".format(self.window, self.level)) 
        rng = self.window_level()
        self.image.set_clim(*rng)        

        self.mloc = (newx, newy)
        self.canvas.draw()

    def mouseReleaseEvent(self, event):
        self.mloc = None

    def window_level(self):
        return (self.level * self.range - self.window / 2 * self.range + self.min, 
                self.level * self.range + self.window / 2 * self.range + self.min)

    def update_image(self, n=0, c=0, z=0):
        image = numpy.array(self.container.images.to_numpy(self.container.images[n])[1][c][z])
        if self.min is None:
            self.min = image.min()
            self.max = image.max()
            self.range = self.max - self.min

        wl = self.window_level()
        self.image = self.ax.imshow(image, 
                                    vmin=wl[0], 
                                    vmax=wl[1], 
                                    cmap=matplotlib.pyplot.get_cmap('gray'))

        self.ax.set_xticks([])
        self.ax.set_yticks([])        
