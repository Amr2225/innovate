import React, { use } from "react";
import { Book } from "lucide-react";

// Components
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button";

// Libs
import { getSession, logout } from "@/lib/session";
import { getNameInitials } from "@/lib/getNameInitials";
import { cn } from "@/lib/utils";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectValue,
  SelectContent,
  SelectItem,
  SelectTrigger,
} from "@/components/ui/select";
import DatePicker from "@/components/date-picker";

export default function StudentDashboard() {
  const session = use(getSession());
  if (!session) {
    logout();
    return;
  }

  const nameInitial = getNameInitials(session.user.name);

  return (
    <div className='w-full max-h-full'>
      <div className='bg-primary/20 h-[150px] w-full' />

      <div className='w-[80%] h-[650px] -mt-20 bg-white rounded-md shadow-m mx-auto'>
        <header className='py-5 mx-auto flex items-center justify-center gap-4'>
          <Avatar className='h-16 w-16 rounded-full'>
            <AvatarImage src='https://github.com/shadcn.png' alt={"user-profile"} />
            <AvatarFallback className='rounded-lg bg-primary text-white items-center justify-center flex'>
              {nameInitial}
            </AvatarFallback>
          </Avatar>

          <div className='flex flex-col'>
            <h1 className='text-2xl font-bold capitalize'>{session.user.name}</h1>
            <p className='text-gray-500'>Student Level / GPA</p>
            <p className='text-gray-500'>{session.user.email}</p>
          </div>
        </header>
        <Separator />
        <StudentTabs name={session.user.name.split(" ")[0]} />
      </div>
    </div>
  );
}

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

const StudentTabs = ({ name }: { name: string }) => {
  return (
    <Tabs defaultValue='dashboard'>
      <TabsList className='w-full grid grid-cols-7 py-2'>
        <TabsTrigger value='dashboard'>Dashboard</TabsTrigger>
        <TabsTrigger value='courses'>Courses</TabsTrigger>
        <TabsTrigger value='assignments'>Assignments</TabsTrigger>
        <TabsTrigger value='exams'>Exams</TabsTrigger>
        <TabsTrigger value='teachers'>Teachers</TabsTrigger>
        <TabsTrigger value='messages'>Messages</TabsTrigger>
        <TabsTrigger value='settings'>Settings</TabsTrigger>
      </TabsList>

      <TabsContent value='dashboard'>
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
            <VideoCard />
            <VideoCard />
            <VideoCard />
            <VideoCard />
            <VideoCard />
            {/* <VideoCard /> */}
          </div>
        </div>
      </TabsContent>

      <TabsContent value='courses'>
        <div>
          <h1 className='text-xl font-bold mt-3'>Courses (20)</h1>
          <div className='grid grid-cols-5 items-center gap-4 mb-5'>
            <div className='col-span-2'>
              <Label htmlFor='search'>Search:</Label>
              <Input id='search' placeholder='Search in your courses..' />
            </div>

            <div>
              <Label>Sort by:</Label>
              <Select defaultValue='latest'>
                <SelectTrigger className='w-full'>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value='latest'>Latest</SelectItem>
                  <SelectItem value='earliest'>Earliest</SelectItem>
                  <SelectItem value='alphabetical'>Alphabetical</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor='sort'>Status:</Label>
              <Select defaultValue='latest'>
                <SelectTrigger className='w-full'>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value='latest'>Latest</SelectItem>
                  <SelectItem value='earliest'>Earliest</SelectItem>
                  <SelectItem value='alphabetical'>Alphabetical</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor='sort'>Teacher:</Label>
              <Select defaultValue='latest'>
                <SelectTrigger className='w-full'>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value='latest'>Latest</SelectItem>
                  <SelectItem value='earliest'>Earliest</SelectItem>
                  <SelectItem value='alphabetical'>Alphabetical</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className='grid grid-cols-4 gap-4 pb-5'>
            <VideoCard />
            <VideoCard />
            <VideoCard />
            <VideoCard />
            <VideoCard />
          </div>
        </div>
      </TabsContent>

      <TabsContent value='settings'>
        <div>
          <h1 className='text-xl font-bold mt-3 mb-2'>Account Settings</h1>
          <div className='flex justify-center items-center gap-10'>
            <div className='border p-5 rounded-md'>
              <div className='bg-primary/10 w-full h-[200px] rounded-md' />
              <p className='text-sm text-wrap w-[70%] mx-auto text-gray-500 text-center mt-3'>
                Image size should be under 1MB and image ration needs to be 1:1
              </p>
            </div>

            <div className='w-full'>
              <form action='' className='space-y-3'>
                <div className='flex items-center justify-center gap-3'>
                  <div className='w-full'>
                    <Label htmlFor='first_name'>First Name</Label>
                    <Input id='first_name' placeholder='First Name' />
                  </div>

                  <div className='w-full'>
                    <Label htmlFor='middle_name'>Middle Name</Label>
                    <Input id='middle_name' placeholder='Middle Name' />
                  </div>

                  <div className='w-full'>
                    <Label htmlFor='last_name'>Last Name</Label>
                    <Input id='last_name' placeholder='Last Name' />
                  </div>
                </div>

                <div className='w-full flex items-center justify-center gap-3'>
                  <div className='w-full'>
                    <Label>Birth Date</Label>
                    <DatePicker date={new Date()} />
                  </div>
                  <div className='w-full'>
                    <Label htmlFor='age'>Age</Label>
                    <Input id='age' placeholder='Age' />
                  </div>
                </div>

                <div className='w-full'>
                  <Label htmlFor='email'>Email</Label>
                  <Input id='email' placeholder='Email' />
                </div>

                <Button type='submit' className='w-full mt-3'>
                  Save Changes
                </Button>
              </form>
            </div>
          </div>

          <div className='pb-5'>
            <h1 className='text-xl font-bold mt-3'>Change Password</h1>
            <form action='' className='space-y-3'>
              <div>
                <Label htmlFor='old_password'>Old Password</Label>
                <Input id='old_password' placeholder='Old Password' />
              </div>

              <div>
                <Label htmlFor='new_password'>New Password</Label>
                <Input id='new_password' placeholder='New Password' />
              </div>

              <div>
                <Label htmlFor='confirm_password'>Confirm Password</Label>
                <Input id='confirm_password' placeholder='Confirm Password' />
              </div>

              <Button type='submit' className='w-full mt-3'>
                Change Password
              </Button>
            </form>
          </div>
        </div>
      </TabsContent>
    </Tabs>
  );
};

const VideoCard = () => {
  return (
    <div className='w-full h-full border border-neutral-200 rounded-md'>
      <span className='w-[200px] block h-[100px] bg-white rounded-full' />
      <div className='flex flex-col items-start justify-center px-3 py-1'>
        <h4 className='font-bold text-sm'>Course Name</h4>
        <p className='text-sm text-gray-500'>Course Description</p>
      </div>
      <Separator />
      <div className='px-3 p-2'>
        <Button type='button' variant='default' className='w-full'>
          Watch Lecture
        </Button>
      </div>
    </div>
  );
};

interface DashboardCardsProps {
  count: number;
  title: string;
  color: string;
  Icon: React.ElementType;
  iconColor: string;
}

const DashboardCards = ({ count, title, color, Icon, iconColor }: DashboardCardsProps) => {
  return (
    <div className='w-full h-full mt-2'>
      <div
        className={cn("p-3 w-full h-full flex items-center justify-start gap-3 rounded-md", color)}
      >
        <span className='p-2 rounded-full bg-white'>
          <Icon className={iconColor} />
        </span>
        <div className='flex flex-col'>
          <h1 className='text-xl'>{count}</h1>
          <p className='text-sm font-semibold text-black/60'>{title}</p>
        </div>
      </div>
    </div>
  );
};
