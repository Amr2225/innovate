// Define the image metadata structure
export interface ImageMetadata {
    id: string;
    name: string;
    type: string;
    size: number;
    date: number;
    lastModified: number;
    // entityId: string; // The ID or email of the entity this image belongs to (course, user, etc.)
}

// Initialize the IndexedDB database for images
export const initImageDB = () => {
    return new Promise<IDBDatabase>((resolve, reject) => {
        const request = indexedDB.open('innovateTemp-image-db', 1);

        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);

        request.onupgradeneeded = (event) => {
            const db = (event.target as IDBOpenDBRequest).result;

            // Create store for image files
            if (!db.objectStoreNames.contains('images')) {
                db.createObjectStore('images');
            }

            // Create store for image metadata
            if (!db.objectStoreNames.contains('imageList')) {
                const store = db.createObjectStore('imageList', { keyPath: 'id' });
                // Create an index to quickly find images by entity ID
                store.createIndex('byEntityId', 'entityId', { unique: false });
            }
        };
    });
};

// Save an image file for a specific entity
export const saveImage = async (file: File, imageKey: string): Promise<string> => {
    const db = await initImageDB();

    // Generate a unique ID for the image
    const id = `image_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;

    // Create metadata object
    const metadata: ImageMetadata = {
        id,
        name: file.name,
        type: file.type,
        size: file.size,
        lastModified: file.lastModified,
        date: Date.now(),
    };

    return new Promise((resolve, reject) => {
        const transaction = db.transaction(['images', 'imageList'], 'readwrite');

        // Save the image file
        const imageStore = transaction.objectStore('images');
        imageStore.put(file, imageKey);

        // Save the metadata
        const listStore = transaction.objectStore('imageList');
        listStore.put(metadata);

        transaction.oncomplete = () => resolve(imageKey);
        transaction.onerror = () => reject(transaction.error);
    });
};

// Get an image file by imageKey
export const getImage = async (imageKey: string) => {
    const db = await initImageDB();
    return new Promise<File | null>((resolve, reject) => {
        const transaction = db.transaction('images', 'readonly');
        const store = transaction.objectStore('images');
        const request = store.get(imageKey);

        request.onsuccess = () => resolve(request.result || null);
        request.onerror = () => reject(request.error);
    });
};

// Get image metadata by ID
export const getImageMetadata = async (imageKey: string): Promise<ImageMetadata | null> => {
    const db = await initImageDB();
    return new Promise((resolve, reject) => {
        const transaction = db.transaction('imageList', 'readonly');
        const store = transaction.objectStore('imageList');
        const request = store.get(imageKey);

        request.onsuccess = () => resolve(request.result || null);
        request.onerror = () => reject(request.error);
    });
};

// TODO: may be deleted Get all images for an entity
export const getImagesForEntity = async (entityId: string): Promise<ImageMetadata[]> => {
    const db = await initImageDB();
    return new Promise((resolve, reject) => {
        const transaction = db.transaction('imageList', 'readonly');
        const store = transaction.objectStore('imageList');
        const index = store.index('byEntityId');
        const request = index.getAll(entityId);

        request.onsuccess = () => resolve(request.result || []);
        request.onerror = () => reject(request.error);
    });
};

// Delete an image by ID
export const deleteImage = async (imageId: string): Promise<boolean> => {
    const db = await initImageDB();
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(['images', 'imageList'], 'readwrite');

        // Delete the file
        transaction.objectStore('images').delete(imageId);

        // Delete the metadata
        transaction.objectStore('imageList').delete(imageId);

        transaction.oncomplete = () => resolve(true);
        transaction.onerror = () => reject(transaction.error);
    });
};

// Get image URL for display
export const getImageUrl = async (imageKey: string): Promise<string | null> => {
    const file = await getImage(imageKey);
    if (!file) return null;
    return URL.createObjectURL(file);
};
