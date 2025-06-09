# Chapter Module

This module manages chapters for courses, allowing teachers and institutions to organize course content.

## Features

- Create, retrieve, update and delete chapters
- Organize lectures within chapters
- Bulk creation of multiple chapters at once
- Nested creation of chapters with their lectures in one request
- Support for file uploads (videos and attachments) for lectures

## API Endpoints

### GET `/chapter/`

List all chapters accessible to the authenticated user.

### POST `/chapter/`

Create new chapters with lectures and file uploads in a single request.

For this endpoint, you should use `multipart/form-data` to include both JSON data and file uploads.

#### Request Format

The request should include:

1. A `chapters` field containing a JSON string with chapter and lecture data
2. Individual file uploads for videos and attachments using a specific naming pattern

Example request structure:

```
// Form fields
chapters: JSON string with chapter and lecture data
chapter_0_lecture_0_video: [FILE UPLOAD]
chapter_0_lecture_1_attachment: [FILE UPLOAD]
chapter_1_lecture_0_video: [FILE UPLOAD]
...
```

Example JSON for the `chapters` field:

```json
[
  {
    "title": "Chapter 1",
    "courseId": "UUID_OF_COURSE",
    "lectures": [
      {
        "title": "Lecture 1.1",
        "description": "Description of Lecture 1.1"
      },
      {
        "title": "Lecture 1.2",
        "description": "Description of Lecture 1.2"
      }
    ]
  },
  {
    "title": "Chapter 2",
    "courseId": "UUID_OF_COURSE",
    "lectures": [
      {
        "title": "Lecture 2.1",
        "description": "Description of Lecture 2.1"
      }
    ]
  }
]
```

#### File Upload Format

Files should be named according to this pattern:

- Videos: `chapter_{chapter_index}_lecture_{lecture_index}_video`
- Attachments: `chapter_{chapter_index}_lecture_{lecture_index}_attachment`

Where:

- `{chapter_index}` is the zero-based index of the chapter in the chapters array
- `{lecture_index}` is the zero-based index of the lecture within that chapter's lectures array

### GET `/chapter/<uuid:p_id>`

Retrieve a specific chapter by ID.

### PUT/PATCH `/chapter/<uuid:p_id>`

Update a specific chapter.

### DELETE `/chapter/<uuid:p_id>`

Delete a specific chapter.

## Permission Requirements

- `GET /chapter/`: Authenticated users
- `POST /chapter/`: Teachers or Institutions
- `GET /chapter/<uuid:p_id>`: Authenticated users
- `PUT/PATCH /chapter/<uuid:p_id>`: Teachers or Institutions
- `DELETE /chapter/<uuid:p_id>`: Teachers or Institutions

## Validation Rules

- Teachers can only manage chapters for courses in their institutions
- Institutions can only manage chapters for courses they own
- Chapter titles must be unique within a course
- When creating chapters with lectures, permissions are checked for each course

## File Upload Notes

- For video and attachment uploads, use `multipart/form-data` encoding
- Files are linked to lectures based on the naming pattern in the request
- Missing files for a lecture are treated as empty/null
- The request is processed in a transaction - if any part fails, all changes are rolled back
