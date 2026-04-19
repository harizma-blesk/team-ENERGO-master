<?php

namespace App\Providers;

use App\Services\BotBridgeService;
use App\Services\ScheduleService;
use App\Services\SubjectService;
use App\Tcp\PythonTcpClient;
use App\Tcp\SubjectTcpSender;
use Illuminate\Support\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    public function register(): void
    {
        // PythonTcpClient — singleton, reads config/python_server.php
        $this->app->singleton(PythonTcpClient::class, function () {
            return new PythonTcpClient(
                host:           config('python_server.host'),
                port:           config('python_server.port'),
                timeoutSeconds: config('python_server.timeout'),
            );
        });

        // Services
        $this->app->singleton(SubjectService::class);
        $this->app->singleton(SubjectTcpSender::class);

        $this->app->singleton(ScheduleService::class, function ($app) {
            return new ScheduleService($app->make(SubjectService::class));
        });

        $this->app->singleton(BotBridgeService::class, function ($app) {
            return new BotBridgeService($app->make(PythonTcpClient::class));
        });
    }

    public function boot(): void
    {
        //
    }
}
