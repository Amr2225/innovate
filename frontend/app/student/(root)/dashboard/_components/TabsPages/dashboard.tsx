"use client";
import React from "react";
import DashboardCards from "../dashboardCards";
import { Book } from "lucide-react";
import CourseCard from "../courseCard";
import { studentAnalytics } from "@/apiService/analytics";
import { Skeleton } from "@/components/ui/skeleton";
import { useQuery } from "@tanstack/react-query";
import { getStudentCourses } from "@/apiService/enrollmentService";

export default function DashboardSection({ name }: { name: string }) {
  const { data: dashboardData, isLoading } = useQuery({
    queryKey: ["student-dashboard"],
    queryFn: () => studentAnalytics(),
  });

  const { data: coursesData, isLoading: coursesLoading } = useQuery({
    queryKey: ["student-courses"],
    queryFn: () => getStudentCourses({ page_size: 1000, pageParam: 1 }),
  });

  const dashboardCardData = [
    {
      count: dashboardData?.course_count || 0,
      title: "Courses",
      color: "bg-primary/20",
      icon: Book,
      iconColor: "text-primary",
    },
    {
      count: dashboardData?.assignment_count || 0,
      title: "Assignments",
      color: "bg-blue-500/20",
      icon: Book,
      iconColor: "text-blue-500",
    },
    {
      count: dashboardData?.exam_count || 0,
      title: "Exams",
      color: "bg-green-400/20",
      icon: Book,
      iconColor: "text-green-500",
    },
    {
      count: dashboardData?.quiz_count || 0,
      title: "Quizzes",
      color: "bg-primary/20",
      icon: Book,
      iconColor: "text-primary",
    },
    {
      count: dashboardData?.submitted_assignments_count || 0,
      title: "Submitted Assessments",
      color: "bg-blue-500/20",
      icon: Book,
      iconColor: "text-blue-500",
    },
  ];

  return (
    <div>
      <h1 className='text-xl font-bold mt-3'>Dashboard</h1>
      <div className='grid grid-cols-5 gap-4'>
        {dashboardCardData.map((data, index) =>
          isLoading ? (
            <Skeleton className='w-full h-[50px]' key={index} />
          ) : (
            <DashboardCards
              key={index}
              count={data.count}
              title={data.title}
              color={data.color}
              Icon={data.icon}
              iconColor={data.iconColor}
              submitted_assignments_count={dashboardData?.submitted_assignments_count || 0}
              submitted_quizzes_count={dashboardData?.submitted_quizzes_count || 0}
              submitted_exams_count={dashboardData?.submitted_exams_count || 0}
              isHover={data.title === "Submitted Assessments"}
            />
          )
        )}
      </div>

      <h1 className='text-xl font-bold mt-10 capitalize mb-2'>Continue Learning, {name || ""}</h1>
      <div className='grid grid-cols-4 gap-4 pb-5'>
        {coursesLoading ? (
          <Skeleton className='w-full h-[50px]' />
        ) : coursesData?.length && coursesData?.length > 0 ? (
          coursesData?.map((course) => (
            <CourseCard
              key={course.id}
              courseName={course.name}
              courseDescription={course.description}
              courseId={course.id}
            />
          ))
        ) : (
          <p className='text-2xl font-semibold text-center text-gray-500 col-span-4'>
            No lectures found
          </p>
        )}
      </div>
    </div>
  );
}
