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
        // ==================== АУДИТОРИИ (Только А и Б) ====================
        $auditoriesData = [
            ['name' => 'А-301', 'number' => 301, 'corpus' => 'А', 'category' => 'lecture'],
            ['name' => 'А-302', 'number' => 302, 'corpus' => 'А', 'category' => 'lecture'],
            ['name' => 'А-401', 'number' => 401, 'corpus' => 'А', 'category' => 'lecture'],
            ['name' => 'А-101', 'number' => 101, 'corpus' => 'А', 'category' => 'lecture'],
            ['name' => 'Б-205', 'number' => 205, 'corpus' => 'Б', 'category' => 'lab'],
            ['name' => 'Б-305', 'number' => 305, 'corpus' => 'Б', 'category' => 'lab'],
            ['name' => 'Б-101', 'number' => 101, 'corpus' => 'Б', 'category' => 'lab'],
        ];

        $auditories = [];
        foreach ($auditoriesData as $data) {
            // Автоматически вычисляем этаж: берем первую цифру из number (например, 301 -> 3)
            $data['floor'] = (int)substr((string)$data['number'], 0, 1);
            
            $auditories[$data['name']] = Auditory::create($data);
        }

        // ==================== ПРЕДМЕТЫ ====================
        $subjectsData = [
            ['sub_name' => 'Высшая математика',           'teacher_name' => 'Иванов И.И.'],
            ['sub_name' => 'Физика',                      'teacher_name' => 'Петров П.П., Сидорова А.А.'],
            ['sub_name' => 'Программирование на Python',  'teacher_name' => 'Смирнов С.С.'],
            ['sub_name' => 'Базы данных',                 'teacher_name' => 'Каримов А.Б.'],
        ];

        foreach ($subjectsData as $sub) {
            Subject::create($sub);
        }

        // ==================== ТЕСТОВОЕ РАСПИСАНИЕ (Без Д) ====================
        $schedule = [
            ['aud_name' => 'А-301', 'day' => 1, 'start' => '08:00', 'end' => '09:30'],
            ['aud_name' => 'А-302', 'day' => 1, 'start' => '09:30', 'end' => '11:00'],
            ['aud_name' => 'Б-205', 'day' => 1, 'start' => '11:00', 'end' => '12:40'],
            ['aud_name' => 'А-401', 'day' => 1, 'start' => '14:10', 'end' => '15:30'],
            ['aud_name' => 'Б-305', 'day' => 2, 'start' => '08:00', 'end' => '09:30'],
            ['aud_name' => 'А-301', 'day' => 2, 'start' => '11:00', 'end' => '12:40'],
            ['aud_name' => 'Б-101', 'day' => 2, 'start' => '12:40', 'end' => '14:10'],
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

        echo "\n✅ Сидер успешно выполнен!\n";
        echo "   • Корпус Д удален.\n";
        echo "   • Поле 'floor' заполнено автоматически.\n";
    }

    private function minutesBetween(string $start, string $end): int
    {
        [$sh, $sm] = array_map('intval', explode(':', $start));
        [$eh, $em] = array_map('intval', explode(':', $end));
        return ($eh * 60 + $em) - ($sh * 60 + $sm);
    }
}