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

        logging.info("Image constructor.")
        image = numpy.array(container.images.to_numpy(container.images[0])[1][0][0])
        layout = QtWidgets.QVBoxLayout(self)
        fig = Figure(figsize=(self.width(), self.height()), dpi=72, facecolor=(1,1,1), edgecolor=(0,0,0))
        fig.add_subplot(111)

        #matplotlib.pyplot.imshow(image, vmin=image.min(), vmax=image.max())
        matplotlib.pyplot.plot([0, 1, 2], [0, 1, 0])
        fig.draw()
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas) 
        #pdb.set_trace()
