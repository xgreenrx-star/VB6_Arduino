"""Serial Plotter widget for VB2Arduino IDE."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QColor
import pyqtgraph as pg
import collections

class SerialPlotter(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Serial Plotter")
        self.setMinimumSize(600, 320)
        layout = QVBoxLayout(self)
        # Controls
        controls = QHBoxLayout()
        label = QLabel("Y Range:")
        label.setMinimumWidth(60)
        controls.addWidget(label)
        self.yrange_combo = QComboBox()
        self.yrange_combo.addItems(["Auto", "0-255", "-1 to 1", "-5 to 5", "-10 to 10", "-100 to 100", "Custom..."])
        self.yrange_combo.currentIndexChanged.connect(self._update_yrange)
        # Prevent the combo from expanding too wide and potentially overlapping other widgets
        self.yrange_combo.setMaximumWidth(140)
        self.yrange_combo.setToolTip("Select Y axis range for plotted data")
        controls.addWidget(self.yrange_combo)
        controls.addStretch()
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear)
        self.clear_btn.setMaximumWidth(90)
        controls.addWidget(self.clear_btn)

        # Overflow menu for narrow windows
        from PyQt6.QtWidgets import QToolButton, QMenu
        self.plot_more_btn = QToolButton()
        self.plot_more_btn.setText("⋯")
        self.plot_more_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.plot_more_menu = QMenu()
        self.plot_more_menu.addAction("Clear", self.clear)
        self.plot_more_btn.setMenu(self.plot_more_menu)
        self.plot_more_btn.setVisible(False)
        controls.addWidget(self.plot_more_btn)

        layout.addLayout(controls)
        # Plot widget
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.addLegend()
        layout.addWidget(self.plot_widget)
        # Data
        self.max_points = 500
        self.data = collections.defaultdict(lambda: collections.deque(maxlen=self.max_points))
        self.curves = {}
        self.colors = [QColor("#0072BD"), QColor("#D95319"), QColor("#EDB120"), QColor("#7E2F8E"), QColor("#77AC30"), QColor("#4DBEEE"), QColor("#A2142F")]
        # Timer for UI refresh will be created when the widget is shown (avoid background work during tests)
        self.timer = None
        self.yrange = None
        # Responsive behaviour threshold (px)
        self._responsive_threshold = 360

    def showEvent(self, event):
        super().showEvent(event)
        if self.timer is None:
            self.timer = QTimer(self)
            self.timer.timeout.connect(self._refresh_plot)
            self.timer.setInterval(50)
            self.timer.start()
        elif not self.timer.isActive():
            self.timer.start()

    def hideEvent(self, event):
        super().hideEvent(event)
        if self.timer and self.timer.isActive():
            self.timer.stop()
        # Responsive behaviour: update visibility of overflow menu on resize
        self._responsive_threshold = 360

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_responsive_layout()

    def _update_responsive_layout(self):
        w = self.width()
        if w < self._responsive_threshold:
            self.clear_btn.setVisible(False)
            self.plot_more_btn.setVisible(True)
        else:
            self.clear_btn.setVisible(True)
            self.plot_more_btn.setVisible(False)
    def add_sample(self, label, value):
        self.data[label].append(value)
        if label not in self.curves:
            color = self.colors[len(self.curves) % len(self.colors)]
            curve = self.plot_widget.plot(pen=pg.mkPen(color, width=2), name=label)
            self.curves[label] = curve
    def clear(self):
        self.data.clear()
        for curve in self.curves.values():
            curve.clear()
        self.curves.clear()
    def _refresh_plot(self):
        for label, curve in self.curves.items():
            y = list(self.data[label])
            x = list(range(len(y)))
            curve.setData(x, y)
        if self.yrange:
            self.plot_widget.setYRange(*self.yrange)
        else:
            self.plot_widget.enableAutoRange(axis=pg.ViewBox.YAxis)
    def _update_yrange(self):
        text = self.yrange_combo.currentText()
        if text == "Auto":
            self.yrange = None
        elif text == "0-255":
            self.yrange = (0, 255)
        elif text == "-1 to 1":
            self.yrange = (-1, 1)
        elif text == "-5 to 5":
            self.yrange = (-5, 5)
        elif text == "-10 to 10":
            self.yrange = (-10, 10)
        elif text == "-100 to 100":
            self.yrange = (-100, 100)
        else:
            # Custom: prompt user (not implemented)
            self.yrange = None
        self._refresh_plot()
