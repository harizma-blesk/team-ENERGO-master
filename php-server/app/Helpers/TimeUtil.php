<?php

namespace App\Helpers;

use Carbon\Carbon;

class TimeUtil
{
    private const TIMEZONE = 'Asia/Almaty';

    public static function now(): Carbon
    {
        return Carbon::now(self::TIMEZONE);
    }

    public static function currentTime(): string
    {
        return self::now()->format('H:i');
    }

    public static function currentDayOfWeek(): int
    {
        // ISO: 1=Monday ... 7=Sunday
        return self::now()->dayOfWeekIso;
    }

    public static function parseTime(string $time): Carbon
    {
        return Carbon::createFromFormat('H:i', $time, self::TIMEZONE);
    }

    public static function formatTime(Carbon $time): string
    {
        return $time->format('H:i');
    }
}
