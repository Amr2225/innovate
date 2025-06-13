export const initHandwrittenDB = () => {
    return new Promise<IDBDatabase>((resolve, reject) => {
        const request = indexedDB.open('innovate-handwritten-db', 1);

        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);

        request.onupgradeneeded = (event) => {
            const db = (event.target as IDBOpenDBRequest).result;

            // Create store for handwritten images
            if (!db.objectStoreNames.contains('images')) {
                db.createObjectStore('images');
            }
        };
    });
};

export const saveHandwrittenImage = async (key: string, imageData: string) => {
    const db = await initHandwrittenDB();
    return new Promise((resolve, reject) => {
        const transaction = db.transaction('images', 'readwrite');
        const store = transaction.objectStore('images');
        const request = store.put(imageData, key);

        request.onsuccess = () => resolve(true);
        request.onerror = () => reject(request.error);
    });
};

export const getHandwrittenImage = async (key: string) => {
    const db = await initHandwrittenDB();
    return new Promise<string | null>((resolve, reject) => {
        const transaction = db.transaction('images', 'readonly');
        const store = transaction.objectStore('images');
        if (!key) return resolve(null);
        const request = store.get(key);

        request.onsuccess = () => resolve(request.result || null);
        request.onerror = () => reject(request.error);
    });
};

export const deleteHandwrittenImage = async (key: string) => {
    const db = await initHandwrittenDB();
    return new Promise((resolve, reject) => {
        const transaction = db.transaction('images', 'readwrite');
        const store = transaction.objectStore('images');
        const request = store.delete(key);

        request.onsuccess = () => resolve(true);
        request.onerror = () => reject(request.error);
    });
};
