/**
 * オフライン同期: IndexedDB キュー
 * オンライン復帰時にまとめてAPIへ送信
 */
import { openDB, IDBPDatabase } from "idb";
import type { EventCreate } from "./api";

const DB_NAME = "ikesu_offline";
const STORE = "event_queue";

let db: IDBPDatabase | null = null;

async function getDB() {
  if (!db) {
    db = await openDB(DB_NAME, 1, {
      upgrade(database) {
        if (!database.objectStoreNames.contains(STORE)) {
          database.createObjectStore(STORE, { keyPath: "local_id", autoIncrement: true });
        }
      },
    });
  }
  return db;
}

export async function queueEvent(event: EventCreate): Promise<void> {
  const database = await getDB();
  await database.add(STORE, { ...event, queued_at: new Date().toISOString() });
}

export async function getQueuedEvents(): Promise<Array<EventCreate & { local_id: number }>> {
  const database = await getDB();
  return database.getAll(STORE);
}

export async function clearQueue(ids: number[]): Promise<void> {
  const database = await getDB();
  const tx = database.transaction(STORE, "readwrite");
  await Promise.all(ids.map((id) => tx.store.delete(id)));
  await tx.done;
}

export async function syncOfflineQueue(
  syncFn: (events: EventCreate[]) => Promise<{ created_ids: number[]; errors: string[] }>
): Promise<{ synced: number; errors: string[] }> {
  const queued = await getQueuedEvents();
  if (queued.length === 0) return { synced: 0, errors: [] };

  const events = queued.map(({ local_id: _id, ...ev }) => ev as EventCreate);
  const result = await syncFn(events);

  // 成功分を削除
  if (result.created_ids.length > 0) {
    const successIds = queued
      .slice(0, result.created_ids.length)
      .map((q) => q.local_id);
    await clearQueue(successIds);
  }

  return { synced: result.created_ids.length, errors: result.errors };
}
