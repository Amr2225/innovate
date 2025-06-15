import { api } from "./api";


interface StudentPerCourse {
    courses: {
        course_name: string;
        active_students: number;
    }[];
    overall_statistics: {
        total_courses: number;
        total_active_students: number;
    }
}

interface CourseAvgScore {
    courses: {
        course_name: string;
        avg_score: number;
        assessment_metrics: {
            average_score: number;
        }
    }[];
    overall_metrics: {
        total_courses: number;
        total_students: number;
        average_completion_rate: number;
        average_assessment_score: number;
    }
}

interface TopStudents {
    course_id: string;
    course_name: string;
    top_students: {
        student_id: string;
        student_name: string;
        total_grade: number;
    }[];
}

interface StudentDashboard {
    course_count: number;
    assignment_count: number;
    exam_count: number;
    quiz_count: number;
    submission_count: number;
    submitted_assignments_count: number;
    submitted_exams_count: number;
    submitted_quizzes_count: number;
}

interface InstitutionUsersCourseAnalytics {
    course_count: number;
    teacher_count: number;
    student_count: number;
}

export const getTeacherCourseStudentAnalytics = async (): Promise<StudentPerCourse> => {
    const response = await api.get('analytics/');

    if (response.status === 200) return response.data;
    throw new Error(response.data.message || "Something went wrong");
}

export const getCourseAvgScore = async (): Promise<CourseAvgScore> => {
    const response = await api.get('analytics/courses-metrics');

    if (response.status === 200) return response.data;
    throw new Error(response.data.message || "Something went wrong");
}


export const getTopStudents = async ({ courseId }: { courseId: string }): Promise<TopStudents> => {
    const response = await api.get(`analytics/top-students/${courseId}`);

    if (response.status === 200) return response.data;
    throw new Error(response.data.message || "Something went wrong");
}


export const studentAnalytics = async (): Promise<StudentDashboard> => {
    const response = await api.get('analytics/student-dashboard/');

    if (response.status === 200) return response.data;
    throw new Error(response.data.message || "Something went wrong");
}


export const getCourseUsersCount = async (): Promise<InstitutionUsersCourseAnalytics> => {
    const response = await api.get('analytics/course-count/');

    if (response.status === 200) return response.data;
    throw new Error(response.data.message || "Something went wrong");
}