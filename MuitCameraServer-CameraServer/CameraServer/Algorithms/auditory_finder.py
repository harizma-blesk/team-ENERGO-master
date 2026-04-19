from PyQt5.QtCore import QObject, pyqtSignal, QTime
from database_manager.models import AuditoryNote, AuditoryJournalNote, FindCabinetReq, TimePart

class AuditoryFinder(QObject):
    signalAuditoryFound = pyqtSignal(object)  # AuditoryNote
    signalCheckAgain = pyqtSignal()
    signalAuditoryNotFound = pyqtSignal(str)

    def __init__(self, database_manager, parent=None):
        super().__init__(parent)
        self.database = database_manager

    def find_auditory(self, target_corpus, start_time, day_of_week, longness):
        if not self.database:
            return AuditoryNote()

        end_time = start_time.addSecs(longness * 60)

        time_part = TimePart(start_time, end_time, day_of_week, longness)
        auditory = AuditoryNote(corpus=target_corpus)
        req = FindCabinetReq(time_part, auditory)

        # Execute the complex SQL query
        query = """
        SET NOCOUNT ON;
        SET XACT_ABORT ON;
        BEGIN TRAN;
        DECLARE @InsertedId TABLE (id INT);

        INSERT INTO dbo.auditory_journal (aud_id, startTime, endTime, dayOfWeek, timeStatus, duration)
        OUTPUT INSERTED.aud_id INTO @InsertedId(id)
        SELECT TOP (1) a.id, :startTime, :endTime, :dayOfWeek, 2, :duration
        FROM dbo.auditory AS a WITH (UPDLOCK, HOLDLOCK)
        LEFT JOIN dbo.camera_cab_journal AS cam ON a.id = cam.id_cab
        WHERE (cam.is_busy = 0 OR cam.is_busy IS NULL)
          AND NOT EXISTS (
            SELECT 1 FROM dbo.auditory_journal AS aj
            WHERE aj.aud_id = a.id
              AND aj.dayOfWeek = :dayOfWeek
              AND aj.startTime < :endTime
              AND aj.endTime > :startTime
              AND aj.timeStatus IN (0, 1, 2)
        )
        ORDER BY CASE WHEN a.corpus = :targetCorpus THEN 0 ELSE 1 END, a.number;

        SELECT a.id, a.name, a.number, a.corpus, a.category
        FROM dbo.auditory a
        INNER JOIN @InsertedId i ON a.id = i.id;
        COMMIT;
        """

        params = {
            'startTime': start_time.toString('hh:mm:ss'),
            'endTime': end_time.toString('hh:mm:ss'),
            'dayOfWeek': day_of_week,
            'duration': longness,
            'targetCorpus': target_corpus
        }

        result = self.database.execute_query(query, params)
        row = result.fetchone()
        if row:
            note = AuditoryNote(id=row[0], name=row[1], number=row[2], corpus=row[3], category=row[4])
            return note
        return AuditoryNote()

    def complete_booking(self, note, start_time, day_of_week, longness):
        if not self.database:
            return

        end_time = start_time.addSecs(longness * 60)

        query = """
        UPDATE dbo.auditory_journal
        SET timeStatus = 1
        WHERE aud_id = :aud_id
          AND dayOfWeek = :dayOfWeek
          AND startTime = :startTime
          AND endTime = :endTime
          AND timeStatus = 2;
        """

        params = {
            'aud_id': note.id,
            'dayOfWeek': day_of_week,
            'startTime': start_time.toString('hh:mm:ss'),
            'endTime': end_time.toString('hh:mm:ss')
        }

        self.database.execute_query(query, params)

    def clear_temporary_bookings(self):
        if not self.database:
            return

        query = "DELETE FROM auditory_journal WHERE timeStatus = 1"
        self.database.execute_query(query)