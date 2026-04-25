<?php

namespace App\Services;

use App\Models\Auditory;
use App\Models\AuditoryJournal;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;

class ScheduleService
{
    public function __construct(private SubjectService $subjectService) {}

    /**
     * Parse schedule rows and save to DB.
     *
     * @param array $dto ['fileName' => string, 'sheet' => string, 'rows' => string[][]]
     */
    public function saveSchedule(array $dto): array
{
    $fileName = $dto['fileName'] ?? '';
    $rows     = $dto['rows'] ?? [];
    // Очищаем журнал перед импортом
    AuditoryJournal::truncate();
    Auditory::truncate();;

    Log::info("ScheduleService: saving schedule from {$fileName}");

    $auditoriesAdded = 0;
    $camerasAdded    = 0;
    $journalAdded    = 0;
    $rowsSkipped     = 0;

    if (count($rows) < 2) {
        Log::warning("ScheduleService: no data rows in {$fileName}");
    } else {
        $header = $rows[0];

        $colDay      = $this->findColumn($header, 'день');
        $colTime     = $this->findColumn($header, 'время');
        $colSubject  = $this->findColumn($header, 'предмет');
        $colTeacher  = $this->findColumn($header, 'преподаватель');
        $colRoom     = $this->findColumn($header, 'кабинет');
        $colCapacity = $this->findColumn($header, 'вместимость');
        $colCamIp    = $this->findColumn($header, 'камера_ip');
        $colCamPort  = $this->findColumn($header, 'камера_порт');
        $colCamLogin = $this->findColumn($header, 'камера_логин');
        $colCamPass  = $this->findColumn($header, 'камера_пароль');
        $colCamName  = $this->findColumn($header, 'камера_название');

        Log::info("Columns: day={$colDay}, time={$colTime}, subject={$colSubject}, teacher={$colTeacher}, room={$colRoom}");
        Log::info("Camera columns: ip={$colCamIp}, port={$colCamPort}, login={$colCamLogin}, pass={$colCamPass}, name={$colCamName}");

        if ($colDay < 0 || $colTime < 0 || $colRoom < 0) {
            Log::error('ScheduleService: missing required columns (день/время/кабинет)');
        } else {
            $cache = Auditory::all()->keyBy('name')->toArray();

            DB::beginTransaction();
            try {
                for ($i = 1; $i < count($rows); $i++) {
                    $row     = $rows[$i];
                    $dayStr  = $this->safeGet($row, $colDay);
                    $timeStr = $this->safeGet($row, $colTime);
                    $roomStr = $this->safeGet($row, $colRoom);

                    if (empty(trim((string)$dayStr))) { $rowsSkipped++; continue; }
                    if (empty(trim((string)$roomStr))) { $rowsSkipped++; continue; }

                    $dayOfWeek = $this->parseDayOfWeek((string)$dayStr);
                    if ($dayOfWeek === 0) { $rowsSkipped++; continue; }

                   $roomName = trim((string)$roomStr);
                    $corpus   = $this->extractCorpus($roomName);

                    // ── Аудитория ─────────────────────────────────────────
                    $capacityVal = $colCapacity >= 0 ? (int)$this->safeGet($row, $colCapacity) : null;

                    if (!isset($cache[$roomName])) {
                        $number   = $this->extractNumber($roomName);
                        $floor    = $number ? intdiv($number, 100) : null;
                        $auditory = Auditory::create([
                            'name'     => $roomName,
                            'number'   => $number,
                            'corpus'   => $corpus,
                            'floor'    => $floor,
                            'category' => null,
                            'capacity' => $capacityVal ?: null,
                        ]);
                        $cache[$roomName] = $auditory->toArray();
                        $auditoriesAdded++;
                    } elseif ($capacityVal > 0 && empty($cache[$roomName]['capacity'])) {
                        Auditory::where('id', $cache[$roomName]['id'])->update(['capacity' => $capacityVal]);
                        $cache[$roomName]['capacity'] = $capacityVal;
                    }

                    $audId = $cache[$roomName]['id'];                     // ── Камера ────────────────────────────────────────────
                    if ($colCamIp >= 0) {
                        $camIp = trim((string)($this->safeGet($row, $colCamIp) ?? ''));

                        if ($camIp !== '') {
                            $camPort  = $colCamPort  >= 0 ? (int)$this->safeGet($row, $colCamPort)          : 554;
                            $camLogin = $colCamLogin >= 0 ? trim((string)$this->safeGet($row, $colCamLogin)) : null;
                            $camPass  = $colCamPass  >= 0 ? trim((string)$this->safeGet($row, $colCamPass))  : null;
                            $camName  = $colCamName  >= 0 ? trim((string)$this->safeGet($row, $colCamName))  : "Camera_{$roomName}";

                            $rtspUrl = ($camLogin && $camPass)
                                ? "rtsp://{$camLogin}:{$camPass}@{$camIp}:{$camPort}/stream"
                                : "rtsp://{$camIp}:{$camPort}/stream";

                            $created = \App\Models\Camera::updateOrCreate(
                                ['auditory_id' => $audId],
                                [
                                    'name'     => $camName ?: "Camera_{$roomName}",
                                    'ip'       => $camIp,
                                    'port'     => $camPort ?: 554,
                                    'login'    => $camLogin ?: null,
                                    'password' => $camPass  ?: null,
                                    'rtsp_url' => $rtspUrl,
                                ]
                            );

                            if ($created->wasRecentlyCreated) {
                                $camerasAdded++;
                                Log::debug("Created camera: {$camName} → {$camIp}:{$camPort}");
                            } else {
                                Log::debug("Updated camera: {$camName} → {$camIp}:{$camPort}");
                            }
                        }
                    }

                    // ── Предмет ───────────────────────────────────────────
                    $subjectName = $colSubject >= 0 ? $this->safeGet($row, $colSubject) : null;
                    $teacherName = $colTeacher >= 0 ? $this->safeGet($row, $colTeacher) : null;

                    if (!empty(trim((string)$subjectName))) {
                        try {
                            $this->subjectService->addOrUpdateSubject(
                                trim((string)$subjectName),
                                $teacherName ? trim((string)$teacherName) : null
                            );
                        } catch (\Throwable $e) {
                            Log::warning("Failed to save subject: {$e->getMessage()}");
                        }
                    }
                    $subjectVal = $colSubject >= 0 ? trim((string)$this->safeGet($row, $colSubject)) : '';
                        if (empty($subjectVal)) {
                        // свободный слот — в журнал не пишем
                        continue;
                    }

                   // ── Журнал ────────────────────────────────────────────
                    $times = $this->parseTime((string)$timeStr);
                    if ($times !== null) {
                        [$startTime, $endTime] = $times;

                        $journal = AuditoryJournal::firstOrCreate(
                            [
                                'aud_id'    => $audId,
                                'dayOfWeek' => $dayOfWeek,
                                'startTime' => $startTime,
                                'endTime'   => $endTime,
                            ],
                            [
                                'duration'   => $this->minutesBetween($startTime, $endTime),
                                'timeStatus' => 1,
                            ]
                        );

                        if ($journal->wasRecentlyCreated) {
                            $journalAdded++;
                        }
                    } else {
                        Log::warning("Row {$i}: cannot parse time '{$timeStr}'");
                        $rowsSkipped++;
                    }
                }

                DB::commit();
            } catch (\Throwable $e) {
                DB::rollBack();
                throw $e;
            }
        }
    }

    Log::info("Schedule saved: auditories={$auditoriesAdded}, cameras={$camerasAdded}, journal={$journalAdded}, skipped={$rowsSkipped}");

    return [
        'fileName'            => $fileName,
        'sheet'               => $dto['sheet'] ?? null,
        'totalRows'           => max(0, count($rows) - 1),
        'auditoriesAdded'     => $auditoriesAdded,
        'camerasAdded'        => $camerasAdded,
        'journalEntriesAdded' => $journalAdded,
        'rowsSkipped'         => $rowsSkipped,
    ];
}

    public function getAllAuditories(): \Illuminate\Database\Eloquent\Collection
    {
        return Auditory::all();
    }

    public function getAllJournal(): \Illuminate\Database\Eloquent\Collection
    {
        return AuditoryJournal::all();
    }

    public function getJournalByAuditoryId(int $audId): \Illuminate\Database\Eloquent\Collection
    {
        return AuditoryJournal::where('aud_id', $audId)->get();
    }

    // ─── Helpers ──────────────────────────────────────────────────────────────

    private function findColumn(array $header, string $keyword): int
    {
        foreach ($header as $i => $cell) {
            if ($cell !== null && mb_stripos((string)$cell, $keyword) !== false) {
                return $i;
            }
        }
        return -1;
    }

    private function safeGet(array $row, int $index): mixed
    {
        return $row[$index] ?? null;
    }

    private function extractCorpus(string $roomName): ?string
    {
        // Pattern: "А-301", "Б-201"
        if (preg_match('/^([А-ЯA-Za-z])\s*[-–—]/u', trim($roomName), $m)) {
            return mb_strtoupper($m[1]);
        }
        // Pattern: "лаб корпус А"
        if (preg_match('/(?:лаб|корпус)\s+([А-ЯA-Za-z])/ui', trim($roomName), $m)) {
            return mb_strtoupper($m[1]);
        }
        return null;
    }

    private function extractNumber(string $roomName): ?int
    {
        if (preg_match('/(\d+)/', $roomName, $m)) {
            return (int)$m[1];
        }
        return null;
    }

    private function parseTime(string $timeStr): ?array
    {
        // Matches "8:00-9:30", "08.00–09.30", "8;00 — 9;30", etc.
        if (!preg_match('/(\d{1,2}[.:;]\d{2})\s*[-–—]\s*(\d{1,2}[.:;]\d{2})/', trim($timeStr), $m)) {
            return null;
        }

        try {
            $start = str_replace(['.', ';'], ':', $m[1]);
            $end   = str_replace(['.', ';'], ':', $m[2]);

            // Pad to HH:mm
            if (strlen($start) === 4) $start = '0' . $start;
            if (strlen($end) === 4)   $end   = '0' . $end;

            // Validate
            \DateTime::createFromFormat('H:i', $start) ?: throw new \InvalidArgumentException("bad start: $start");
            \DateTime::createFromFormat('H:i', $end)   ?: throw new \InvalidArgumentException("bad end: $end");

            return [$start, $end];
        } catch (\Throwable) {
            return null;
        }
    }

    private function minutesBetween(string $start, string $end): int
    {
        [$sh, $sm] = array_map('intval', explode(':', $start));
        [$eh, $em] = array_map('intval', explode(':', $end));
        return ($eh * 60 + $em) - ($sh * 60 + $sm);
    }

    private function parseDayOfWeek(string $day): int
    {
        return match (mb_strtolower(trim($day))) {
            'понедельник' => 1,
            'вторник'     => 2,
            'среда'       => 3,
            'четверг'     => 4,
            'пятница'     => 5,
            'суббота'     => 6,
            'воскресенье' => 7,
            default       => 0,
        };
    }

    private function saveCamera(int $auditoryId, array $data): void
    {
        \App\Models\Camera::updateOrCreate(
            ['auditory_id' => $auditoryId],
            [
                'name'     => $data['name'],
                'ip'       => $data['ip'],
                'port'     => $data['port'],
                'login'    => $data['login'],
                'password' => $data['password'],
            ]
        );
    }
    /**
 * Обновить статус занятости аудитории (вызывается из ScheduleController)
 */
public function updateAuditoryStatus(string $name, int $status): bool
{
    // Обязательно используем trim, чтобы избежать проблем с лишними пробелами из Python
    $roomName = trim($name);

    $auditory = Auditory::where('name', $roomName)->first();

    if ($auditory) {
        // Здесь мы обновляем поле is_occupied. 
        // Убедитесь, что это поле есть в вашей таблице 'auditories'!
        $auditory->is_occupied = ($status === 1); 
        $saved = $auditory->save();

        Log::info("Status updated for {$roomName}: " . ($status ? 'Occupied' : 'Free'));
        return $saved;
    }

    Log::warning("ScheduleService: Auditory '{$roomName}' not found for status update.");
    return false;
}
}
