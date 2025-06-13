'use client'
import { useState, useEffect } from 'react';
import { getVideo } from '@/store/videoStorage';


export default function useVideo(storageKey: string) {
    const [previewUrl, setPreviewUrl] = useState<string | null>(null);

    useEffect(() => {
        const loadVideo = async () => {
            if (storageKey) {
                const video = await getVideo(storageKey);
                if (video) {
                    const url = URL.createObjectURL(video);
                    setPreviewUrl(url);
                }
            }
        };
        loadVideo();
    }, [storageKey]);

    return { previewUrl };
}