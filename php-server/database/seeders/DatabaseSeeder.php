<?php

namespace Database\Seeders;

use App\Models\Auditory;
use App\Models\AuditoryJournal;
use App\Models\Subject;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class DatabaseSeeder extends Seeder
{
    use WithoutModelEvents;

    public function run(): void
    {
        // ==================== АУДИТОРИИ ====================
        $auditoriesData = [
            ['name' => 'А-301', 'number' => 301, 'corpus' => 'А', 'category' => 'lecture'],
            ['name' => 'А-302', 'number' => 302, 'corpus' => 'А', 'category' => 'lecture'],
            ['name' => 'А-401', 'number' => 401, 'corpus' => 'А', 'category' => 'lecture'],
            ['name' => 'Б-205', 'number' => 205, 'corpus' => 'Б', 'category' => 'lab'],
            ['name' => 'Б-305', 'number' => 305, 'corpus' => 'Б', 'category' => 'lab'],
            ['name' => 'Д-101', 'number' => 101, 'corpus' => 'Д', 'category' => 'lecture'],
            ['name' => 'Д-102', 'number' => 102, 'corpus' => 'Д', 'category' => 'lecture'],
            ['name' => 'Д-201', 'number' => 201, 'corpus' => 'Д', 'category' => 'lab'],
            ['name' => 'А-101', 'number' => 101, 'corpus' => 'А', 'category' => 'lecture'],
            ['name' => 'Б-101', 'number' => 101, 'corpus' => 'Б', 'category' => 'lab'],
        ];

        $auditories = [];
        foreach ($auditoriesData as $data) {
            $auditories[$data['name']] = Auditory::create($data);
        }

        // ==================== ПРЕДМЕТЫ ====================
        $subjectsData = [
            ['sub_name' => 'Высшая математика',           'teacher_name' => 'Иванов И.И.'],
            ['sub_name' => 'Физика',                      'teacher_name' => 'Петров П.П., Сидорова А.А.'],
            ['sub_name' => 'Программирование на Python',  'teacher_name' => 'Смирнов С.С.'],
            ['sub_name' => 'Английский язык',             'teacher_name' => 'Johnson E.'],
            ['sub_name' => 'История Казахстана',          'teacher_name' => 'Абдуллаева М.К.'],
            ['sub_name' => 'Базы данных',                 'teacher_name' => 'Каримов А.Б.'],
            ['sub_name' => 'Алгоритмы и структуры данных', 'teacher_name' => 'Ахметов Д.К.'],
        ];

        foreach ($subjectsData as $sub) {
            Subject::create($sub);
        }

        // ==================== ТЕСТОВОЕ РАСПИСАНИЕ ====================
        $schedule = [
            // Понедельник (1)
            ['aud_name' => 'А-301', 'day' => 1, 'start' => '08:00', 'end' => '09:30'],
            ['aud_name' => 'А-302', 'day' => 1, 'start' => '09:30', 'end' => '11:00'],
            ['aud_name' => 'Б-205', 'day' => 1, 'start' => '11:00', 'end' => '12:40'],
            ['aud_name' => 'Д-101', 'day' => 1, 'start' => '12:40', 'end' => '14:10'],
            ['aud_name' => 'А-401', 'day' => 1, 'start' => '14:10', 'end' => '15:30'],

            // Вторник (2)
            ['aud_name' => 'Б-305', 'day' => 2, 'start' => '08:00', 'end' => '09:30'],
            ['aud_name' => 'Д-102', 'day' => 2, 'start' => '09:30', 'end' => '11:00'],
            ['aud_name' => 'А-301', 'day' => 2, 'start' => '11:00', 'end' => '12:40'],
            ['aud_name' => 'Б-101', 'day' => 2, 'start' => '12:40', 'end' => '14:10'],

            // Среда (3)
            ['aud_name' => 'Д-201', 'day' => 3, 'start' => '08:00', 'end' => '09:30'],
            ['aud_name' => 'А-302', 'day' => 3, 'start' => '09:30', 'end' => '11:00'],
            ['aud_name' => 'А-401', 'day' => 3, 'start' => '11:00', 'end' => '12:40'],
            ['aud_name' => 'Б-205', 'day' => 3, 'start' => '14:10', 'end' => '15:30'],

            // Четверг (4)
            ['aud_name' => 'Д-101', 'day' => 4, 'start' => '08:00', 'end' => '09:30'],
            ['aud_name' => 'Б-305', 'day' => 4, 'start' => '09:30', 'end' => '11:00'],
            ['aud_name' => 'А-101', 'day' => 4, 'start' => '12:40', 'end' => '14:10'],

            // Пятница (5)
            ['aud_name' => 'А-301', 'day' => 5, 'start' => '08:00', 'end' => '09:30'],
            ['aud_name' => 'Д-102', 'day' => 5, 'start' => '09:30', 'end' => '11:00'],
            ['aud_name' => 'Б-101', 'day' => 5, 'start' => '11:00', 'end' => '12:40'],
            ['aud_name' => 'А-401', 'day' => 5, 'start' => '14:10', 'end' => '15:30'],
        ];

        $journalAdded = 0;
        foreach ($schedule as $item) {
            $auditory = $auditories[$item['aud_name']] ?? null;

            if ($auditory) {
                $duration = $this->minutesBetween($item['start'], $item['end']);

                AuditoryJournal::create([
                    'aud_id'     => $auditory->id,
                    'dayOfWeek'  => $item['day'],
                    'startTime'  => $item['start'],
                    'endTime'    => $item['end'],
                    'duration'   => $duration,
                    'timeStatus' => 1,
                ]);
                $journalAdded++;
            }
        }

        echo "\n✅ Сеeder успешно выполнен!\n";
        echo "   • Аудиторий добавлено: " . count($auditories) . "\n";
        echo "   • Предметов добавлено: " . count($subjectsData) . "\n";
        echo "   • Записей в расписании добавлено: " . $journalAdded . "\n";
    }

    /**
     * Вспомогательная функция для расчёта длительности
     */
    private function minutesBetween(string $start, string $end): int
    {
        [$sh, $sm] = array_map('intval', explode(':', $start));
        [$eh, $em] = array_map('intval', explode(':', $end));
        return ($eh * 60 + $em) - ($sh * 60 + $sm);
    }
}