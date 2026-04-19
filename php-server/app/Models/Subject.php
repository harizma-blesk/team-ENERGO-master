<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Subject extends Model
{
    public $timestamps = false;
    protected $table = 'subjects';
    protected $primaryKey = 'id_sub';

    protected $fillable = ['sub_name', 'teacher_name'];
}
