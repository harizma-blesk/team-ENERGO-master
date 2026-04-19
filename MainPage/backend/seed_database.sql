BEGIN;

-- Очищаем только те таблицы, которые точно создала Prisma
TRUNCATE TABLE "ScheduleItem", "StudentProfile", "Subject", "Group", "User" RESTART IDENTITY CASCADE;

-- Удаляем таблицы для Laravel, если они вдруг остались от старых версий (необязательно)
DROP TABLE IF EXISTS "AuditoryJournal" CASCADE;
DROP TABLE IF EXISTS "Auditory" CASCADE;

-- 1. ТЕПЕРЬ СОЗДАЕМ ИХ ЗАНОВО (так как их нет в Prisma)
CREATE TABLE "Auditory" (
                            id SERIAL PRIMARY KEY,
                            name TEXT UNIQUE NOT NULL,
                            number INTEGER,
                            corpus TEXT,
                            category TEXT
);

CREATE TABLE "AuditoryJournal" (
                                   id SERIAL PRIMARY KEY,
                                   aud_id INTEGER NOT NULL REFERENCES "Auditory"(id) ON DELETE CASCADE,
                                   day_of_week INTEGER,
                                   start_time TEXT,
                                   end_time TEXT,
                                   duration INTEGER,
                                   time_status INTEGER
);
-- 2. ЗАПОЛНЕНИЕ ПОЛЬЗОВАТЕЛЕЙ (User)
-- Пароли в примере - это заглушки (хэши). Роли: STUDENT, TEACHER, ADMIN
INSERT INTO "User" (id, email, "passwordHash", role, status, locale, "createdAt", "updatedAt")
VALUES
    ('user_admin_01', 'admin@energo.kz', '$2b$10$ExmplHashAdmin', 'ADMIN', 'ACTIVE', 'ru', NOW(), NOW()),
    ('user_teacher_01', 'teacher1@energo.kz', '$2b$10$ExmplHashTeacher', 'TEACHER', 'ACTIVE', 'ru', NOW(), NOW()),
    ('user_student_01', 'student1@energo.kz', '$2b$10$ExmplHashStudent', 'STUDENT', 'ACTIVE', 'ru', NOW(), NOW());

-- 3. ЗАПОЛНЕНИЕ ГРУПП (Group)
INSERT INTO "Group" (id, code, name, semester, "createdAt")
VALUES
    ('group_global', 'GLOBAL', 'Общая группа', '1', NOW()),
    ('group_it_24', 'IT-24', 'Информационные технологии 2024', '2', NOW());

-- 4. ЗАПОЛНЕНИЕ ПРЕДМЕТОВ (Subject)
-- Здесь id текстовые, как того требует ваша схема Prisma
INSERT INTO "Subject" (id, name, teacher_name, "externalSubjectCode", description, "createdAt")
VALUES
    ('sub_math', 'Математика', 'Иванов И.И., Петров П.П.', 'laravel_1', 'Высшая математика и анализ', NOW()),
    ('sub_phys', 'Физика', 'Сидоров С.С.', 'laravel_2', 'Общая физика', NOW()),
    ('sub_chem', 'Химия', 'Смирнова М.М.', 'laravel_3', 'Органическая химия', NOW()),
    ('sub_hist', 'История', 'Федоров Ф.Ф.', 'laravel_4', 'История Казахстана', NOW()),
    ('sub_lang', 'Русский язык', 'Егорова Е.Е.', 'laravel_5', 'Академическое письмо', NOW());

-- 5. ЗАПОЛНЕНИЕ ПРОФИЛЯ СТУДЕНТА (StudentProfile)
INSERT INTO "StudentProfile" (id, "userId", "fullName", "studentNo", "groupId", "createdAt")
VALUES
    ('st_prof_01', 'user_student_01', 'Кирилл Энерго', 'ID-777888', 'group_it_24', NOW());

-- 6. ЗАПОЛНЕНИЕ РАСПИСАНИЯ (ScheduleItem)
-- Связываем предметы с группами
INSERT INTO "ScheduleItem" (id, "externalScheduleId", "subjectId", "groupId", "startsAt", "endsAt", room, "syncedAt")
VALUES
    ('sched_01', 'ext_001', 'sub_math', 'group_it_24', NOW() + interval '1 day', NOW() + interval '1 day 90 min', 'Кабинет 101', NOW()),
    ('sched_02', 'ext_002', 'sub_phys', 'group_it_24', NOW() + interval '2 day', NOW() + interval '2 day 90 min', 'Кабинет 102', NOW());

-- 7. ЗАПОЛНЕНИЕ АУДИТОРИЙ (Ваши доп. таблицы для Laravel)
INSERT INTO "Auditory" (name, number, corpus, category)
VALUES
    ('Кабинет 101', 101, 'Корпус А', 'лаборатория'),
    ('Кабинет 102', 102, 'Корпус А', 'лаборатория'),
    ('Кабинет 201', 201, 'Корпус Б', 'класс');

-- 8. ЗАПОЛНЕНИЕ ЖУРНАЛА АУДИТОРИЙ
INSERT INTO "AuditoryJournal" (aud_id, day_of_week, start_time, end_time, duration, time_status)
VALUES
    (1, 1, '09:00', '10:30', 90, 1),
    (2, 1, '10:45', '12:15', 90, 1),
    (1, 2, '14:00', '15:30', 90, 1);

COMMIT;