import { api } from './client';

export async function findFreeRooms(query) {
  const res = await api.post('/rooms/find-free', query);
  return res.data;
}

export async function loadAuditories() {
  const res = await api.get('/rooms/auditories');
  return res.data;
}

export async function loadJournal(audId) {
  const res = await api.get('/rooms/journal', {
    params: audId != null ? { audId } : undefined
  });
  return res.data;
}

export async function roomFinderHealth() {
  const res = await api.get('/rooms/health');
  return res.data;
}

export async function loadLocations() {
    const res = await api.get('/rooms/locations');
    return res.data;
}
