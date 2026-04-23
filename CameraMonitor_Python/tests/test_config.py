"""
Тесты для конфигурационной системы
"""

import unittest
import tempfile
from pathlib import Path
from src.core.config import Config


class TestConfig(unittest.TestCase):
    """Тесты для класса Config"""

    def setUp(self):
        """Создание временного конфиг файла для тестов"""
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False)
        self.temp_config.write("""[Database]
path=test.db

[Camera]
startRtcp=rtsp://test:pass@test.com
cameraIndex=1

[UDP]
IP_PythonServer=127.0.0.1
IP_Port_Listen=5000

[NEUROMODEL]
WeightsPath=models/test.pt
ConfThreshold=0.7

[TCP_Servers]
IP_PHP=192.168.1.100
PORT_PHP=3333

[Logging]
level=DEBUG
""")
        self.temp_config.close()
        self.config_path = self.temp_config.name

    def tearDown(self):
        """Очистка после тестов"""
        Path(self.config_path).unlink(missing_ok=True)

    def test_config_loading(self):
        """Тест загрузки конфигурации"""
        config = Config(self.config_path)

        # Проверяем основные свойства
        self.assertEqual(config.db_path, "test.db")
        self.assertEqual(config.camera_rtsp_url, "rtsp://test:pass@test.com")
        self.assertEqual(config.camera_index, 1)
        self.assertEqual(config.udp_server_ip, "127.0.0.1")
        self.assertEqual(config.udp_listen_port, 5000)
        self.assertEqual(config.yolo_weights_path, "models/test.pt")
        self.assertEqual(config.yolo_conf_threshold, 0.7)
        self.assertEqual(config.PHP_server_ip, "192.168.1.100")
        self.assertEqual(config.PHP_server_port, 3333)
        self.assertEqual(config.log_level, "DEBUG")

    def test_config_defaults(self):
        """Тест значений по умолчанию"""
        # Создаем пустой конфиг файл
        empty_config = tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False)
        empty_config.write("[Database]\npath=default.db\n")
        empty_config.close()

        config = Config(empty_config.name)

        # Проверяем значения по умолчанию
        self.assertEqual(config.camera_index, 0)
        self.assertEqual(config.udp_listen_port, 5000)
        self.assertEqual(config.yolo_conf_threshold, 0.5)
        self.assertEqual(config.window_width, 1200)

        Path(empty_config.name).unlink(missing_ok=True)

    def test_config_reload(self):
        """Тест перезагрузки конфигурации"""
        config = Config(self.config_path)

        # Изменяем файл
        with open(self.config_path, 'w') as f:
            f.write("""[Database]
path=reloaded.db
""")

        config.reload()
        self.assertEqual(config.db_path, "reloaded.db")

    def test_config_sections(self):
        """Тест получения секций"""
        config = Config(self.config_path)

        db_section = config.get_section("Database")
        self.assertEqual(db_section["path"], "test.db")

        nonexistent = config.get_section("NonExistent")
        self.assertEqual(nonexistent, {})


if __name__ == "__main__":
    unittest.main()