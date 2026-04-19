<?php

namespace App\Services;

use App\Models\Subject;

class SubjectService
{
    /**
     * Add a new subject or append teacher name to existing one (deduplication by lowercase).
     */
    public function addOrUpdateSubject(string $subName, ?string $teacherName): void
    {
        $subName = trim($subName);
        if ($subName === '') return;

        $incoming = $teacherName ?? '';
        $incomingParts = array_filter(array_map('trim', explode(',', $incoming)));

        $subject = Subject::where('sub_name', $subName)->first();

        if ($subject) {
            $existing = $subject->teacher_name ?? '';
            $existingParts = array_filter(array_map('trim', explode(',', $existing)));

            // Deduplicate by lowercase key, preserve original casing
            $unique = [];
            foreach ($existingParts as $t) {
                $unique[mb_strtolower($t)] = $t;
            }
            foreach ($incomingParts as $t) {
                $unique[mb_strtolower($t)] = $unique[mb_strtolower($t)] ?? $t;
            }

            $joined = implode(', ', $unique);
            if ($joined !== $existing) {
                $subject->teacher_name = $joined;
                $subject->save();
            }
        } else {
            $unique = [];
            foreach ($incomingParts as $t) {
                $unique[mb_strtolower($t)] = $t;
            }
            Subject::create([
                'sub_name'     => $subName,
                'teacher_name' => implode(', ', $unique),
            ]);
        }
    }

    public function getAll(): \Illuminate\Database\Eloquent\Collection
    {
        return Subject::orderBy('sub_name')->get();
    }
}
