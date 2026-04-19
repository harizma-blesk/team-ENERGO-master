<?php
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;
return new class extends Migration {
    public function up(): void
    {
        Schema::create('auditory', function (Blueprint $table) {
            $table->id();
            $table->string('name')->unique();
            $table->integer('number')->nullable();
            $table->string('corpus')->nullable();
            $table->string('category')->nullable();
            $table->integer('capacity')->nullable();
            $table->integer('has_projector')->default(0);
            $table->integer('floor')->nullable();
        });
        Schema::create('auditory_journal', function (Blueprint $table) {
            $table->id();
            $table->unsignedBigInteger('aud_id');
            $table->integer('dayOfWeek');
            $table->string('startTime')->nullable();
            $table->string('endTime')->nullable();
            $table->integer('duration')->nullable();
            $table->integer('timeStatus')->nullable();
            $table->foreign('aud_id')->references('id')->on('auditory')->onDelete('cascade');
        });
        Schema::create('subjects', function (Blueprint $table) {
            $table->id('id_sub');
            $table->string('sub_name')->unique();
            $table->string('teacher_name')->nullable();
        });
    }
    public function down(): void
    {
        Schema::dropIfExists('auditory_journal');
        Schema::dropIfExists('auditory');
        Schema::dropIfExists('subjects');
    }
};