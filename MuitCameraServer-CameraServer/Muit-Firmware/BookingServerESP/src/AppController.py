import network
import time
from CabinetStorage import CabinetStorage
from ServerConfig import ServerConfig
from EspWebServer import EspWebServer
from TCP_Manager import TCP_Manager
from Constants import SERVER_QT_IP, SERVER_QT_PORT, WIFI_DEFAULT_SSID, WIFI_DEFAULT_PASS, AP_SSID, AP_PASSWORD
from Dictionary import C2ESPpacket

class AppController:
    def __init__(self):
        self.storage = CabinetStorage()
        self.config = ServerConfig()
        self.webServer = EspWebServer(self.storage, self.config)
        self.tcpClient = TCP_Manager()
        self.lastKnownIp = ""
        self.lastKnownPort = 0

    def setup(self):
        print("Starting setup...")
        time.sleep(1)

        self.config.load(SERVER_QT_IP, SERVER_QT_PORT, WIFI_DEFAULT_SSID, WIFI_DEFAULT_PASS)

        # WiFi mode AP_STA
        sta = network.WLAN(network.STA_IF)
        ap = network.WLAN(network.AP_IF)
        ap.active(True)

        self.webServer.StartAP(AP_SSID, AP_PASSWORD)
        self.webServer.begin()

        self.tcpClient.ConnectWiFi(self.config.WifiSsid(), self.config.WifiPass())

        self.lastKnownIp = self.config.Ip()
        self.lastKnownPort = self.config.Port()

        self.tcpClient.Connect(self.config.Ip(), self.config.Port())

    def loop(self):
        self.webServer.handle()

        if self.config.Ip() != self.lastKnownIp or self.config.Port() != self.lastKnownPort:
            print(f"[APP] Server changed: {self.lastKnownIp}:{self.lastKnownPort} -> {self.config.Ip()}:{self.config.Port()}")
            self.lastKnownIp = self.config.Ip()
            self.lastKnownPort = self.config.Port()
            self.tcpClient.Disconnect()
            time.sleep(0.1)
            self.tcpClient.Connect(self.config.Ip(), self.config.Port())

        self.tcpClient.Process()

        while self.tcpClient.HasPackets():
            packet = self.tcpClient.GetNextPacket()
            self.storage.UpdateOrAddPacket(packet)
            self.webServer.setLastRequest(packet.CabNum())
            print(f"Updated: Cab {packet.CabNum()}, Status: {'BUSY' if packet.IsBusy() else 'FREE'}")
