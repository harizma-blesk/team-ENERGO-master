import network
import socket
import time
import struct
from TCP_Client import TCP_Client
from Dictionary import C2ESPpacket

class TCP_Manager(TCP_Client):
    def __init__(self):
        super().__init__()
        self.client = None
        self.server_ip = ""
        self.server_port = 0
        self.sta = network.WLAN(network.STA_IF)
        self.sta.active(True)

    def ConnectWiFi(self, ssid, passw):
        print("Connecting to WiFi...")
        self.sta.connect(ssid, passw)
        attempts = 0
        while not self.sta.isconnected() and attempts < 20:
            time.sleep(0.5)
            print(".")
            attempts += 1
        if self.sta.isconnected():
            print("\nConnected to Router!")
            print("STA IP:", self.sta.ifconfig()[0])
        else:
            print("\nFailed to connect to Router.")

    def Connect(self, ip, port):
        self.server_ip = ip
        self.server_port = port
        print(f"Attempting connection to {ip}:{port}...")
        try:
            self.client = socket.socket()
            self.client.connect((ip, port))
            self.client.setblocking(False)  # Non-blocking for reading
            print("CONNECTED to Qt Server!")
            return True
        except OSError as e:
            print(f"Connection failed. Reason: {e}")
            return False

    def Disconnect(self):
        if self.client:
            self.client.close()
            self.client = None

    def SendPacket(self, packet):
        if not self.client:
            return False
        id = packet.Id()
        cabNum = packet.CabNum()
        isBusy = 1 if packet.IsBusy() else 0
        data = struct.pack('<i i B', id, cabNum, isBusy)
        try:
            self.client.send(data)
            return True
        except:
            return False

    def ReceivePacket(self):
        if not self.client:
            return False
        try:
            data = self.client.recv(9)
            if len(data) < 9:
                return False
            id, cabNum, isBusy = struct.unpack('<i i B', data)
            p = C2ESPpacket()
            p.SetId(id)
            p.SetCabNum(cabNum)
            p.SetIsBusy(isBusy != 0)
            print(f"Received Packet - ID: {id}, CabNum: {cabNum}, IsBusy: {'BUSY' if p.IsBusy() else 'FREE'}")
            self.PacketStorage.append(p)
            return True
        except:
            return False

    def IsConnected(self):
        return self.client is not None

    def Process(self):
        if not self.sta.isconnected():
            return
        if not self.IsConnected():
            print("Reconnecting to Qt Server...")
            if self.Connect(self.server_ip, self.server_port):
                print("Connected to Qt Server!")
            else:
                time.sleep(2)
                return
        # Read all available packets
        while self.ReceivePacket():
            pass
