-- SQL файл для базы данных камер
-- Используется для laravel-server

CREATE TABLE IF NOT EXISTS auditory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    number INTEGER,
    corpus TEXT,
    category TEXT
);

CREATE TABLE IF NOT EXISTS auditory_journal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aud_id INTEGER NOT NULL,
    day_of_week INTEGER,
    start_time TEXT,
    end_time TEXT,
    duration INTEGER,
    time_status INTEGER,
    FOREIGN KEY (aud_id) REFERENCES auditory(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS subjects (
    id_sub INTEGER PRIMARY KEY AUTOINCREMENT,
    sub_name TEXT UNIQUE NOT NULL,
    teacher_name TEXT
);

-- Вставка данных в auditory
INSERT OR IGNORE INTO auditory (name, number, corpus, category) VALUES
('Кабинет 101', 101, 'Корпус А', 'лаборатория'),
('Кабинет 102', 102, 'Корпус А', 'лаборатория'),
('Кабинет 201', 201, 'Корпус Б', 'класс'),
('Кабинет 202', 202, 'Корпус Б', 'класс');

-- Вставка данных в subjects
INSERT OR IGNORE INTO subjects (sub_name, teacher_name) VALUES
('Математика', 'Иванов И.И., Петров П.П.'),
('Физика', 'Сидоров С.С.'),
('Химия', 'Смирнова М.М.'),
('История', 'Федоров Ф.Ф.'),
('Русский язык', 'Егорова Е.Е.');

-- Вставка данных в auditory_journal
INSERT OR IGNORE INTO auditory_journal (aud_id, day_of_week, start_time, end_time, duration, time_status) VALUES
(1, 1, '09:00', '10:30', 90, 1),
(2, 1, '10:45', '12:15', 90, 1),
(1, 2, '14:00', '15:30', 90, 1),
(2, 2, '15:45', '17:15', 90, 1),
(1, 3, '09:00', '10:30', 90, 1),
(2, 3, '10:45', '12:15', 90, 1),
(3, 1, '11:00', '12:30', 90, 1),
(4, 2, '13:00', '14:30', 90, 1),
(1, 4, '09:00', '10:30', 90, 1),
(2, 4, '10:45', '12:15', 90, 1),
(3, 5, '11:00', '12:30', 90, 1),
(4, 6, '13:00', '14:30', 90, 1);
