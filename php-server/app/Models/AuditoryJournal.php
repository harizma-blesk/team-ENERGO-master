<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class AuditoryJournal extends Model
{
    public $timestamps = false;
    protected $table = 'auditory_journal';

    protected $fillable = ['aud_id', 'dayOfWeek', 'startTime', 'endTime', 'duration', 'timeStatus'];

    public function auditory(): BelongsTo
    {
        return $this->belongsTo(Auditory::class, 'aud_id');
    }
}
