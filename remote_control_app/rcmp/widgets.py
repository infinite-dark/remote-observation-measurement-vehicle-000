from PySide6.QtGui import QColor, QPainter, QBrush, QPixmap
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QLabel, QWidget, QHBoxLayout, QTableWidget, QHeaderView, \
    QTableWidgetItem, QProgressBar
from PySide6.QtCore import Qt, QSize, QPointF, Signal

from rcmp.workers import VideoReceiver, TelemetryReceiver, CommandTransmitter


class JoystickPanel(QWidget):

    valueChanged = Signal(tuple)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(240, 240)
        self.joystick_position = QPointF(0, 0)
        self.dragging = False

    def paintEvent(self, event):
        painter = QPainter(self)

        brush = QBrush(QColor(200, 200, 200))
        painter.setBrush(brush)
        painter.drawRect(self.rect())

        if self.dragging:
            brush.setColor(QColor(100, 100, 250))
        else:
            brush.setColor(QColor(150, 150, 150))

        painter.setBrush(brush)
        painter.drawEllipse(self.joystick_position, 10, 10)

        painter.setPen(QColor(0, 0, 0))
        painter.drawText(self.width() // 2 - 12, 15, "|^|")
        painter.drawText(self.width() // 2 - 12, self.height() - 10, "|v|")
        painter.drawText(5, self.height() // 2 + 5, "<<")
        painter.drawText(self.width() - 20, self.height() // 2 + 5, ">>")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.joystick_position = self.rect().center()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.updateJoystickPosition(event.position())

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.updateJoystickPosition(event.position())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.joystick_position = self.rect().center()
            self.update()
            self.valueChanged.emit((0, 0))

    def updateJoystickPosition(self, position):
        rect = self.rect()
        center = rect.center()

        x_percent = ((position.x() - center.x()) / (rect.width() / 2)) * 100
        y_percent = ((center.y() - position.y()) / (rect.height() / 2)) * 100

        x_percent = int(max(min(x_percent, 100), -100))
        y_percent = int(max(min(y_percent, 100), -100))

        self.joystick_position = position
        self.update()

        self.valueChanged.emit((x_percent, y_percent))


class ReadoutsTable(QTableWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(240, 500)
        self.setColumnCount(2)
        self.setHorizontalHeaderLabels(["Parameter", "Value"])
        self.setSortingEnabled(False)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.data_items = dict()

    def updateData(self, data: dict):
        for key, index in zip(data.keys(), range(len(data.keys()))):
            if key not in self.data_items.keys():
                name = QTableWidgetItem(str(key))
                value = QTableWidgetItem(str(data[key]))

                self.insertRow(index)
                self.setItem(index, 0, name)
                self.setItem(index, 1, value)

                self.data_items[key] = value
            else:
                item = self.item(index, 1)
                item.setText(str(data[key]))


class RCMPApp(QMainWindow):

    def __init__(self, ip: str):
        super().__init__()
        self.setWindowTitle("RCMP-ENV")
        self.setFixedSize(1600, 720)

        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.mainLayout = QHBoxLayout(self.centralWidget)

        self.videoLabel = QLabel("image", self.centralWidget)
        self.videoLabel.setFixedSize(QSize(1280, 720))

        self.videoReceiver = VideoReceiver(ip)
        self.videoReceiver.frameReceived.connect(self.updateFrame)

        self.interfaceHolder = QWidget(self.centralWidget)
        self.holderLayout = QVBoxLayout()
        self.interfaceHolder.setLayout(self.holderLayout)

        self.table = ReadoutsTable(self)
        self.holderLayout.addWidget(self.table)

        self.telemetryReceiver = TelemetryReceiver(ip, 6000)
        self.telemetryReceiver.telemetryReceived.connect(self.updateData)

        self.batteryIndicator = QProgressBar()
        self.batteryIndicator.setFixedHeight(30)
        self.batteryIndicator.setValue(0)
        self.holderLayout.addWidget(self.batteryIndicator)

        self.joystick = JoystickPanel(self)
        self.holderLayout.addWidget(self.joystick)

        self.commandTransmitter = CommandTransmitter(ip, 5000)
        self.joystick.valueChanged.connect(self.commandTransmitter.updateCommand)

        self.mainLayout.addWidget(self.videoLabel)
        self.mainLayout.addWidget(self.interfaceHolder)

        self.centerWindow()

        self.videoReceiver.start()
        self.telemetryReceiver.start()
        self.commandTransmitter.start()

    def updateFrame(self, frame: QPixmap):
        self.videoLabel.setPixmap(frame)

    def updateData(self, data: dict):
        self.batteryIndicator.setValue(int(data["Battery [%]"]))
        data.pop("Battery [%]")
        self.table.updateData(data)

    def centerWindow(self):
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, event):
        self.videoReceiver.stop()
        self.videoReceiver.wait()

        self.telemetryReceiver.stop()
        self.telemetryReceiver.wait()

        self.commandTransmitter.stop()
        self.commandTransmitter.wait()

        event.accept()
