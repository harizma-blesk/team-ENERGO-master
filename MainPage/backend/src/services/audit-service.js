import { prisma } from '../db/prisma.js';

export const writeAuditLog = async (input) => {
  await prisma.auditLog.create({
    data: {
      actorUserId: input.actorUserId,
      action: input.action,
      entityType: input.entityType,
      entityId: input.entityId,
      payloadJson: input.payload,
      traceId: input.traceId
    }
  });
};
