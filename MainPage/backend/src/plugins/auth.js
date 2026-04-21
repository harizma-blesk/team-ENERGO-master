import fp from 'fastify-plugin';
import fastifyJwt from '@fastify/jwt';
import { env } from '../config/env.js';

export default fp(async (fastify) => {
  await fastify.register(fastifyJwt, {
    secret: env.JWT_ACCESS_SECRET
  });

  fastify.decorate('signAccessToken', async (payload) => {
    return fastify.jwt.sign(payload, { expiresIn: env.JWT_ACCESS_EXPIRES_IN });
  });

  fastify.decorate('authenticate', async (request, reply) => {
    try {
      const payload = await request.jwtVerify();
      request.authUser = {
        userId: payload.userId,
        role: payload.role,
        email: payload.email
      };
    } catch {
      reply.code(401).send({
        error: {
          code: 'UNAUTHORIZED',
          message: 'Authentication required',
          traceId: request.traceId,
          timestamp: new Date().toISOString()
        }
      });
    }
  });

  fastify.decorate('authorize', (roles) => {
    return async (request, reply) => {
      await fastify.authenticate(request, reply);
      if (reply.sent) {
        return;
      }
      if (!request.authUser || !roles.includes(request.authUser.role)) {
        reply.code(403).send({
          error: {
            code: 'FORBIDDEN',
            message: 'Insufficient role',
            traceId: request.traceId,
            timestamp: new Date().toISOString()
          }
        });
      }
    };
  });
});
