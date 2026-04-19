import socket
import json
import time
import network
import machine
from WebPage import index_html
from AdminPage import admin_html

class EspWebServer:
    def __init__(self, storage, config):
        self.storage = storage
        self.config = config
        self.lastCabNum = 0
        self.server_sock = None

    def setLastRequest(self, num):
        self.lastCabNum = num

    def StartAP(self, ssid="ESP_Admin_Panel", password="12345678"):
        ap = network.WLAN(network.AP_IF)
        ap.active(True)
        ap.config(essid=ssid, password=password)
        print("AP IP:", ap.ifconfig()[0])

    def begin(self):
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.bind(('0.0.0.0', 80))
        self.server_sock.listen(5)
        print("Web Server started. Admin: http://<AP_IP>/admin")

    def handle(self):
        try:
            client_sock, addr = self.server_sock.accept()
            request = client_sock.recv(1024).decode('utf-8')
            if not request:
                client_sock.close()
                return
            lines = request.split('\n')
            if lines:
                method, path, _ = lines[0].split()
                self._handle_request(client_sock, method, path, request)
            client_sock.close()
        except OSError:
            pass

    def _handle_request(self, sock, method, path, request):
        if path == '/':
            self._send_response(sock, 200, 'text/html', index_html)
        elif path == '/api/status':
            data = {
                'last': self.lastCabNum,
                'cabinets': [{'num': p.CabNum(), 'isBusy': p.IsBusy()} for p in self.storage.GetAllCabinets()]
            }
            self._send_response(sock, 200, 'application/json', json.dumps(data))
        elif path == '/api/config':
            data = {
                'serverIp': self.config.Ip(),
                'serverPort': self.config.Port(),
                'wifiSsid': self.config.WifiSsid()
            }
            self._send_response(sock, 200, 'application/json', json.dumps(data))
        elif path == '/admin':
            self._send_response(sock, 200, 'text/html', admin_html)
        elif path == '/admin/save-server' and method == 'POST':
            # Parse POST data
            body = self._parse_post(request)
            ip = body.get('ip', '')
            port = int(body.get('port', 0))
            if not ip or not (1 <= port <= 65535):
                self._send_response(sock, 400, 'application/json', '{"ok":false}')
                return
            self.config.saveServer(ip, port)
            self._send_response(sock, 200, 'application/json', '{"ok":true}')
        elif path == '/admin/save-wifi' and method == 'POST':
            body = self._parse_post(request)
            ssid = body.get('ssid', '')
            password = body.get('pass', '')
            if not ssid:
                self._send_response(sock, 400, 'application/json', '{"ok":false}')
                return
            self.config.saveWifi(ssid, password)
            self._send_response(sock, 200, 'application/json', '{"ok":true}')
        elif path == '/admin/reboot' and method == 'POST':
            self._send_response(sock, 200, 'application/json', '{"ok":true}')
            time.sleep(0.3)
            machine.reset()
        else:
            self._send_response(sock, 404, 'text/plain', 'Not Found')

    def _send_response(self, sock, status, content_type, body):
        response = f'HTTP/1.1 {status} OK\r\nContent-Type: {content_type}\r\n\r\n{body}'
        sock.send(response.encode('utf-8'))

    def _parse_post(self, request):
        # Simple POST parser
        parts = request.split('\r\n\r\n')
        if len(parts) > 1:
            body = parts[1]
            params = {}
            for pair in body.split('&'):
                if '=' in pair:
                    k, v = pair.split('=', 1)
                    params[k] = v
            return params
        return {}
