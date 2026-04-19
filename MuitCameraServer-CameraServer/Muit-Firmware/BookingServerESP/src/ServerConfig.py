import json
import os

class ServerConfig:
    def __init__(self):
        self.data = {
            'magic': 0xB2,
            'serverIp': '',
            'serverPort': 0,
            'wifiSsid': '',
            'wifiPass': ''
        }
        self.config_file = 'config.json'

    def load(self, defaultIp, defaultPort, defaultSsid, defaultPass):
        try:
            with open(self.config_file, 'r') as f:
                self.data = json.load(f)
            if self.data.get('magic') != 0xB2:
                raise ValueError
            print(f"[CONFIG] Server: {self.data['serverIp']}:{self.data['serverPort']} | WiFi SSID: {self.data['wifiSsid']}")
        except:
            print("[CONFIG] Config file missing or invalid, writing defaults")
            self.data['magic'] = 0xB2
            self.data['serverIp'] = defaultIp
            self.data['serverPort'] = defaultPort
            self.data['wifiSsid'] = defaultSsid
            self.data['wifiPass'] = defaultPass
            self._write()

    def saveServer(self, newIp, newPort):
        self.data['serverIp'] = newIp
        self.data['serverPort'] = newPort
        self.data['magic'] = 0xB2
        self._write()
        print(f"[CONFIG] Server saved: {newIp}:{newPort}")

    def saveWifi(self, newSsid, newPass):
        self.data['wifiSsid'] = newSsid
        self.data['wifiPass'] = newPass
        self.data['magic'] = 0xB2
        self._write()
        print(f"[CONFIG] WiFi saved: SSID={newSsid}")

    def Ip(self):
        return self.data['serverIp']

    def Port(self):
        return self.data['serverPort']

    def WifiSsid(self):
        return self.data['wifiSsid']

    def WifiPass(self):
        return self.data['wifiPass']

    def _write(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.data, f)
