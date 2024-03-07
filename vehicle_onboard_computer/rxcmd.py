import socket
import serial
import json
from threading import Thread
from time import sleep, perf_counter


class MotorDriver:

    def __init__(self, port: str = "/dev/ttyS7", baudrate: int = 115200, freq: int = 60):
        self.serial = serial.Serial(port, baudrate)

        self.delay_time = 0
        if freq > 0:
            self.delay_time = 1/freq

        self.worker = Thread(target=self.run, daemon=True)
        self.running = False

        self.steer_val = 0
        self.steer_dir = 0

        self.mot_val = 0
        self.mot_dir = 0

        self.steer_bit_map = {
            "c": 0b00000000,
            "l": 0b00001000,
            "r": 0b00000100
        }

        self.mot_bit_map = {
            "s": 0b00000000,
            "f": 0b00000010,
            "r": 0b00000001
        }

    def start(self) -> None:
        self.running = True
        self.worker.start()

    def run(self) -> None:
        while self.running:
            command_byte = (self.steer_dir | self.mot_dir).to_bytes(1, "big")
            steer_val_byte = self.steer_val.to_bytes(1, "big")
            mot_val_byte = self.mot_val.to_bytes(1, "big")

            t = perf_counter()
            self.serial.write(command_byte)
            self.serial.write(steer_val_byte)
            self.serial.write(mot_val_byte)
            t = perf_counter() - t

            delay = self.delay_time - t / 1000
            if delay > 0:
                sleep(delay)

        self.serial.close()

    def update(self, params: str) -> None:
        if params != "stop":
            steer_dir = params[0]
            steer_val = int(params[2:5])

            mot_dir = params[1]
            mot_val = int(params[5:])

            self.steer_dir = self.steer_bit_map[steer_dir]
            self.steer_val = steer_val

            self.mot_dir = self.mot_bit_map[mot_dir]
            self.mot_val = mot_val
        else:
            self.steer_dir = 0b10000000
            self.mot_dir = 0b00000000

            self.steer_val = 0
            self.mot_val = 0

    def stop(self):
        self.running = False
        self.worker.join()


class Receiver:

    def __init__(self, ip: str, port: int = 5000, serial: str = "/dev/ttyS8"):
        self.ip = ip
        self.port = port
        self.connected = False
        
        self.motor_driver = MotorDriver(serial)
        self.running = False

    def start(self):
        self.motor_driver.start()
        self.running = True
        self.run()

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.ip, self.port))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            while self.running:
                s.listen(1)
                conn, addr = s.accept()

                self.connected = True
                while self.connected:
                    data = conn.recv(8)

                    if not data:
                        self.motor_driver.update("stop")
                        self.connected = False
                        conn.close()
                        break

                    data = data.decode("ascii")
                    self.motor_driver.update(data)

    def stop(self):
        self.connected = False
        self.running = False
        self.motor_driver.stop()

if __name__ == "__main__":
    rx = Receiver("192.168.0.33")
    rx.start()

