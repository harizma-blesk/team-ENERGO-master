<?php

namespace App\Tcp;

use Illuminate\Support\Facades\Log;

/**
 * TCP client for the Python camera service.
 * Protocol (same as original C++ server):
 *   Send:    4-byte big-endian int32 (payload length) + UTF-8 JSON
 *   Receive: 4-byte big-endian int32 (response length) + UTF-8 JSON
 */
class PythonTcpClient
{
    private string $host;
    private int $port;
    private int $timeoutSeconds;

    public function __construct(string $host, int $port, int $timeoutSeconds = 30)
    {
        $this->host = $host;
        $this->port = $port;
        $this->timeoutSeconds = $timeoutSeconds;
    }

    /**
     * @param array $payload Associative array — will be JSON-encoded
     * @return array Decoded JSON response from Python server
     * @throws \RuntimeException on connection or protocol error
     */
    public function send(array $payload): array
    {
        $json = json_encode($payload, JSON_UNESCAPED_UNICODE);
        Log::info('PythonTcpClient: sending', ['host' => $this->host, 'port' => $this->port, 'payload' => $payload]);

        $socket = @fsockopen($this->host, $this->port, $errno, $errstr, $this->timeoutSeconds);

        if ($socket === false) {
            throw new \RuntimeException("Cannot connect to Python server {$this->host}:{$this->port} — {$errstr} ({$errno})");
        }

        stream_set_timeout($socket, $this->timeoutSeconds);

        try {
            // Write: 4-byte big-endian length + JSON bytes
            $length = strlen($json);
            $header = pack('N', $length); // 'N' = unsigned long, big-endian 32-bit
            fwrite($socket, $header . $json);

            // Read: 4-byte big-endian response length
            $responseHeader = $this->readExact($socket, 4);
            $responseLength = unpack('N', $responseHeader)[1];

            if ($responseLength <= 0 || $responseLength > 1_000_000) {
                throw new \RuntimeException("Invalid response length from Python server: {$responseLength}");
            }

            // Read response JSON
            $responseJson = $this->readExact($socket, $responseLength);
            Log::info('PythonTcpClient: received', ['response' => $responseJson]);

            $decoded = json_decode($responseJson, true);
            if ($decoded === null) {
                throw new \RuntimeException("Invalid JSON from Python server: {$responseJson}");
            }

            return $decoded;

        } finally {
            fclose($socket);
        }
    }

    /**
     * Read exactly $length bytes from socket, throws on timeout or EOF.
     */
    private function readExact($socket, int $length): string
    {
        $data = '';
        $remaining = $length;

        while ($remaining > 0) {
            $chunk = fread($socket, $remaining);

            if ($chunk === false || $chunk === '') {
                $meta = stream_get_meta_data($socket);
                if ($meta['timed_out']) {
                    throw new \RuntimeException("Read timeout from Python server");
                }
                throw new \RuntimeException("Connection closed by Python server unexpectedly");
            }

            $data .= $chunk;
            $remaining -= strlen($chunk);
        }

        return $data;
    }
}
