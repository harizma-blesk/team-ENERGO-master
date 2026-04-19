from Dictionary import C2ESPpacket

class CabinetStorage:
    def __init__(self):
        self.cabinet = []

    def UpdateOrAddPacket(self, packet):
        for p in self.cabinet:
            if p.CabNum() == packet.CabNum():
                p.SetId(packet.Id())
                p.SetIsBusy(packet.IsBusy())
                return
        self.cabinet.append(packet)

    def GetAllCabinets(self):
        return self.cabinet

    def GetPacketByCab(self, cab_num):
        for packet in self.cabinet:
            if packet.CabNum() == cab_num:
                return packet
        empty = C2ESPpacket()
        empty.SetCabNum(cab_num)
        return empty
