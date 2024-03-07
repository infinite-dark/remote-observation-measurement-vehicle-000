import cv2
import socket
import json

from PySide6.QtCore import Signal, QThread
from PySide6.QtGui import QImage, QPixmap


class VideoReceiver(QThread):

    frameReceived = Signal(QPixmap)

    def __init__(self, ip: str, port: int = 4000):
        super().__init__()

        self.cap = cv2.VideoCapture(f"tcpclientsrc host={ip} port={port} ! decodebin ! videoconvert ! appsink", cv2.CAP_GSTREAMER)
        self.running = False

    def run(self) -> None:
        if self.cap.isOpened():
            self.running = True

            while self.running:
                ret, frame = self.cap.read()
                if ret:
                    h, w, ch = frame.shape
                    image = QImage(frame.data, w, h, ch * w, QImage.Format_BGR888)
                    pixmap = QPixmap.fromImage(image)

                    self.frameReceived.emit(pixmap)
                else:
                    self.running = False

            self.cap.release()

    def stop(self):
        self.running = False


class TelemetryReceiver(QThread):

    telemetryReceived = Signal(dict)

    def __init__(self, ip: str, port: int = 5000):
        super().__init__()

        self.ip = ip
        self.port = port

        self.running = False

    def run(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((self.ip, self.port))
                self.running = True
            except socket.error:
                pass
            else:
                while self.running:
                    size = s.recv(5)
                    size = int(size)

                    data = s.recv(size)
                    data = data.decode("ascii")

                    telemetry = json.loads(data)
                    self.telemetryReceived.emit(telemetry)

    def stop(self):
        self.running = False


class CommandTransmitter(QThread):

    def __init__(self, ip: str, port: int = 6000, freq: int = 60):
        super().__init__()

        self.ip = ip
        self.port = port

        self.command = "cs000000"

        self.running = False
        self.delay = int(1000/freq)

    def run(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((self.ip, self.port))
                self.running = True
            except socket.error:
                pass
            else:
                while self.running:
                    cmd = self.command.encode("ascii")
                    s.sendall(cmd)

                    self.msleep(self.delay)

    def updateCommand(self, params: tuple[int]):
        command = ""

        steer_val = params[0]
        motor_var = params[1]

        if steer_val < 0:
            command += "l"
        elif steer_val > 0:
            command += "r"
        else:
            command += "c"

        if motor_var > 0:
            command += "f"
        elif motor_var < 0:
            command += "r"
        else:
            command += "s"

        steer_str = str(abs(steer_val))
        steer_str = (3 - len(steer_str)) * "0" + steer_str
        command += steer_str

        motor_str = str(abs(motor_var))
        motor_str = (3 - len(motor_str)) * "0" + motor_str
        command += motor_str

        self.command = command

    def stop(self):
        self.running = False
