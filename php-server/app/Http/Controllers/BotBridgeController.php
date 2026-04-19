<?php

namespace App\Http\Controllers;

use App\Services\BotBridgeService;
use App\Tcp\PythonTcpClient;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log;

class BotBridgeController extends Controller
{
    public function __construct(
        private BotBridgeService $botBridgeService,
        private PythonTcpClient  $tcpClient,
    ) {}

    /**
     * POST /api/bridge
     * Body: { location_id, duration_minutes, floor?, requested_by?, filters? }
     */
    public function bridge(Request $request): JsonResponse
    {
        try {
            Log::info('POST /api/bridge', $request->all());

            $response = $this->botBridgeService->findRooms($request->all());

            Log::info('Bridge response', [
                'free_rooms'   => count($response['free_rooms'] ?? []),
                'alternatives' => count($response['alternatives'] ?? []),
            ]);

            return response()->json($response, 200);

        } catch (\InvalidArgumentException $e) {
            Log::warning('Bridge bad request: ' . $e->getMessage());
            return response()->json(['status' => 'error', 'message' => $e->getMessage()], 400);

        } catch (\Throwable $e) {
            Log::error('Bridge error: ' . $e->getMessage(), ['exception' => $e]);
            return response()->json(['status' => 'error', 'message' => $e->getMessage()], 500);
        }
    }

    /**
     * GET /api/bridge
     * Health check.
     */
    public function health(): JsonResponse
    {
        Log::info('GET /api/bridge (health check)');
        return response()->json([
            'status'      => 'ok',
            'service'     => 'schedule-server',
            'pythonServer' => 'configured',
        ]);
    }

    /**
     * POST /api/bridge/cancel
     * Body: { telegram_user_id, auditory_name, corpus, start_time, end_time }
     */
    public function cancelBooking(Request $request): JsonResponse
    {
        try {
            Log::info('POST /api/bridge/cancel', $request->all());

            $result = $this->botBridgeService->cancelBooking($request->all());
            $status = $result['status'] ?? 'error';

            $httpCode = match ($status) {
                'ok'        => 200,
                'not_found' => 404,
                default     => 400,
            };

            return response()->json($result, $httpCode);

        } catch (\Throwable $e) {
            Log::error('Cancel booking error: ' . $e->getMessage(), ['exception' => $e]);
            return response()->json(['status' => 'error', 'message' => $e->getMessage()], 500);
        }
    }
}
