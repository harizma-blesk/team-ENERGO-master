-- CreateTable
CREATE TABLE "User" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "email" TEXT NOT NULL UNIQUE,
    "passwordHash" TEXT NOT NULL,
    "role" TEXT NOT NULL CHECK("role" IN ('STUDENT', 'TEACHER', 'ADMIN')),
    "status" TEXT NOT NULL DEFAULT 'ACTIVE' CHECK("status" IN ('ACTIVE', 'BLOCKED')),
    "locale" TEXT NOT NULL DEFAULT 'ru',
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" DATETIME NOT NULL
);

-- CreateTable
CREATE TABLE "RefreshToken" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "userId" TEXT NOT NULL,
    "tokenHash" TEXT NOT NULL UNIQUE,
    "expiresAt" DATETIME NOT NULL,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "revokedAt" DATETIME,
    FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE
);

-- CreateTable
CREATE TABLE "Group" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "code" TEXT NOT NULL UNIQUE,
    "name" TEXT NOT NULL,
    "semester" TEXT NOT NULL,
    "externalGroupCode" TEXT,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- CreateTable
CREATE TABLE "StudentProfile" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "userId" TEXT NOT NULL UNIQUE,
    "fullName" TEXT NOT NULL,
    "studentNo" TEXT NOT NULL UNIQUE,
    "groupId" TEXT NOT NULL,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE,
    FOREIGN KEY ("groupId") REFERENCES "Group"("id") ON DELETE RESTRICT
);

-- CreateTable
CREATE TABLE "TeacherProfile" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "userId" TEXT NOT NULL UNIQUE,
    "fullName" TEXT NOT NULL,
    "department" TEXT,
    "externalTeacherId" TEXT,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE
);

-- CreateTable
CREATE TABLE "Subject" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "externalSubjectCode" TEXT UNIQUE,
    "name" TEXT NOT NULL UNIQUE,
    "teacher_name" TEXT,
    "description" TEXT,
    "syllabusJson" TEXT,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- CreateTable
CREATE TABLE "ScheduleItem" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "externalScheduleId" TEXT NOT NULL UNIQUE,
    "subjectId" TEXT NOT NULL,
    "groupId" TEXT NOT NULL,
    "teacherExternalId" TEXT,
    "startsAt" DATETIME NOT NULL,
    "endsAt" DATETIME NOT NULL,
    "room" TEXT,
    "syncedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("subjectId") REFERENCES "Subject"("id") ON DELETE RESTRICT,
    FOREIGN KEY ("groupId") REFERENCES "Group"("id") ON DELETE RESTRICT
);

-- CreateTable
CREATE TABLE "Test" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "studentId" TEXT NOT NULL,
    "subjectId" TEXT NOT NULL,
    "scheduleItemId" TEXT,
    "difficulty" TEXT NOT NULL CHECK("difficulty" IN ('EASY', 'MEDIUM', 'HARD')),
    "status" TEXT NOT NULL DEFAULT 'GENERATING' CHECK("status" IN ('GENERATING', 'READY', 'FAILED')),
    "questionCount" INTEGER NOT NULL,
    "promptVersion" TEXT NOT NULL DEFAULT 'v1',
    "language" TEXT NOT NULL DEFAULT 'ru',
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("studentId") REFERENCES "User"("id") ON DELETE RESTRICT,
    FOREIGN KEY ("subjectId") REFERENCES "Subject"("id") ON DELETE RESTRICT,
    FOREIGN KEY ("scheduleItemId") REFERENCES "ScheduleItem"("id") ON DELETE SET NULL
);

-- CreateTable
CREATE TABLE "Question" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "testId" TEXT NOT NULL,
    "type" TEXT NOT NULL CHECK("type" IN ('SINGLE_CHOICE', 'MULTI_CHOICE', 'OPEN_SHORT')),
    "stem" TEXT NOT NULL,
    "topicCode" TEXT NOT NULL,
    "difficulty" TEXT NOT NULL CHECK("difficulty" IN ('EASY', 'MEDIUM', 'HARD')),
    "rubricJson" TEXT,
    "correctAnswerJson" TEXT,
    "fingerprint" TEXT NOT NULL,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("testId") REFERENCES "Test"("id") ON DELETE CASCADE
);

-- CreateTable
CREATE TABLE "AnswerOption" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "questionId" TEXT NOT NULL,
    "code" TEXT NOT NULL,
    "text" TEXT NOT NULL,
    "isCorrect" INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY ("questionId") REFERENCES "Question"("id") ON DELETE CASCADE
);

-- CreateTable
CREATE TABLE "TestAttempt" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "testId" TEXT NOT NULL,
    "studentId" TEXT NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'IN_PROGRESS' CHECK("status" IN ('IN_PROGRESS', 'CHECKING', 'COMPLETED')),
    "startedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "submittedAt" DATETIME,
    "checkedAt" DATETIME,
    "scorePoints" REAL,
    "scorePercent" REAL,
    "passed" INTEGER,
    "clientDurationSec" INTEGER,
    FOREIGN KEY ("testId") REFERENCES "Test"("id") ON DELETE RESTRICT,
    FOREIGN KEY ("studentId") REFERENCES "User"("id") ON DELETE RESTRICT
);

-- CreateTable
CREATE TABLE "StudentAnswer" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "attemptId" TEXT NOT NULL,
    "questionId" TEXT NOT NULL,
    "selectedOptionIds" TEXT,
    "answerText" TEXT,
    "scorePoints" REAL,
    "isCorrect" INTEGER,
    "rationale" TEXT,
    FOREIGN KEY ("attemptId") REFERENCES "TestAttempt"("id") ON DELETE CASCADE,
    FOREIGN KEY ("questionId") REFERENCES "Question"("id") ON DELETE RESTRICT,
    UNIQUE("attemptId", "questionId")
);

-- CreateTable
CREATE TABLE "Feedback" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "attemptId" TEXT NOT NULL UNIQUE,
    "summary" TEXT NOT NULL,
    "mistakesJson" TEXT,
    "strengthsJson" TEXT,
    FOREIGN KEY ("attemptId") REFERENCES "TestAttempt"("id") ON DELETE CASCADE
);

-- CreateTable
CREATE TABLE "Recommendation" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "attemptId" TEXT NOT NULL,
    "studentId" TEXT NOT NULL,
    "type" TEXT NOT NULL CHECK("type" IN ('REVIEW', 'PRACTICE', 'THEORY')),
    "contentJson" TEXT NOT NULL,
    "priority" INTEGER NOT NULL DEFAULT 1,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("studentId") REFERENCES "User"("id") ON DELETE RESTRICT,
    FOREIGN KEY ("attemptId") REFERENCES "TestAttempt"("id") ON DELETE CASCADE
);

-- CreateTable
CREATE TABLE "WeakTopic" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "studentId" TEXT NOT NULL,
    "subjectId" TEXT NOT NULL,
    "topicCode" TEXT NOT NULL,
    "weaknessScore" REAL NOT NULL,
    "lastSeenAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("studentId") REFERENCES "User"("id") ON DELETE RESTRICT,
    FOREIGN KEY ("subjectId") REFERENCES "Subject"("id") ON DELETE RESTRICT,
    UNIQUE("studentId", "subjectId", "topicCode")
);

-- CreateTable
CREATE TABLE "PracticeTask" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "studentId" TEXT NOT NULL,
    "subjectId" TEXT NOT NULL,
    "topicCode" TEXT NOT NULL,
    "prompt" TEXT NOT NULL,
    "expectedFormat" TEXT NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'NEW',
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("studentId") REFERENCES "User"("id") ON DELETE RESTRICT,
    FOREIGN KEY ("subjectId") REFERENCES "Subject"("id") ON DELETE RESTRICT
);

-- CreateTable
CREATE TABLE "ProgressSnapshot" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "studentId" TEXT NOT NULL,
    "subjectId" TEXT NOT NULL,
    "weekStart" DATETIME NOT NULL,
    "avgScore" REAL NOT NULL,
    "masteryJson" TEXT NOT NULL,
    "trend" TEXT,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("studentId") REFERENCES "User"("id") ON DELETE RESTRICT,
    FOREIGN KEY ("subjectId") REFERENCES "Subject"("id") ON DELETE RESTRICT,
    UNIQUE("studentId", "subjectId", "weekStart")
);

-- CreateTable
CREATE TABLE "ActivitySession" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "studentId" TEXT NOT NULL,
    "subjectId" TEXT NOT NULL,
    "type" TEXT NOT NULL CHECK("type" IN ('FEYNMAN', 'DEBATE')),
    "transcriptJson" TEXT NOT NULL,
    "scoreJson" TEXT NOT NULL,
    "reviewStatus" TEXT NOT NULL DEFAULT 'PENDING_REVIEW' CHECK("reviewStatus" IN ('PENDING_REVIEW', 'REVIEWED')),
    "teacherComment" TEXT,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("studentId") REFERENCES "User"("id") ON DELETE RESTRICT,
    FOREIGN KEY ("subjectId") REFERENCES "Subject"("id") ON DELETE RESTRICT
);

-- CreateTable
CREATE TABLE "AuditLog" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "actorUserId" TEXT,
    "action" TEXT NOT NULL,
    "entityType" TEXT NOT NULL,
    "entityId" TEXT NOT NULL,
    "payloadJson" TEXT,
    "traceId" TEXT NOT NULL,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("actorUserId") REFERENCES "User"("id") ON DELETE SET NULL
);

-- CreateIndex
CREATE INDEX "RefreshToken_userId_idx" ON "RefreshToken"("userId");

-- CreateIndex
CREATE INDEX "RefreshToken_expiresAt_idx" ON "RefreshToken"("expiresAt");

-- CreateIndex
CREATE INDEX "Group_semester_idx" ON "Group"("semester");

-- CreateIndex
CREATE INDEX "TeacherProfile_externalTeacherId_idx" ON "TeacherProfile"("externalTeacherId");

-- CreateIndex
CREATE INDEX "ScheduleItem_groupId_startsAt_idx" ON "ScheduleItem"("groupId", "startsAt");

-- CreateIndex
CREATE INDEX "ScheduleItem_subjectId_idx" ON "ScheduleItem"("subjectId");

-- CreateIndex
CREATE INDEX "Test_studentId_createdAt_idx" ON "Test"("studentId", "createdAt");

-- CreateIndex
CREATE INDEX "Test_subjectId_idx" ON "Test"("subjectId");

-- CreateIndex
CREATE INDEX "Question_testId_idx" ON "Question"("testId");

-- CreateIndex
CREATE INDEX "Question_fingerprint_idx" ON "Question"("fingerprint");

-- CreateIndex
CREATE INDEX "AnswerOption_questionId_idx" ON "AnswerOption"("questionId");

-- CreateIndex
CREATE INDEX "TestAttempt_studentId_submittedAt_idx" ON "TestAttempt"("studentId", "submittedAt");

-- CreateIndex
CREATE INDEX "TestAttempt_testId_idx" ON "TestAttempt"("testId");

-- CreateIndex
CREATE INDEX "StudentAnswer_questionId_idx" ON "StudentAnswer"("questionId");

-- CreateIndex
CREATE INDEX "Recommendation_studentId_createdAt_idx" ON "Recommendation"("studentId", "createdAt");

-- CreateIndex
CREATE INDEX "WeakTopic_subjectId_weaknessScore_idx" ON "WeakTopic"("subjectId", "weaknessScore");

-- CreateIndex
CREATE INDEX "PracticeTask_studentId_createdAt_idx" ON "PracticeTask"("studentId", "createdAt");

-- CreateIndex
CREATE INDEX "ProgressSnapshot_subjectId_weekStart_idx" ON "ProgressSnapshot"("subjectId", "weekStart");

-- CreateIndex
CREATE INDEX "ActivitySession_subjectId_createdAt_idx" ON "ActivitySession"("subjectId", "createdAt");

-- CreateIndex
CREATE INDEX "ActivitySession_reviewStatus_idx" ON "ActivitySession"("reviewStatus");

-- CreateIndex
CREATE INDEX "AuditLog_action_createdAt_idx" ON "AuditLog"("action", "createdAt");

-- CreateIndex
CREATE INDEX "AuditLog_traceId_idx" ON "AuditLog"("traceId");