import type { FastifyPluginAsync } from 'fastify';
//import { loadSubjectsFromCache } from '../services/subject-service.js';

const scheduleCompatRoutes: FastifyPluginAsync = async (fastify) => {
  // Compatibility endpoint used by older schedule providers
  // Returns array of items in a simple Java-friendly format: { id, subName, teacherName }
  fastify.get('/subjects', async (request) => {
    const q = request.query as Record<string, string | undefined>;
    const query = {
      groupCode: q.groupCode,
      semester: q.semester,
      teacherExternalId: q.teacherExternalId
    };

    // Read subjects from local cache to avoid calling the remote provider (which may point to this same endpoint)
    const items = await loadSubjectsFromCache(query);

    return items.map((s) => ({
      id: s.subjectId,
      subName: s.subjectName,
      teacherName: s.teacher?.name ?? s.teacher?.externalId ?? undefined
    }));
  });
};

export default scheduleCompatRoutes;



