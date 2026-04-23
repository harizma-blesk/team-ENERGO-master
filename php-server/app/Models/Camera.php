<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;  // ← добавь этот импорт

class Camera extends Model
{
    protected $fillable = ['auditory_id', 'name', 'ip', 'port', 'login', 'password', 'rtsp_url'];

    public function auditory()
    {
        return $this->belongsTo(Auditory::class);
    }
}