require('dotenv/config');
const { PrismaClient } = require('@prisma/client');

const prisma = new PrismaClient();

const main = async () => {
  

  // ----------------------------------------------------------------
  // Очистка базовых таблиц (порядок важен — сначала зависимые)
  // ----------------------------------------------------------------
  await prisma.scheduleItem.deleteMany();
  await prisma.subject.deleteMany();
  await prisma.group.deleteMany();

  // ----------------------------------------------------------------
  // GROUPS
  // ----------------------------------------------------------------
  const [group1, group2, group3] = await Promise.all([
    prisma.group.create({
      data: { code: 'COMPS-101', name: 'Информатика 1 курс', semester: '2025S2', externalGroupCode: 'EXT-COMPS-101' }
    }),
    prisma.group.create({
      data: { code: 'COMPS-201', name: 'Информатика 2 курс', semester: '2025S2', externalGroupCode: 'EXT-COMPS-201' }
    }),
    prisma.group.create({
      data: { code: 'MATH-101', name: 'Математика 1 курс', semester: '2025S2', externalGroupCode: 'EXT-MATH-101' }
    }),
  ]);

  // ----------------------------------------------------------------
  // SUBJECTS
  // ----------------------------------------------------------------
  const [sMath, sPhys, sCS, sDB, sAlgo] = await Promise.all([
    prisma.subject.create({
      data: {
        externalSubjectCode: 'MATH101',
        name: 'Математический анализ',
        teacher_name: 'Бекова Айгерим Сериковна',
        description: 'Пределы, производные, интегралы. Базовый курс для 1 курса.',
        syllabusJson: { weeks: 16, topics: ['Пределы', 'Производные', 'Интегралы', 'Ряды'] }
      }
    }),
    prisma.subject.create({
      data: {
        externalSubjectCode: 'PHYS101',
        name: 'Физика',
        teacher_name: 'Нурланова Зарина Асетовна',
        description: 'Механика, термодинамика, электричество.',
        syllabusJson: { weeks: 16, topics: ['Механика', 'Термодинамика', 'Электростатика', 'Оптика'] }
      }
    }),
    prisma.subject.create({
      data: {
        externalSubjectCode: 'CS101',
        name: 'Основы программирования',
        teacher_name: 'Сейткали Данияр Маратович',
        description: 'Алгоритмы, структуры данных, Python.',
        syllabusJson: { weeks: 16, topics: ['Алгоритмы', 'Массивы', 'Функции', 'ООП'] }
      }
    }),
    prisma.subject.create({
      data: {
        externalSubjectCode: 'CS201',
        name: 'Базы данных',
        teacher_name: 'Ахметов Болат Ержанович',
        description: 'SQL, реляционные БД, проектирование схем.',
        syllabusJson: { weeks: 14, topics: ['SQL SELECT', 'JOIN', 'Нормализация', 'Индексы'] }
      }
    }),
    prisma.subject.create({
      data: {
        externalSubjectCode: 'ALGOS101',
        name: 'Алгоритмы и структуры данных',
        teacher_name: 'Сейткали Данияр Маратович',
        description: 'Сортировки, деревья, графы, динамическое программирование.',
        syllabusJson: { weeks: 15, topics: ['Сортировки', 'Деревья', 'Графы', 'ДП'] }
      }
    }),
  ]);



  
  // ----------------------------------------------------------------
  // SCHEDULE ITEMS
  // ----------------------------------------------------------------
  await Promise.all([
    prisma.scheduleItem.create({
      data: {
        externalScheduleId: 'SCH-001',
        subjectId: sMath.id, groupId: group1.id,
        teacherExternalId: 't_01',
        startsAt: new Date('2025-02-03T08:00:00Z'),
        endsAt:   new Date('2025-02-03T09:30:00Z'),
        room: '301А'
      }
    }),
    prisma.scheduleItem.create({
      data: {
        externalScheduleId: 'SCH-002',
        subjectId: sCS.id, groupId: group1.id,
        teacherExternalId: 't_02',
        startsAt: new Date('2025-02-04T10:00:00Z'),
        endsAt:   new Date('2025-02-04T11:30:00Z'),
        room: '215Б'
      }
    }),
    prisma.scheduleItem.create({
      data: {
        externalScheduleId: 'SCH-003',
        subjectId: sPhys.id, groupId: group2.id,
        teacherExternalId: 't_03',
        startsAt: new Date('2025-02-05T13:00:00Z'),
        endsAt:   new Date('2025-02-05T14:30:00Z'),
        room: '102В'
      }
    }),
    prisma.scheduleItem.create({
      data: {
        externalScheduleId: 'SCH-004',
        subjectId: sDB.id, groupId: group2.id,
        teacherExternalId: 't_04',
        startsAt: new Date('2025-02-06T08:00:00Z'),
        endsAt:   new Date('2025-02-06T09:30:00Z'),
        room: '408Г'
      }
    }),
    prisma.scheduleItem.create({
      data: {
        externalScheduleId: 'SCH-005',
        subjectId: sAlgo.id, groupId: group3.id,
        teacherExternalId: 't_02',
        startsAt: new Date('2025-02-07T10:00:00Z'),
        endsAt:   new Date('2025-02-07T11:30:00Z'),
        room: '215Б'
      }
    }),
  ]);

  
};

main()
  .catch((e) => { 
    console.error(e); 
    process.exit(1); 
  })
  .finally(async () => { 
    await prisma.$disconnect(); 
  });