<?php

namespace App\Http\Controllers;

use App\Services\ScheduleService;
use App\Services\SubjectService;
use App\Tcp\SubjectTcpSender;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log;

class ScheduleController extends Controller
{
    public function __construct(
        private ScheduleService $scheduleService,
        private SubjectService  $subjectService,
        private SubjectTcpSender $subjectTcpSender,
    ) {}

    /**
     * POST /api/schedule/upload
     * Body: { fileName, sheet, rows: string[][] }
     */
    public function upload(Request $request): JsonResponse
    {
        Log::info('POST /api/schedule/upload', ['file' => $request->input('fileName')]);

        $saveResult = $this->scheduleService->saveSchedule($request->all());

        return response()->json([
            'status'  => 'success',
            'message' => 'Расписание успешно обработано',
            ...$saveResult,
        ], 201);
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
            'corpus'   => $a->corpus,
            'category' => $a->category,
        ]);

        return response()->json($list);
    }

    /**
     * GET /api/schedule/journal
     */
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

    /**
     * POST /api/schedule/subjects/push?ip=...&port=...
     */
    public function pushSubjects(Request $request): JsonResponse
    {
        $ip   = $request->query('ip');
        $port = (int)$request->query('port');

        $this->subjectTcpSender->sendSubjects($ip, $port);

        return response()->json(['status' => 'sent', 'ip' => $ip, 'port' => $port]);
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
}
