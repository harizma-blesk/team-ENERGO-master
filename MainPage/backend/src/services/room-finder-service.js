import { env } from '../config/env.js';

/* ───── HTTP helpers ───── */

const baseUrl = () => {
  const url = env.ROOM_FINDER_PHP_URL;
  if (!url) throw new Error('ROOM_FINDER_PHP_URL is not configured');
  return url.replace(/\/+$/, '');
};

const headers = () => {
  const h = {
    'Content-Type': 'application/json',
    Accept: 'application/json'
  };
  if (env.ROOM_FINDER_API_KEY) {
    h['X-API-Key'] = env.ROOM_FINDER_API_KEY;
  }
  return h;
};

async function javaFetch(path, init) {
  const url = `${baseUrl()}${path}`;

  console.log(`[room-finder] → ${init?.method ?? 'GET'} ${url}`);

  let res;
  try {
    res = await fetch(url, {
      ...init,
      headers: { ...headers(), ...(init?.headers ?? {}) },
      signal: AbortSignal.timeout(8_000)
    });
  } catch (err) {
    console.error(`[room-finder] Network error reaching ${url}:`, err.message);
    throw new Error(`Cannot reach Java server at ${url}: ${err.message}`);
  }

  console.log(`[room-finder] ← ${res.status} ${res.statusText}`);

  if (!res.ok) {
    const text = await res.text().catch(() => '');
    console.error(`[room-finder] Error body:`, text);
    throw new Error(`Java API ${res.status}: ${text}`);
  }
  return res.json();
}

/* ───── Public API ───── */

/** Health-check of Java server */
export async function roomFinderHealth() {
  return javaFetch('/api/bridge');
}

/** POST /api/bridge  — find free rooms via YOLO + schedule */
export async function findFreeRooms(req) {
  return javaFetch('/api/bridge', {
    method: 'POST',
    body: JSON.stringify(req)
  });
}

/** GET /api/schedule/auditories — list of all rooms */
export async function getAuditories() {
  return javaFetch('/api/schedule/auditories');
}

/** GET /api/schedule/journal — occupancy journal */
export async function getJournal(audId) {
  const path = audId != null ? `/api/schedule/journal/${audId}` : '/api/schedule/journal';
  return javaFetch(path);
}
