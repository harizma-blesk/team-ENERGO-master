<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Auditory extends Model
{
    public $timestamps = false;
    protected $table = 'auditory';

    protected $fillable = ['name', 'number', 'corpus', 'category', 'capacity', 'has_projector', 'floor'];

    public function journal(): HasMany
    {
        return $this->hasMany(AuditoryJournal::class, 'aud_id');
    }
}
