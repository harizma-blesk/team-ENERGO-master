import 'dotenv/config';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

const main = async () => {
  // ----------------------------------------------------------------
  // Очистка таблиц (удаляем только группы)
  // ----------------------------------------------------------------
  // Примечание: если у вас есть связанные данные в других таблицах, 
  // Prisma может выдать ошибку foreign key. В таком случае их тоже нужно чистить.
  await prisma.group.deleteMany();

  // ----------------------------------------------------------------
  // GROUPS
  // ----------------------------------------------------------------
  const [group1, group2, group3] = await Promise.all([
    prisma.group.create({
      data: { 
        code: 'COMPS-101', 
        name: 'Информатика 1 курс', 
        semester: '2025S2', 
        externalGroupCode: 'EXT-COMPS-101' 
      }
    }),
    prisma.group.create({
      data: { 
        code: 'COMPS-201', 
        name: 'Информатика 2 курс', 
        semester: '2025S2', 
        externalGroupCode: 'EXT-COMPS-201' 
      }
    }),
    prisma.group.create({
      data: { 
        code: 'MATH-101', 
        name: 'Математика 1 курс', 
        semester: '2025S2', 
        externalGroupCode: 'EXT-MATH-101' 
      }
    }),
  ]);

  console.log('База данных успешно заполнена группами');
};

main()
  .catch((e) => { 
    console.error(e); 
    process.exit(1); 
  })
  .finally(async () => { 
    await prisma.$disconnect(); 
  });