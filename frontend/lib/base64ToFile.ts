export function base64ToFile(base64: string) {
    // Extract content type and base64 data
    const [metadata, base64Data] = base64.split(',');
    const contentType = metadata.split(':')[1].split(';')[0];

    // Decode base64
    const buffer = Buffer.from(base64Data, 'base64');

    // Create a single Blob directly from the buffer
    const blob = new Blob([buffer], { type: contentType });
    return new File([blob], "handwritten.jpg", { type: contentType });
}