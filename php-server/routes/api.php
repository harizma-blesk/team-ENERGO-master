<?php

use App\Http\Controllers\BotBridgeController;
use App\Http\Controllers\ScheduleController;
use Illuminate\Support\Facades\Route;


// ─── Bot bridge ───────────────────────────────────────────────────────────────
Route::post('/bridge',        [BotBridgeController::class, 'bridge']);
Route::get('/bridge',         [BotBridgeController::class, 'health']);
Route::post('/bridge/cancel', [BotBridgeController::class, 'cancelBooking']);

// ─── Schedule ─────────────────────────────────────────────────────────────────
Route::post('/schedule/upload',          [ScheduleController::class, 'upload']);
Route::get('/schedule/auditories',       [ScheduleController::class, 'auditories']);
Route::get('/schedule/journal',          [ScheduleController::class, 'journal']);
Route::get('/schedule/journal/{audId}',  [ScheduleController::class, 'journalByAuditory']);
Route::get('/schedule/subjects',         [ScheduleController::class, 'subjects']);
Route::post('/schedule/subjects/push',   [ScheduleController::class, 'pushSubjects']);
Route::post('/schedule/cameras/detection', [ScheduleController::class, 'updateCameraDetection']);
// Добавляем этот маршрут специально для Python-скрипта
Route::get('/auditories', [ScheduleController::class, 'auditories']);
Route::get('/cameras', [ScheduleController::class, 'cameras']);
