"use client";
import React from "react";
import { CustomBarChart } from "@/components/chart/BarChart";
import { useQuery } from "@tanstack/react-query";
import { getTeacherCourseStudentAnalytics } from "@/apiService/analytics";
import { ChartConfig } from "@/components/ui/chart";
import Loader from "@/components/Loader";

export default function StudentsPerCourse() {
  const { data, isLoading } = useQuery({
    queryKey: ["students-course"],
    queryFn: () => getTeacherCourseStudentAnalytics(),
    select: (data) =>
      data.courses.map((item) => ({
        course: item.course_name,
        students: item.active_students,
      })),
  });

  if (isLoading) return <Loader />;

  console.log(data);

  const chartConfig = {
    students: {
      label: "students",
      color: "hsl(var(--primary))",
    },
  } satisfies ChartConfig;

  return (
    <CustomBarChart
      chartConfig={chartConfig}
      dataKeyY='course'
      dataKeyX='students'
      chartData={data || []}
    />
  );
}
