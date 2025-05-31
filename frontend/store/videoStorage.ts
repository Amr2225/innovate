// TODO: Make a general storage init file for all the storage files
export const initVideoDB = () => {
    return new Promise<IDBDatabase>((resolve, reject) => {
        const request = indexedDB.open('innovateTemp-course-db', 1);

        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);

        request.onupgradeneeded = (event) => {
            const db = (event.target as IDBOpenDBRequest).result;

            // Create store for videos
            if (!db.objectStoreNames.contains('videos')) {
                db.createObjectStore('videos');
            }

            // Create store for attachment files (ensure compatibility with attachmentStorage.ts)
            if (!db.objectStoreNames.contains('attachments')) {
                db.createObjectStore('attachments');
            }

            // Create store for attachment metadata (ensure compatibility with attachmentStorage.ts)
            if (!db.objectStoreNames.contains('attachmentList')) {
                const store = db.createObjectStore('attachmentList', { keyPath: 'id' });
                // Create an index to quickly find attachments by lecture ID
                store.createIndex('byLectureId', 'lectureId', { unique: false });
            }
        };
    });
};

export const saveVideo = async (key: string, file: File) => {
    const db = await initVideoDB();
    return new Promise((resolve, reject) => {
        const transaction = db.transaction('videos', 'readwrite');
        const store = transaction.objectStore('videos');
        const request = store.put(file, key);

        request.onsuccess = () => resolve(true);
        request.onerror = () => reject(request.error);
    });
};

export const getVideo = async (key: string) => {
    const db = await initVideoDB();
    return new Promise<File | null>((resolve, reject) => {
        const transaction = db.transaction('videos', 'readonly');
        const store = transaction.objectStore('videos');
        const request = store.get(key);

        request.onsuccess = () => resolve(request.result || null);
        request.onerror = () => reject(request.error);
    });
};

export const deleteVideo = async (key: string) => {
    const db = await initVideoDB();
    return new Promise((resolve, reject) => {
        const transaction = db.transaction('videos', 'readwrite');
        const store = transaction.objectStore('videos');
        const request = store.delete(key);

        request.onsuccess = () => resolve(true);
        request.onerror = () => reject(request.error);
    });
};