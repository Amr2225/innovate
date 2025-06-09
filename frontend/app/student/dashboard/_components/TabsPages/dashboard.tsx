import React from "react";
import DashboardCards from "../dashboardCards";
import { Book } from "lucide-react";
import CourseCard from "../courseCard";

const dashboardCardData = [
  {
    count: 10,
    title: "Courses",
    color: "bg-primary/20",
    icon: Book,
    iconColor: "text-primary",
  },
  {
    count: 200,
    title: "Assignments",
    color: "bg-blue-500/20",
    icon: Book,
    iconColor: "text-blue-500",
  },
  {
    count: 120,
    title: "Exams",
    color: "bg-green-400/20",
    icon: Book,
    iconColor: "text-green-500",
  },
  {
    count: 10,
    title: "Courses",
    color: "bg-primary/20",
    icon: Book,
    iconColor: "text-primary",
  },
  {
    count: 200,
    title: "Assignments",
    color: "bg-blue-500/20",
    icon: Book,
    iconColor: "text-blue-500",
  },
];

export default function DashboardSection({ name }: { name: string }) {
  return (
    <div>
      <h1 className='text-xl font-bold mt-3'>Dashboard</h1>
      <div className='grid grid-cols-5 gap-4'>
        {dashboardCardData.map((data, index) => (
          <DashboardCards
            key={index}
            count={data.count}
            title={data.title}
            color={data.color}
            Icon={data.icon}
            iconColor={data.iconColor}
          />
        ))}
      </div>

      <h1 className='text-xl font-bold mt-5 capitalize'>Continue Learning, {name || ""}</h1>
      <div className='grid grid-cols-4 gap-4 pb-5'>
        <CourseCard />
        <CourseCard />
        <CourseCard />
        <CourseCard />
        <CourseCard />
      </div>
    </div>
  );
}
