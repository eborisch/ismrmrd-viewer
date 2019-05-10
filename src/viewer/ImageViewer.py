import logging
import numpy
import pdb
import matplotlib.pyplot

from PySide2 import QtCore, QtWidgets as QTW

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class ImageViewer(QTW.QWidget):
    def __init__(self, container):
        """
        Stores off container for later use; sets up the main panel display
        canvas for plotting into with matplotlib. Also prepares the interface
        for working with multi-dimensional data.
        """
        super().__init__()

        self.container = container

        # Main layout
        layout = QTW.QVBoxLayout(self)

        self.nimg = len(self.container.images)

        # Dimension controls; Add a widget with a horizontal layout
        cw = QTW.QWidget()
        layout.addWidget(cw)
        controls = QTW.QHBoxLayout(cw)

        # Create a drop-down for the image instance
        self.selected = {}
        for dim in ('Instance', 'Coil', 'Slice'):
            controls.addWidget(QTW.QLabel("{}:".format(dim)))
            self.selected[dim] = QTW.QSpinBox()
            controls.addWidget(self.selected[dim])
            self.selected[dim].valueChanged.connect(self.update_image)
        self.selected['Instance'].setMaximum(self.nimg - 1)

        layout.setContentsMargins(0,0,0,0)
        self.fig = Figure(figsize=(8,8),
                          dpi=72,
                          facecolor=(1,1,1),
                          edgecolor=(0,0,0))

        self.ax = self.fig.add_subplot(111)
        logging.info("Image constructor.")
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        layout.addWidget(self.canvas) 
        
        self.stack = numpy.array(self.container.images.data)
        #pdb.set_trace()

        # Window/Level support
        self.min = self.stack.min()
        self.max = self.stack.max()
        self.range = self.max - self.min
        self.window = 1.0
        self.level = 0.5
        self.mloc = None

        self.selected['Coil'].setMaximum(len(self.stack[0]) - 1)
        self.selected['Slice'].setMaximum(len(self.stack[0][0]) - 1)

        self.update_image()

    def frame(self):
        return self.selected['Instance'].value()

    def coil(self):
        return self.selected['Coil'].value()

    def slice(self):
        return self.selected['Slice'].value()

    def mouseMoveEvent(self, event):
        "Provides window/level behavior."
        newx = event.x()
        newy = event.y()
        if self.mloc is None:
            self.mloc = (newx, newy)
            return 
        
        # Modify mapping and polarity as desired
        self.window = self.window - (newx - self.mloc[0]) * 0.01
        self.level = self.level - (newy - self.mloc[1]) * 0.01
        
        # Don't invert
        if self.window < 0:
            self.window = 0.0
        if self.window > 2:
            self.window = 2.0

        if self.level < 0:
            self.level = 0.0
        if self.level > 1:
            self.level = 1.0

        #print("{},{}".format(self.window, self.level)) 

        rng = self.window_level()
        self.image.set_clim(*rng)        

        self.mloc = (newx, newy)
        self.canvas.draw()

    def mouseReleaseEvent(self, event):
        "Reset .mloc to indicate we are done with one click/drag operation"
        self.mloc = None

    def window_level(self):
        return (self.level * self.range 
                  - self.window / 2 * self.range + self.min, 
                self.level * self.range
                  + self.window / 2 * self.range + self.min)
    
    def update_image(self):
        image = self.stack[self.frame()][self.coil()][self.slice()]

        wl = self.window_level()
        self.ax.clear()
        self.image = \
            self.ax.imshow(self.stack[self.frame()][self.coil()][self.slice()], 
                           vmin=wl[0], 
                           vmax=wl[1], 
                           cmap=matplotlib.pyplot.get_cmap('gray'))

        self.ax.set_xticks([])
        self.ax.set_yticks([])        
        self.canvas.draw()
