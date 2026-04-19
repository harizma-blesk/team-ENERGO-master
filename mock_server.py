"""
Заглушка Python TCP сервера для тестирования PHP сервера.
Слушает порт 2222, всегда отвечает что кабинет 301 свободен.

Запуск:
    python mock_server.py

Остановка: Ctrl+C
"""

import socket
import struct
import json

HOST = '127.0.0.1'
PORT = 2222

def handle_client(conn, addr):
    print(f"[+] Подключение от {addr}")
    try:
        # Читаем 4 байта — длина JSON
        raw_len = conn.recv(4)
        if len(raw_len) < 4:
            print("[-] Неполный заголовок")
            return

        length = struct.unpack('>I', raw_len)[0]  # big-endian uint32
        print(f"[<] Ожидаем {length} байт")

        # Читаем JSON
        data = b''
        while len(data) < length:
            chunk = conn.recv(length - len(data))
            if not chunk:
                break
            data += chunk

        request = json.loads(data.decode('utf-8'))
        print(f"[<] Запрос: {request}")

        # Всегда отвечаем что кабинет 301 свободен
        response = {
            "id":      request.get("id", 1),
            "cabinet": 301,
            "status":  "answer"
        }

        response_bytes = json.dumps(response, ensure_ascii=False).encode('utf-8')
        response_len   = struct.pack('>I', len(response_bytes))  # big-endian uint32

        conn.sendall(response_len + response_bytes)
        print(f"[>] Ответ: {response}")

    except Exception as e:
        print(f"[!] Ошибка: {e}")
    finally:
        conn.close()
        print(f"[-] Соединение закрыто")


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen(5)
        print(f"[*] Заглушка запущена на {HOST}:{PORT}")
        print(f"[*] Всегда отвечает: cabinet=301, status=answer")
        print(f"[*] Ctrl+C для остановки\n")

        while True:
            conn, addr = server.accept()
            handle_client(conn, addr)


if __name__ == '__main__':
    main()
