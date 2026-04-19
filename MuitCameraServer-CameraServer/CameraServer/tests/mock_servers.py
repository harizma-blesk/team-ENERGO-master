import socket
import json
import struct
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse


class MockPHPHandler(BaseHTTPRequestHandler):
    """Mock PHP server request handler"""
    
    def do_POST(self):
        """Handle POST requests"""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            data = json.loads(body.decode())
            print(f"[MOCK PHP SERVER] Received: {data}")
            
            # Send response
            response = {
                'status': 'success',
                'message': 'Request processed',
                'data': data
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {'status': 'error', 'message': str(e)}
            self.wfile.write(json.dumps(response).encode())
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass


class MockPHPServer:
    """Mock PHP server using HTTP"""
    
    def __init__(self, host='127.0.0.1', port=8080):
        self.host = host
        self.port = port
        self.server = None
        self.thread = None
        self.running = False
    
    def start(self):
        """Start mock PHP server"""
        self.server = HTTPServer((self.host, self.port), MockPHPHandler)
        self.running = True
        self.thread = threading.Thread(target=self._run_server, daemon=True)
        self.thread.start()
        print(f"[MOCK PHP SERVER] Started on {self.host}:{self.port}")
    
    def _run_server(self):
        """Server loop"""
        while self.running:
            self.server.handle_request()
    
    def stop(self):
        """Stop mock PHP server"""
        self.running = False
        if self.server:
            self.server.server_close()
        print("[MOCK PHP SERVER] Stopped")


class MockJavaServer:
    """Legacy MockJavaServer - replaced by MockPHPServer"""
    
    def __init__(self, host='127.0.0.1', port=2222):
        self.host = host
        self.port = port
        self.running = False
    
    def start(self):
        print(f"[MOCK JAVA SERVER] Deprecated - use MockPHPServer instead")
    
    def stop(self):
        pass
    
    def get_last_request(self):
        return None


class MockESPServer:
    """Mock ESP32 server for testing binary communication"""
    
    def __init__(self, host='127.0.0.1', port=4444):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        self.last_request = None
        self.thread = None
    
    def start(self):
        """Start mock server"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        self.running = True
        
        self.thread = threading.Thread(target=self._run_server, daemon=True)
        self.thread.start()
        
        print(f"[MOCK ESP SERVER] Started on {self.host}:{self.port}")
    
    def _run_server(self):
        """Server loop"""
        while self.running:
            try:
                self.server_socket.settimeout(1)
                client_socket, addr = self.server_socket.accept()
                print(f"[MOCK ESP SERVER] Client connected from {addr}")
                
                # Receive binary data (room_id + busy_status)
                data = client_socket.recv(8)
                if data:
                    room_id, status = struct.unpack('>II', data)
                    self.last_request = {'room_id': room_id, 'busy': status}
                    print(f"[MOCK ESP SERVER] Received: Room {room_id}, Status {status}")
                
                client_socket.close()
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"[MOCK ESP SERVER] Error: {e}")
    
    def stop(self):
        """Stop mock server"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        print("[MOCK ESP SERVER] Stopped")
    
    def get_last_request(self):
        """Get last received request"""
        return self.last_request


class MockRTSPServer:
    """Mock RTSP camera server"""
    
    def __init__(self, camera_id=1, host='127.0.0.1', port=554):
        self.camera_id = camera_id
        self.host = host
        self.port = port
        self.running = False
    
    def start(self):
        """Start mock RTSP server"""
        print(f"[MOCK RTSP SERVER] Camera {self.camera_id} on {self.host}:{self.port}")
        self.running = True
    
    def stop(self):
        """Stop mock RTSP server"""
        self.running = False
        print(f"[MOCK RTSP SERVER] Camera {self.camera_id} stopped")


def test_mock_servers():
    """Test all mock servers"""
    print("=" * 50)
    print("TESTING MOCK SERVERS")
    print("=" * 50)
    
    # Test PHP Server
    print("\n--- Testing Mock PHP Server ---")
    php_server = MockPHPServer()
    php_server.start()
    time.sleep(0.5)
    
    # Simulate client request
    try:
        import requests
        request_data = {'corpus': 'A', 'time': '10:00', 'duration': 60}
        response = requests.post('http://127.0.0.1:8080/api/find_auditory.php', json=request_data, timeout=2)
        print(f"[OK] PHP Server test passed. Response: {response.json()}")
    except Exception as e:
        print(f"[FAIL] PHP Server test failed: {e}")
    
    php_server.stop()
    
    # Test ESP Server
    print("\n--- Testing Mock ESP Server ---")
    esp_server = MockESPServer()
    esp_server.start()
    time.sleep(0.5)
    
    # Simulate client request
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('127.0.0.1', 4444))
        data = struct.pack('>II', 101, 0)  # room_id=101, busy=0
        client.send(data)
        print(f"[OK] ESP Server test passed. Request: Room 101, Status 0")
        client.close()
    except Exception as e:
        print(f"[FAIL] ESP Server test failed: {e}")
    
    esp_server.stop()
    
    print("\n" + "=" * 50)
    print("[OK] ALL MOCK SERVER TESTS PASSED")
    print("=" * 50)


if __name__ == "__main__":
    test_mock_servers()
