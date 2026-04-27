<?php

namespace App\Providers;

use App\Services\BotBridgeService;
use App\Services\ScheduleService;
use App\Services\SubjectService;
use Illuminate\Support\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    public function register(): void
    {
    

        // Services
        $this->app->singleton(SubjectService::class);     

        $this->app->singleton(ScheduleService::class, function ($app) {
            return new ScheduleService($app->make(SubjectService::class));
        });

        $this->app->singleton(BotBridgeService::class, function ($app) {
            return new BotBridgeService();
        });
    }

    public function boot(): void
    {
        //
    }
}
