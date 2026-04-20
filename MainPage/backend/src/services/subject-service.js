import { prisma } from '../db/prisma.js';
import { env } from '../config/env.js';
import { fetchRemoteSchedule } from './schedule-provider.js';

const upsertScheduleCache = async (query, remoteItems) => {
  for (const item of remoteItems) {
    const groupCode = item.groupCode || query.groupCode || 'GLOBAL';
    const group = await prisma.group.upsert({
      where: { code: groupCode },
      update: {
        semester: item.semester ?? query.semester ?? 'UNSPECIFIED',
        externalGroupCode: groupCode
      },
      create: {
        code: groupCode,
        name: groupCode,
        semester: item.semester ?? query.semester ?? 'UNSPECIFIED',
        externalGroupCode: groupCode
      }
    });

    const subject = await prisma.subject.upsert({
  where: { externalSubjectCode: item.externalSubjectCode },
  update: {
    name: item.subjectName
  },
  create: {
    externalSubjectCode: item.externalSubjectCode,
    name: item.subjectName,
    description: `Imported from remote schedule for ${groupCode}`
  }
}).catch(async () => {
  const existing = await prisma.subject.findFirst({
    where: { name: item.subjectName }
  });
  if (existing) return existing;
  return prisma.subject.create({
    data: {
      externalSubjectCode: item.externalSubjectCode + '_dup',
      name: item.subjectName + ' (' + item.externalSubjectCode + ')',
      description: `Imported from remote schedule for ${groupCode}`
    }
  });
});

    await prisma.scheduleItem.upsert({
      where: { externalScheduleId: item.externalScheduleId },
      update: {
        subjectId: subject.id,
        groupId: group.id,
        teacherExternalId: item.teacherExternalId,
        startsAt: new Date(item.startsAt),
        endsAt: new Date(item.endsAt),
        room: item.room,
        syncedAt: new Date()
      },
      create: {
        externalScheduleId: item.externalScheduleId,
        subjectId: subject.id,
        groupId: group.id,
        teacherExternalId: item.teacherExternalId,
        startsAt: new Date(item.startsAt),
        endsAt: new Date(item.endsAt),
        room: item.room
      }
    });
  }
};

const buildSubjectResponse = (items) => {
  const map = new Map();

  for (const item of items) {
    const key = item.externalSubjectCode;
    if (!map.has(key)) {
      map.set(key, {
        subjectId: key,
        subjectCode: item.externalSubjectCode,
        subjectName: item.subjectName,
        semester: item.semester,
        teacher: {
          externalId: item.teacherExternalId,
          name: item.teacherName
        }
      });
    }
  }

  return [...map.values()];
};

const loadFromCache = async (query) => {
  const scheduleItems = await prisma.scheduleItem.findMany({
    where: {
      ...(query.teacherExternalId ? { teacherExternalId: query.teacherExternalId } : {})
    },
    include: {
      subject: true,
      group: true
    },
    orderBy: {
      startsAt: 'asc'
    },
    take: 500
  });

  const bySubject = new Map();
  for (const row of scheduleItems) {
    const subjectCode = row.subject.externalSubjectCode ?? row.subject.id;
    if (!bySubject.has(subjectCode)) {
      bySubject.set(subjectCode, {
        subjectId: row.subject.id,
        subjectCode,
        subjectName: row.subject.name,
        semester: row.group.semester,
        teacher: {
          externalId: row.teacherExternalId ?? undefined
        }
      });
    }
  }

  return [...bySubject.values()];
};

export const getSubjectsFromSchedule = async (query) => {
  if (env.SCHEDULE_PROVIDER_MODE === 'push') {
    const cachedItems = await loadFromCache(query);
    return {
      source: 'CACHE',
      stale: false,
      syncedAt: new Date().toISOString(),
      items: cachedItems,
      reason: cachedItems.length > 0 ? undefined : 'Кэш расписания пока пуст.'
    };
  }

  try {
    const remote = await fetchRemoteSchedule(query);
    await upsertScheduleCache(query, remote);

    return {
      source: 'REMOTE_SCHEDULE',
      stale: false,
      syncedAt: new Date().toISOString(),
      items: buildSubjectResponse(remote)
    };
  } catch (error) {
    const message = error instanceof Error ? error.message : 'schedule provider failed';
    console.error(`[schedule-provider] ${message}`);
    const cachedItems = await loadFromCache(query);
    return {
      source: 'CACHE',
      stale: true,
      syncedAt: new Date().toISOString(),
      items: cachedItems,
      reason: message
    };
  }
};

export const resolveSubjectId = async (subjectIdOrCode) => {
  const direct = await prisma.subject.findUnique({
    where: { id: subjectIdOrCode },
    select: { id: true }
  });
  if (direct) {
    return direct.id;
  }
  const byCode = await prisma.subject.findFirst({
    where: { externalSubjectCode: subjectIdOrCode },
    select: { id: true }
  });
  return byCode?.id ?? null;
};