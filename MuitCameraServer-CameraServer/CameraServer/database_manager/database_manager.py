from .database_connector import DatabaseConnector
from .models import AuditoryNote, AuditoryJournalNote, CameraCabJournalNote, Base
from PyQt5.QtCore import QObject
import os

class DatabaseManager(DatabaseConnector):
    def __init__(self, settings_file, parent=None):
        # Use database path from settings or default to current directory
        db_path = getattr(settings_file, 'db_path', 'camera_server.db')
        super().__init__(db_path, parent)
        self.settings_file = settings_file
        self._initialized = False
    
    def open_connection(self):
        # Open connection and create tables if needed
        result = super().open_connection()
        if result and not self._initialized:
            self.create_tables()
            self._initialized = True
        return result
    
    def create_tables(self):
        """Create all tables from SQLAlchemy models"""
        try:
            Base.metadata.create_all(self.engine)
            print("[DATABASEMANAGER] Tables created successfully")
        except Exception as e:
            print(f"[DATABASEMANAGER] Error creating tables: {e}")

    def insert_note(self, note):
        session = self.Session()
        session.add(note)
        session.commit()
        session.close()

    def update_note(self, note):
        session = self.Session()
        session.merge(note)
        session.commit()
        session.close()

    def delete_note(self, note_class, note_id):
        session = self.Session()
        note = session.query(note_class).filter_by(id=note_id).first()
        if note:
            session.delete(note)
            session.commit()
        session.close()

    def get_notes(self, note_class):
        session = self.Session()
        notes = session.query(note_class).all()
        session.close()
        return notes

    def execute_query(self, query_str, params=None):
        session = self.Session()
        result = session.execute(query_str, params or {})
        session.close()
        return result