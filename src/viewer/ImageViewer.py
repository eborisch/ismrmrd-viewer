import logging
import numpy
import pdb
import matplotlib.pyplot as pyplot
import matplotlib.animation as animation

from PySide2 import QtCore, QtGui, QtWidgets as QTW

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

DIMS = ('Instance', 'Channel', 'Slice')

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
        for dim in DIMS:
            controls.addWidget(QTW.QLabel("{}:".format(dim)))
            self.selected[dim] = QTW.QSpinBox()
            controls.addWidget(self.selected[dim])
            self.selected[dim].valueChanged.connect(self.update_image)
        self.selected['Instance'].setMaximum(self.nimg - 1)

        self.animate = QTW.QCheckBox("Animate")
        controls.addWidget(self.animate)

        self.animDim = QTW.QComboBox()
        for dim in DIMS:
            self.animDim.addItem(dim)
        controls.addWidget(self.animDim)

        self.animate.stateChanged.connect(self.animation)

        layout.setContentsMargins(0,0,0,0)
        self.fig = Figure(figsize=(6,6),
                          dpi=72,
                          facecolor=(1,1,1),
                          edgecolor=(0,0,0),
                          tight_layout=True)

        self.ax = self.fig.add_subplot(111)
        logging.info("Image constructor.")
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self.canvas.setSizePolicy(QTW.QSizePolicy.Expanding,
                                  QTW.QSizePolicy.Expanding)
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

        self.selected['Channel'].setMaximum(len(self.stack[0]) - 1)
        self.selected['Slice'].setMaximum(len(self.stack[0][0]) - 1)

        #self.installEventFilter(self)
        self.update_image()

    def frame(self):
        return self.selected['Instance'].value()

    def coil(self):
        return self.selected['Channel'].value()

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

        rng = self.window_level()
        self.image.set_clim(*rng)        
#
        self.mloc = (newx, newy)
        self.canvas.draw()

    def mouseReleaseEvent(self, event):
        "Reset .mloc to indicate we are done with one click/drag operation"
        self.mloc = None

#    def eventFilter(self, obj, event):
#        # Want to process resize first
#        handled = QTW.QWidget.eventFilter(self, obj, event)
#        if event.type() == QtCore.QEvent.Resize:
#            #self.fig.set_size_inches(self.width() / 72,
#            #                         self.height() / 72)
#            return handled
#        else:
#            return handled


    def window_level(self):
        return (self.level * self.range 
                  - self.window / 2 * self.range + self.min, 
                self.level * self.range
                  + self.window / 2 * self.range + self.min)
    
    def update_image(self, slice_n=None, animated=False):
        image = self.stack[self.frame()][self.coil()][self.slice()]

        wl = self.window_level()
        self.ax.clear()
        kwargs = {}
        self.image = \
            self.ax.imshow(self.stack[self.frame()][self.coil()][self.slice()], 
                           vmin=wl[0],
                           vmax=wl[1],
                           cmap=pyplot.get_cmap('gray'),
                           animated=animated)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        if animated is False:
            self.canvas.draw_idle()

    def animation(self):
        if self.animate.isChecked() is False:
            self.timer.stop()
            self.timer = None
        
        dimName = self.animDim.currentText()

        def increment():
            v = self.selected[dimName].value()
            m = self.selected[dimName].maximum()
            self.selected[dimName].setValue((v+1) % m)

        self.timer = QtCore.QTimer(this)
        self.timer.interval = 100
        self.timer.timeout.connect(increment)
        timer.start()
