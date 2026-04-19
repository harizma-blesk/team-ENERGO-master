class C2ESPpacket:
    def __init__(self):
        self.id = 0
        self.cabNum = 0
        self.isBusy = False

    def Id(self):
        return self.id

    def CabNum(self):
        return self.cabNum

    def IsBusy(self):
        return self.isBusy

    def SetId(self, newId):
        self.id = newId

    def SetCabNum(self, newCabNum):
        self.cabNum = newCabNum

    def SetIsBusy(self, newIsBusy):
        self.isBusy = newIsBusy
