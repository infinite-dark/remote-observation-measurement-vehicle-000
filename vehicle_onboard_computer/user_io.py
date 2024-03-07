import gpiod
import busio
from board import SDA, SCL
import adafruit_ssd1306

from PIL import Image, ImageDraw, ImageFont
from time import sleep, perf_counter
import psutil


def parseHostapdConf(path: str = "/home/radxa/hostapd.conf"):
	with open(path, "r") as hostapd:
		for line in hostapd.readlines():
			if line.startswith("ssid=") or line.startswith("wpa_passphrase="):
				idx = line.index("=")
				content = line[idx + 1:]
				
			if line.startswith("ssid="):
				ssid = content
			elif line.startswith("wpa_passphrase="):
				password = content

	return ssid, password


def parseUdhcpdConf(path: str = "/home/radxa/udhcpd.conf"):
	with open(path, "r") as udhcpd:
		for line in udhcpd.readlines():
			if line.startswith("opt router"):
				router_line = line.split()
				ip = router_line[2]
				break
	return ip


def isProcessActiveByName(process_name):
	for process in psutil.process_iter(["name"]):
		try:
			if process_name.lower() in process.info["name"].lower():
				return "ACTIVE"
		except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
			pass
	return "INACTIVE"


def isProcessActiveWithArgument(exec_name, argument):
	for proc in psutil.process_iter(attrs=["cmdline", "name"]):
		try:
			if exec_name in proc.info["name"] and any(argument in cmd for cmd in proc.info["cmdline"]):
				return "ACTIVE"
		except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
			continue
	return "INACTIVE"


class Display(adafruit_ssd1306.SSD1306_I2C):

	def __init__(self, w: int = 128, h: int = 32, i2c=busio.I2C(SCL, SDA)):
		super().__init__(w, h, i2c)

		self.w, self.h = w, h
		self.clear()

		self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 14)
		self.text1, self.text2 = "", ""

	def writeText(self, text: str, line: int):
		image = Image.new("1", (self.w, self.h))
		draw = ImageDraw.Draw(image)

		if line == 0:
			self.text1 = text
			kept_line = self.text2
			kept_pos = 17
		elif line == 1:
			self.text2 = text
			kept_line = self.text1
			kept_pos = 1

		draw.text((0, kept_pos), kept_line, font=self.font, fill=255)
		draw.text((0, 17 * line), text, font=self.font, fill=255)

		self.image(image)
		self.show()

	def clear(self):
		self.text1, self.text2 = "", ""
		self.fill(0)
		self.show()


class InputHandler:

	def __init__(self):
		self.display = Display()
		
		self.button_chip = "/dev/gpiochip3"
		self.button_line = 5
		
		self.page = -1
		
		self.ssid, self.passwd = parseHostapdConf()
		self.ip = parseUdhcpdConf()
		
		self.ports = {"CAM": 4000, "TX": 5000, "RX": 6000}
	
	def handleInput(self):
		self.nextPage()

		with gpiod.Chip(self.button_chip) as chip:
		
			config = {
				self.button_line: gpiod.line_settings.LineSettings(
					direction=gpiod.line.Direction.INPUT,
					edge_detection=gpiod.line.Edge.RISING,
					bias=gpiod.line.Bias.PULL_DOWN
				)
			}
			
			line_request = chip.request_lines(consumer="", config=config)
			while True:
				if line_request.wait_edge_events(timeout=0.5):
					events = line_request.read_edge_events()
					if len(events):
						self.nextPage()
	
	def nextPage(self):
		self.page += 1
		if self.page > 5:
			self.page = 0
		
		self.display.clear()
		self.display.writeText("WORKING...", 0)
		
		if self.page == 0:
			self.display.writeText(f"SSID: {self.ssid}", 0)
			self.display.writeText(f"PSWD: {self.passwd}", 1)
			
		elif self.page == 1:
			hostapd_status = isProcessActiveByName("hostapd")
			udhcpd_status = "UNKNOWN"
			
			self.display.writeText(f"WLAN: {hostapd_status}", 0)
			self.display.writeText(f"DHCP: {udhcpd_status}", 1)
			
		elif self.page == 2:
			tx_status = isProcessActiveWithArgument("python3", "txsens.py")
			rx_status = isProcessActiveWithArgument("python3", "rxcmd.py")
			
			self.display.writeText(f"SENTX: {tx_status}", 0)
			self.display.writeText(f"CMDRX: {rx_status}", 1)
			
		elif self.page == 3:
			self.display.writeText("TCP PORT", 0)
			self.display.writeText(f"CAM = {self.ports['CAM']}", 1)
			
		elif self.page == 4:
			self.display.writeText("TCP PORT", 0)
			self.display.writeText(f"TX = {self.ports['TX']}", 1)
			
		elif self.page == 5:
			self.display.writeText("TCP PORT", 0)
			self.display.writeText(f"RX = {self.ports['RX']}", 1)


if __name__ == "__main__":
	ih = InputHandler()
	ih.handleInput()

