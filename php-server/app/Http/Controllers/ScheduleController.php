<?php

namespace App\Http\Controllers;

use App\Services\ScheduleService;
use App\Services\SubjectService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log;

class ScheduleController extends Controller
{
    public function __construct(
        private ScheduleService $scheduleService,
        private SubjectService  $subjectService,
    ) {}

    /**
     * POST /api/schedule/upload
     * Body: { fileName, sheet, rows: string[][] }
     */
    public function upload(Request $request): JsonResponse
{
    Log::info('POST /api/schedule/upload', ['file' => $request->input('fileName')]);

    try {
        $saveResult = $this->scheduleService->saveSchedule($request->all());

        return response()->json([
            'status'  => 'success',
            'message' => 'Расписание успешно обработано',
            ...$saveResult,
        ], 201);

    } catch (\Throwable $e) {
        Log::error('Upload error: ' . $e->getMessage(), [
            'file' => $e->getFile(),
            'line' => $e->getLine(),
        ]);

        return response()->json([
            'status'  => 'error',
            'message' => $e->getMessage(),
            'file'    => $e->getFile(),
            'line'    => $e->getLine(),
        ], 500);
    }
}

    /**
     * GET /api/schedule/auditories
     */
    public function auditories(): JsonResponse
{
    $list = $this->scheduleService->getAllAuditories()->map(fn($a) => [
        'id'       => $a->id,
        'name'     => $a->name,
        'number'   => $a->number,
        'floor'    => $a->floor,  // ← добавить
        'corpus'   => $a->corpus,
        'category' => $a->category,
    ])->values()->toArray();

    return response()->json($list);
}


public function book(Request $request): JsonResponse
{
    $auditoryName = $request->input('auditory_name');
    $startTime    = $request->input('start_time'); // "14:00"
    $endTime      = $request->input('end_time');   // "15:20"
    $dayOfWeek    = $request->input('day_of_week'); // 1-7

    $auditory = \App\Models\Auditory::where('name', $auditoryName)->first();
    if (!$auditory) {
        return response()->json(['status' => 'error', 'message' => 'Кабинет не найден'], 404);
    }

    \App\Models\AuditoryJournal::firstOrCreate(
        [
            'aud_id'    => $auditory->id,
            'dayOfWeek' => $dayOfWeek,
            'startTime' => $startTime,
            'endTime'   => $endTime,
        ],
        [
            'duration'   => $this->minutesBetween($startTime, $endTime),
            'timeStatus' => 1,
        ]
    );

    return response()->json(['status' => 'ok']);
}

private function minutesBetween(string $start, string $end): int
{
    [$sh, $sm] = array_map('intval', explode(':', $start));
    [$eh, $em] = array_map('intval', explode(':', $end));
    return ($eh * 60 + $em) - ($sh * 60 + $sm);
}
    /**
     * GET /api/schedule/journal
     */

    public function cameras(): JsonResponse
    {
        $list = \App\Models\Camera::with('auditory')->get()->map(fn($c) => [
            'id'           => $c->id,
            'name'         => $c->name,
            'ip'           => $c->ip,
            'port'         => $c->port,
            'rtsp_url'     => $c->rtsp_url,
            'auditory_name' => $c->auditory?->name,
        ]);

        return response()->json($list);
    }
    public function journal(): JsonResponse
    {
        $list = $this->scheduleService->getAllJournal()->map(fn($j) => $this->mapJournal($j));
        return response()->json($list);
    }

    /**
     * GET /api/schedule/journal/{audId}
     */
    public function journalByAuditory(int $audId): JsonResponse
    {
        $list = $this->scheduleService->getJournalByAuditoryId($audId)->map(fn($j) => $this->mapJournal($j));
        return response()->json($list);
    }

    /**
     * GET /api/schedule/subjects
     */
    public function subjects(): JsonResponse
    {
        $list = $this->subjectService->getAll()->map(fn($s) => [
            'id'          => $s->id_sub,
            'subName'     => $s->sub_name,
            'teacherName' => $s->teacher_name,
        ]);

        return response()->json($list);
    }


    private function mapJournal($j): array
    {
        return [
            'id'         => $j->id,
            'audId'      => $j->aud_id,
            'dayOfWeek'  => $j->dayOfWeek,
            'startTime'  => $j->startTime,
            'endTime'    => $j->endTime,
            'duration'   => $j->duration,
            'timeStatus' => $j->timeStatus,
        ];
    }
    /**
     * POST /api/schedule/cameras/detection
     * Принимает данные от Python скрипта (камеры)
     */
    public function updateCameraDetection(Request $request): JsonResponse
    {
        // Логируем входящие данные, чтобы увидеть их в storage/logs/laravel.log
        Log::info('Данные от камеры получены:', $request->all());

        $auditoryName = $request->input('auditory_name');
        $status = $request->input('occupancy_status'); // 1 - занято, 0 - свободно

        // Вызываем метод сервиса для обновления статуса в базе
        // Убедитесь, что в вашем ScheduleService есть метод updateAuditoryStatus
        $updated = $this->scheduleService->updateAuditoryStatus($auditoryName, $status);

        if ($updated) {
            return response()->json(['status' => 'success', 'message' => 'Статус обновлен']);
        }

        return response()->json(['status' => 'error', 'message' => 'Кабинет не найден'], 404);
    }

    public function locations(): JsonResponse
    {
        $data = \App\Models\Auditory::select('corpus', 'floor')
            ->whereNotNull('corpus')
            ->whereNotNull('floor')
            ->distinct()
            ->orderBy('corpus')
            ->orderBy('floor')
            ->get()
            ->groupBy('corpus')
            ->map(fn($items) => $items->pluck('floor')->unique()->sort()->values())
            ->toArray();

        return response()->json($data);
    }
}
