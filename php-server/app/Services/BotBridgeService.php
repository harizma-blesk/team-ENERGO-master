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
        $dt = new \DateTime($startAt);
    } else {
        $dt = new \DateTime();
    }

    $dayOfWeek = (int)$dt->format('N'); // 1=пн, 7=вс
    $startTime = $dt->format('H:i');
    $endTime   = (clone $dt)->modify("+{$durationMinutes} minutes")->format('H:i');

    $corpus = $this->resolveCorpus($locationId);

    $query = Auditory::where('corpus', $corpus);
    if ($floor !== null) {
        $query->where('floor', $floor);
    }
    if ($minCapacity > 0) {
        $query->where('capacity', '>=', $minCapacity);
    }
    if ($needProjector) {
        $query->where('has_projector', 1);
    }
    $auditories = $query->get();

    $freeRooms = [];
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

            $roomData = [
                'name'          => $aud->name,
                'location_name' => $corpus,
                'location_id'   => $locationId,
                'floor'         => $aud->floor,
                'capacity'      => $aud->capacity,
                'schedule_free' => true,
                'camera_free'   => !$isOccupied,
                'camera_status' => 'online',
                'auditory_id'   => $aud->id,
            ];

            if ($isOccupied) {
                $alternatives[] = $roomData;
            } else {
                $freeRooms[] = $roomData;
            }
        }
    }

    return [
        'free_rooms'   => $freeRooms,
        'alternatives' => [],
        'reason'       => empty($freeRooms) ? 'Свободных кабинетов не найдено' : null,
    ];
}

    // ─── Cancel booking ───────────────────────────────────────────────────────

    public function cancelBooking(array $request): array
    {
        $auditoryName = $request['auditory_name'] ?? '';
        $corpus       = $request['corpus'] ?? '';

        Log::info('BotBridgeService: cancelBooking', [
            'auditory_name' => $auditoryName,
            'corpus'        => $corpus,
        ]);

        if (empty(trim($auditoryName))) {
            return ['status' => 'error', 'message' => 'Не указано имя аудитории.', 'deleted_count' => 0];
        }

        // Try to find auditory by name as-is
        $auditory = Auditory::where('name', $auditoryName)->first();

        // Try with corpus prefix: "А-301"
        if (!$auditory && !empty(trim($corpus))) {
            $fullName = $corpus . '-' . $auditoryName;
            $auditory = Auditory::where('name', $fullName)->first();
        }

        if (!$auditory) {
            Log::warning("cancelBooking: auditory not found: {$auditoryName}");
            return [
                'status'        => 'not_found',
                'message'       => "Аудитория {$auditoryName} не найдена в базе данных.",
                'deleted_count' => 0,
            ];
        }

        Log::info("Found auditory: id={$auditory->id}, name={$auditory->name}");

        // Delete all journal entries for this auditory (same behavior as original Java)
        $deleted = AuditoryJournal::where('aud_id', $auditory->id)->delete();

        if ($deleted > 0) {
            Log::info("cancelBooking: deleted {$deleted} record(s) for auditory {$auditory->name}");
            return [
                'status'        => 'ok',
                'message'       => "Бронь аудитории {$auditory->name} успешно отменена.",
                'deleted_count' => $deleted,
            ];
        }

        return [
            'status'        => 'not_found',
            'message'       => 'Запись о бронировании не найдена в журнале.',
            'deleted_count' => 0,
        ];
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
