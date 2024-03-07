import socket
import serial
import json
from threading import Thread
from time import sleep, perf_counter

import busio
import board
import adafruit_ltr390
from adafruit_bme280 import basic as adafruit_bme280


class SensorHat:

    def __init__(self, sda=board.SDA, scl=board.SCL, port="/dev/ttyS7", baudrate=115200):
        i2c = busio.I2C(scl, sda)

        self.bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, 0x76)
        self.ltr390 = adafruit_ltr390.LTR390(i2c)
        self.battery = serial.Serial(port, baudrate)
        
        self.readouts = dict()

    def setup(self) -> None:
        self.bme280.sea_level_pressure = 1013.25
        self.battery.reset_output_buffer()

    def readSensors(self) -> dict:
        self.readouts["Temperature [*C]"] = round(self.bme280.temperature, 2)
        self.readouts["Humidity [%]"] = round(self.bme280.relative_humidity, 2)
        self.readouts["Pressure [hPa]"] = round(self.bme280.pressure, 2)
        self.readouts["UV Index"] = self.ltr390.uvi
        self.readouts["Ambient Light [lux]"] = self.ltr390.light
        
        if self.battery.in_waiting >= 3:
            self.readouts["Battery [%]"] = self.battery.readline().rstrip().decode("ascii")
            self.battery.reset_output_buffer()

        return self.readouts


class Transmitter:

    def __init__(self, ip: str, port: int = 6000):
        self.ip = ip
        self.port = port
        self.connected = False
        
        self.sensor_hat = SensorHat()
        self.running = False
    
    def start(self):
        self.sensor_hat.setup()
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
                try:
                    while self.connected:
                        data = self.sensor_hat.readSensors()

                        data = json.dumps(data)
                        data = data.encode("ascii")

                        size = str(len(data))
                        header = (5 - len(size)) * "0" + str(size)
                        header = header.encode("ascii")

                        conn.sendall(header)
                        conn.sendall(data)
                except socket.error:
                    conn.close()
                    self.connected = False


if __name__ == "__main__":
    tx = Transmitter("192.168.0.33")
    tx.start()

