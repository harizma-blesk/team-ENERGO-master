import { randomUUID } from 'crypto';

export const newTraceId = () => `trc_${randomUUID()}`;
