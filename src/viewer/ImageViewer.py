import logging
import numpy
import pdb
import matplotlib.pyplot

from PySide2 import QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class ImageViewer(QtWidgets.QWidget):

    def __init__(self, container):
        super().__init__()

        self.container = container
        layout = QtWidgets.QVBoxLayout(self)
        self.fig = Figure(figsize=(self.width(), self.height()), dpi=72, facecolor=(1,1,1), edgecolor=(0,0,0))
        self.ax = self.fig.add_subplot(111)
        logging.info("Image constructor.")
        canvas = FigureCanvas(self.fig)
        layout.addWidget(canvas) 
        self.min = None
        self.max = None
        self.vmin = None
        self.vmaz = None
        self.update_image()

        #pdb.set_trace()

    def update_image(self, n=0, c=0, z=0):
        image = numpy.array(self.container.images.to_numpy(self.container.images[n])[1][c][z])
        if self.min is None:
            self.min = image.min()
            self.vmin = self.min
            self.max = image.max()
            self.vmax = self.max

        self.ax.imshow(image, 
                       vmin=image.min(),
                       vmax=image.max(),
                       cmap=matplotlib.pyplot.get_cmap('gray'))

        self.ax.set_xticks([])
        self.ax.set_yticks([])        
