from abc import ABC, abstractmethod
from collections import deque
from Dictionary import C2ESPpacket

class TCP_Client(ABC):
    def __init__(self):
        self.PacketStorage = deque()

    @abstractmethod
    def Connect(self, ip, port):
        pass

    @abstractmethod
    def Disconnect(self):
        pass

    @abstractmethod
    def SendPacket(self, packet):
        pass

    @abstractmethod
    def ReceivePacket(self):
        pass

    def HasPackets(self):
        return len(self.PacketStorage) > 0

    def GetNextPacket(self):
        if self.HasPackets():
            return self.PacketStorage.popleft()
        return None
