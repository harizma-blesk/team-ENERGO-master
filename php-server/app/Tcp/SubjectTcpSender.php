<?php

namespace App\Tcp;

use App\Models\Subject;
use Illuminate\Support\Facades\Log;

/**
 * Sends the full subjects list to the Python server over TCP.
 * Sends raw JSON (no length prefix) — matches original SubjectTcpSender behavior.
 */
class SubjectTcpSender
{
    public function sendSubjects(string $ip, int $port): void
    {
        $subjects = Subject::all(['id_sub', 'sub_name', 'teacher_name'])->toArray();
        $json = json_encode($subjects, JSON_UNESCAPED_UNICODE);

        $socket = @fsockopen($ip, $port, $errno, $errstr, 10);

        if ($socket === false) {
            Log::error('SubjectTcpSender: failed to connect', ['ip' => $ip, 'port' => $port, 'error' => $errstr]);
            return;
        }

        try {
            fwrite($socket, $json);
            Log::info('SubjectTcpSender: sent', ['ip' => $ip, 'port' => $port, 'count' => count($subjects)]);
        } catch (\Throwable $e) {
            Log::error('SubjectTcpSender: write failed', ['error' => $e->getMessage()]);
        } finally {
            fclose($socket);
        }
    }
}
