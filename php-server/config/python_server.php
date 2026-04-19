<?php

return [
    'host'    => env('PYTHON_SERVER_HOST', '127.0.0.1'),
    'port'    => (int) env('PYTHON_SERVER_PORT', 2222),
    'timeout' => (int) env('PYTHON_SERVER_TIMEOUT', 30),
];
