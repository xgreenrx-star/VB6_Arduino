# pin_diagram_overlay.py
# Pin diagram overlay widget for VB2Arduino IDE
# Provides a non-modal, resizable overlay showing microcontroller pinouts


from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsSimpleTextItem, QToolButton, QHBoxLayout, QGraphicsItem, QGraphicsRectItem
from PyQt6.QtCore import Qt, QSize, QPointF
import csv, os

class PinDiagramOverlay(QWidget):
    def __init__(self, board_name="esp32-s3-devkitm-1", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pin Diagram")
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint)
        self.setMinimumSize(400, 300)
        self.resize(600, 400)
        self.board_name = board_name
        self._init_ui()
        self.load_board_diagram(board_name)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        header = QHBoxLayout()
        self.title_label = QLabel("Pin Diagram: " + self.board_name)
        self.close_btn = QToolButton()
        self.close_btn.setText("✕")
        self.close_btn.clicked.connect(self.close)
        header.addWidget(self.title_label)
        header.addStretch()
        header.addWidget(self.close_btn)
        layout.addLayout(header)
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(self.view.renderHints() | Qt.RenderHint.Antialiasing)
        layout.addWidget(self.view, 1)

    def load_board_diagram(self, board_name):
        self.scene.clear()
        self.title_label.setText(f"Pin Diagram: {board_name}")
        csv_path = self._get_csv_path(board_name)
        if not os.path.exists(csv_path):
            self.scene.addText("Pin diagram not found.")
            return
        pins = []
        with open(csv_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if not row or row[0].startswith('#') or len(row) < 4:
                    continue
                pin_name, x, y, label = row[0], float(row[1]), float(row[2]), row[3]
                pins.append((pin_name, x, y, label))
        # Draw board outline
        outline = QGraphicsRectItem(30, 20, 220, 360)
        outline.setBrush(Qt.GlobalColor.lightGray)
        outline.setZValue(-1)
        self.scene.addItem(outline)
        # Draw pins
        self.pin_items = []
        for pin_name, x, y, label in pins:
            pin_item = PinEllipseItem(x, y, 18, 18, label)
            pin_item.setToolTip(f"{pin_name}: {label}")
            self.scene.addItem(pin_item)
            self.pin_items.append(pin_item)
        # Draw pin labels
        for pin_name, x, y, label in pins:
            text = QGraphicsSimpleTextItem(label)
            text.setPos(x + 20, y - 2)
            self.scene.addItem(text)
        self.view.setSceneRect(self.scene.itemsBoundingRect().adjusted(-20, -20, 40, 40))

    def _get_csv_path(self, board_name):
        # Map known board IDs to CSV filenames
        board_map = {
            # ESP32
            "esp32-s3-devkitm-1": "pinout_esp32-s3-devkitm-1.csv",
            "esp32-s3-devkitc-1": "pinout_esp32-s3-devkitm-1.csv",
            "esp32dev": "pinout_esp32dev.csv",
            # Arduino AVR
            "uno": "pinout_arduino-uno.csv",
            "megaatmega2560": "pinout_megaatmega2560.csv",
            "nanoatmega328": "pinout_nanoatmega328.csv",
            "leonardo": "pinout_leonardo.csv",
            "micro": "pinout_micro.csv",
            "pro16MHzatmega328": "pinout_pro16MHzatmega328.csv",
            # Arduino ARM
            "nano_33_iot": "pinout_nano_33_iot.csv",
            "due": "pinout_due.csv",
            "mkr1000": "pinout_mkr1000.csv",
            "mkrwifi1010": "pinout_mkrwifi1010.csv",
            "zero": "pinout_zero.csv",
            # Raspberry Pi Pico
            "pico": "pinout_pico.csv",
        }
        # Try direct match
        csv_file = board_map.get(board_name)
        if csv_file:
            return os.path.join("resources", csv_file)
        # Fallback: try partial match
        for key, fname in board_map.items():
            if board_name and key in board_name:
                return os.path.join("resources", fname)
        # Fallback: unknown
        return os.path.join("resources", "pinout_unknown.csv")

    def set_board(self, board_name):
        self.board_name = board_name
        self.load_board_diagram(board_name)

# Custom QGraphicsEllipseItem for interactive pin highlighting
class PinEllipseItem(QGraphicsEllipseItem):
    def __init__(self, x, y, w, h, label):
        super().__init__(x, y, w, h)
        self.setBrush(Qt.GlobalColor.yellow)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setAcceptHoverEvents(True)
        self.label = label

    def hoverEnterEvent(self, event):
        self.setBrush(Qt.GlobalColor.red)
        QGraphicsEllipseItem.hoverEnterEvent(self, event)

    def hoverLeaveEvent(self, event):
        self.setBrush(Qt.GlobalColor.yellow)
        QGraphicsEllipseItem.hoverLeaveEvent(self, event)
