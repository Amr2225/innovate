import { NextRequest, NextResponse } from 'next/server';
import { mkdir, writeFile } from 'fs/promises';
import { join } from 'path';

export async function POST(request: NextRequest) {
    try {
        const formData = await request.formData();
        const file = formData.get('file') as File;
        const assessmentId = formData.get('assessmentId') as string;
        const questionId = formData.get('questionId') as string;

        if (!file || !assessmentId || !questionId) {
            return NextResponse.json(
                { error: 'File, assessmentId, and questionId are required' },
                { status: 400 }
            );
        }

        // Create directory for assessment if it doesn't exist
        const uploadDir = join(process.cwd(), 'public', 'uploads', assessmentId);
        await mkdir(uploadDir, { recursive: true });

        // Generate unique filename with question ID
        const filename = `${questionId}-${Date.now()}${getExtension(file.name)}`;
        const filepath = join(uploadDir, filename);

        // Convert file to buffer and save
        const bytes = await file.arrayBuffer();
        const buffer = Buffer.from(bytes);
        await writeFile(filepath, buffer);

        // Return the relative path to the saved file
        const relativePath = `/uploads/${assessmentId}/${filename}`;

        return NextResponse.json({
            success: true,
            filePath: relativePath
        });

    } catch (error) {
        console.error('Error uploading file:', error);
        return NextResponse.json(
            { error: 'Error uploading file' },
            { status: 500 }
        );
    }
}

function getExtension(filename: string): string {
    const parts = filename.split('.');
    return parts.length > 1 ? `.${parts[parts.length - 1]}` : '';
}
