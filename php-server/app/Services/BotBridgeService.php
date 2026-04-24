<?php

namespace App\Services;

use App\Helpers\TimeUtil;
use App\Models\Auditory;
use App\Models\AuditoryJournal;
use App\Tcp\PythonTcpClient;
use Illuminate\Support\Facades\Log;

class BotBridgeService
{
    /** Fixed class start times (HH:mm) */
    private const CLASS_START_TIMES = [
        '08:00',
        '09:30',
        '11:00',
        '12:40',
        '14:10',
        '15:30',
    ];

    private const GRACE_PERIOD_MINUTES = 30;

    private const LOCATION_TO_CORPUS = [
        'corp_a' => 'А',
        'corp_b' => 'Б',
        'corp_d' => 'Д',
    ];

    private static int $requestIdCounter = 0;

    public function __construct(private PythonTcpClient $tcpClient) {}

    // ─── Find rooms ───────────────────────────────────────────────────────────

   public function findRooms(array $request): array
{
    $locationId      = $request['location_id'] ?? null;
    $durationMinutes = (int)($request['duration_minutes'] ?? 0);
    $floor           = isset($request['floor']) ? (int)$request['floor'] : null;
    $minCapacity     = (int)($request['filters']['min_capacity'] ?? 0);
    $needProjector   = (bool)($request['filters']['need_projector'] ?? false);

   $startAt = $request['start_at'] ?? null;
    if ($startAt) {
    // Если содержит Z или +XX:XX — это UTC/с timezone, конвертируем в Almaty
    // Если без timezone (от бота) — считаем что уже Almaty
    if (str_contains($startAt, 'Z') || preg_match('/[+-]\d{2}:\d{2}$/', $startAt)) {
        $dt = new \DateTime($startAt);
        $dt->setTimezone(new \DateTimeZone('Asia/Almaty'));
    } else {
        $dt = new \DateTime($startAt, new \DateTimeZone('Asia/Almaty'));
    }
    } else {
    $dt = new \DateTime('now', new \DateTimeZone('Asia/Almaty'));
    }

    $dayOfWeek = (int)$dt->format('N');
    $startTime = $dt->format('H:i');
    $endTime   = (clone $dt)->modify("+{$durationMinutes} minutes")->format('H:i');

    Log::info("findRooms: dayOfWeek={$dayOfWeek}, startTime={$startTime}, endTime={$endTime}");

    $corpus = $this->resolveCorpus($locationId);

    $query = Auditory::where('corpus', $corpus);
    if ($floor !== null)  $query->where('floor', $floor);
    if ($minCapacity > 0) $query->where('capacity', '>=', $minCapacity);
    if ($needProjector)   $query->where('has_projector', 1);

    $auditories = $query->get();

    $freeRooms    = [];
    $alternatives = [];

    foreach ($auditories as $aud) {
        $busy = AuditoryJournal::where('aud_id', $aud->id)
            ->where('dayOfWeek', $dayOfWeek)
            ->where(function ($q) use ($startTime, $endTime) {
                $q->where('startTime', '<', $endTime)
                  ->where('endTime', '>', $startTime);
            })
            ->exists();

                if (!$busy) {
                    $isOccupied = (bool)$aud->is_occupied;
                    $hasCamera  = \App\Models\Camera::where('auditory_id', $aud->id)->exists();

                    $roomData = [
                        'name'          => $aud->name,
                        'location_name' => $corpus,
                        'location_id'   => $locationId,
                        'floor'         => $aud->floor,
                        'capacity'      => $aud->capacity,
                        'schedule_free' => true,
                        'camera_free'   => !$isOccupied,
                        'camera_status' => $hasCamera ? 'online' : 'offline',
                        'auditory_id'   => $aud->id,
                    ];

                    // По расписанию свободно — всегда в free_rooms
                    // camera_free просто информирует что сейчас там есть люди
                    $freeRooms[] = $roomData;
                }
    }

    return [
        'free_rooms'   => $freeRooms,
        'alternatives' => $alternatives,
        'reason'       => empty($freeRooms) ? 'Свободных кабинетов не найдено' : null,
    ];
}

    // ─── Cancel booking ───────────────────────────────────────────────────────

   public function cancelBooking(array $request): array
{
    $auditoryName = $request['auditory_name'] ?? '';
    $corpus       = $request['corpus'] ?? '';
    $startTime    = $request['start_time'] ?? '';
    $endTime      = $request['end_time'] ?? '';
    $dayOfWeek    = isset($request['day_of_week']) ? (int)$request['day_of_week'] : null;

    Log::info('BotBridgeService: cancelBooking', $request);

    if (empty(trim($auditoryName))) {
        return ['status' => 'error', 'message' => 'Не указано имя аудитории.', 'deleted_count' => 0];
    }

    $auditory = Auditory::where('name', $auditoryName)->first();
    if (!$auditory && !empty(trim($corpus))) {
        $auditory = Auditory::where('name', $corpus . '-' . $auditoryName)->first();
    }

    if (!$auditory) {
        Log::warning("cancelBooking: auditory not found: {$auditoryName}");
        return ['status' => 'not_found', 'message' => "Аудитория {$auditoryName} не найдена.", 'deleted_count' => 0];
    }

    // Удаляем только конкретную запись брони по времени
    $query = AuditoryJournal::where('aud_id', $auditory->id);

    if ($startTime && $endTime && $dayOfWeek) {
        $query->where('startTime', $startTime)
              ->where('endTime', $endTime)
              ->where('dayOfWeek', $dayOfWeek);
    } else {
        // Если время не передано — ничего не удаляем
        return ['status' => 'error', 'message' => 'Не указано время брони.', 'deleted_count' => 0];
    }

    $deleted = $query->delete();

    Log::info("cancelBooking: deleted {$deleted} record(s) for {$auditory->name}");

    return $deleted > 0
        ? ['status' => 'ok', 'message' => "Бронь отменена.", 'deleted_count' => $deleted]
        : ['status' => 'not_found', 'message' => 'Запись брони не найдена.', 'deleted_count' => 0];
}
    // ─── Helpers ──────────────────────────────────────────────────────────────

    private function resolveCorpus(?string $locationId): string
    {
        if ($locationId === null) return 'Главный';
        return self::LOCATION_TO_CORPUS[strtolower($locationId)] ?? $locationId;
    }

    private function addMinutes(string $time, int $minutes): string
    {
        [$h, $m] = array_map('intval', explode(':', $time));
        $total = $h * 60 + $m + $minutes;
        return sprintf('%02d:%02d', intdiv($total, 60), $total % 60);
    }
}
