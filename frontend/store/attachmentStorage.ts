// Define the attachment metadata structure
export interface AttachmentMetadata {
    id: string;
    name: string;
    type: string;
    size: number;
    date: number;
    lectureId: string; // The ID of the lecture this attachment belongs to
}

// Initialize the IndexedDB database for attachments
export const initAttachmentDB = () => {
    return new Promise<IDBDatabase>((resolve, reject) => {
        const request = indexedDB.open('innovateTemp-course-db', 1);

        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);

        request.onupgradeneeded = (event) => {
            const db = (event.target as IDBOpenDBRequest).result;

            // Create store for attachment files
            if (!db.objectStoreNames.contains('attachments')) {
                db.createObjectStore('attachments');
            }

            // Create store for attachment metadata
            if (!db.objectStoreNames.contains('attachmentList')) {
                const store = db.createObjectStore('attachmentList', { keyPath: 'id' });
                // Create an index to quickly find attachments by lecture ID
                store.createIndex('byLectureId', 'lectureId', { unique: false });
            }

            // Create store for videos (ensure compatibility with videoStorage.ts)
            if (!db.objectStoreNames.contains('videos')) {
                db.createObjectStore('videos');
            }
        };
    });
};

// Save an attachment file for a specific lecture
// This will replace any existing attachment for that lecture
export const saveAttachment = async (file: File, lectureId: string): Promise<string> => {
    const db = await initAttachmentDB();

    // Generate a unique ID for the attachment
    const id = `attachment_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;

    // Create metadata object
    const metadata: AttachmentMetadata = {
        id,
        name: file.name,
        type: file.type,
        size: file.size,
        date: Date.now(),
        lectureId
    };

    return new Promise((resolve, reject) => {
        const transaction = db.transaction(['attachments', 'attachmentList'], 'readwrite');

        // First, check if an attachment already exists for this lecture
        const listStore = transaction.objectStore('attachmentList');
        const index = listStore.index('byLectureId');
        const getRequest = index.get(lectureId);

        getRequest.onsuccess = () => {
            // If there's an existing attachment, delete it first
            if (getRequest.result) {
                const existingId = getRequest.result.id;
                transaction.objectStore('attachments').delete(existingId);
                listStore.delete(existingId);
            }

            // Save the new file
            const attachmentStore = transaction.objectStore('attachments');
            attachmentStore.put(file, id);

            // Save the metadata
            listStore.put(metadata);
        };

        getRequest.onerror = () => reject(getRequest.error);
        transaction.oncomplete = () => resolve(id);
    });
};

// Get an attachment file by lecture ID
export const getAttachmentForLecture = async (lectureId: string) => {
    const db = await initAttachmentDB();

    // First, get the metadata to find the attachment ID
    const metadata = await getAttachmentMetadataForLecture(lectureId);
    if (!metadata) return null;

    // Then, get the actual file using the attachment ID
    return new Promise<File | null>((resolve, reject) => {
        const transaction = db.transaction('attachments', 'readonly');
        const store = transaction.objectStore('attachments');
        const request = store.get(metadata.id);

        request.onsuccess = () => resolve(request.result || null);
        request.onerror = () => reject(request.error);
    });
};

// Get attachment metadata by lecture ID
export const getAttachmentMetadataForLecture = async (lectureId: string): Promise<AttachmentMetadata | null> => {
    const db = await initAttachmentDB();
    return new Promise((resolve, reject) => {
        const transaction = db.transaction('attachmentList', 'readonly');
        const store = transaction.objectStore('attachmentList');
        const index = store.index('byLectureId');
        const request = index.get(lectureId);

        request.onsuccess = () => resolve(request.result || null);
        request.onerror = () => reject(request.error);
    });
};

// Delete an attachment by lecture ID
export const deleteAttachmentForLecture = async (lectureId: string) => {
    const db = await initAttachmentDB();

    // First, get the metadata to find the attachment ID
    const metadata = await getAttachmentMetadataForLecture(lectureId);
    if (!metadata) return false;

    return new Promise<boolean>((resolve, reject) => {
        const transaction = db.transaction(['attachments', 'attachmentList'], 'readwrite');

        // Delete the file
        transaction.objectStore('attachments').delete(metadata.id);

        // Delete the metadata
        transaction.objectStore('attachmentList').delete(metadata.id);

        transaction.oncomplete = () => resolve(true);
        transaction.onerror = () => reject(transaction.error);
    });
};

// Get attachment URL for display/download
export const getAttachmentUrlForLecture = async (lectureId: string): Promise<string | null> => {
    const file = await getAttachmentForLecture(lectureId);
    if (!file) return null;
    return URL.createObjectURL(file);
};

// Download attachment for a lecture
export const downloadAttachmentForLecture = async (lectureId: string): Promise<boolean> => {
    const file = await getAttachmentForLecture(lectureId);
    const metadata = await getAttachmentMetadataForLecture(lectureId);

    if (!file || !metadata) return false;

    const url = URL.createObjectURL(file);
    const a = document.createElement('a');
    a.href = url;
    a.download = metadata.name;
    document.body.appendChild(a);
    a.click();

    // Clean up
    document.body.removeChild(a);
    setTimeout(() => URL.revokeObjectURL(url), 100);
    return true;
};

// Check if a lecture has an attachment
export const hasAttachment = async (lectureId: string): Promise<boolean> => {
    const metadata = await getAttachmentMetadataForLecture(lectureId);
    return metadata !== null;
}; 