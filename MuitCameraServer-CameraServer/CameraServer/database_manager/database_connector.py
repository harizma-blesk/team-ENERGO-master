from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from PyQt5.QtCore import QObject, pyqtSignal
import time
import os

class DatabaseConnector(QObject):
    signalDatabaseConnected = pyqtSignal()
    signalDatabaseNotConnected = pyqtSignal()

    def __init__(self, db_path, parent=None):
        super().__init__(parent)
        self.db_path = db_path if db_path else "camera_server.db"
        self.engine = None
        self.Session = None
        self.reconnection_count = 0

    def open_connection(self):
        try:
            # Create connection string for SQLite
            db_uri = f"sqlite:///{os.path.abspath(self.db_path)}"
            self.engine = create_engine(db_uri, echo=False)
            self.Session = sessionmaker(bind=self.engine)
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            print(f"[DATABASECONNECTOR] Successfully connected to database: {self.db_path}")
            self.reconnection_count = 0
            self.signalDatabaseConnected.emit()
            return True
        except Exception as e:
            print(f"[DATABASECONNECTOR] Error: connection not established! {e}")
            self.reconnection_count += 1
            if self.reconnection_count <= 4:
                time.sleep(2)
                return self.open_connection()
            self.signalDatabaseNotConnected.emit()
            return False

    def close_connection(self):
        if self.engine:
            self.engine.dispose()
        self.reconnection_count = 0