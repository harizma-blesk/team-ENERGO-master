import bcrypt from 'bcryptjs';
import { createHash, randomBytes } from 'crypto';

const BCRYPT_ROUNDS = 10;

export const hashPassword = async (password) => bcrypt.hash(password, BCRYPT_ROUNDS);

export const verifyPassword = async (password, passwordHash) => bcrypt.compare(password, passwordHash);

export const sha256 = (value) => createHash('sha256').update(value).digest('hex');

export const generateOpaqueToken = (bytes = 48) => randomBytes(bytes).toString('base64url');
