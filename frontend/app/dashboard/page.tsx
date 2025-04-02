"use client";
import { signOutAction } from "@/actions/signOut";
import { Button } from "@/components/ui/button";
import useApi from "@/hooks/useApi";
import { useSession } from "next-auth/react";
import React, { useState } from "react";

export default function page() {
  const { data, status } = useSession();
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [courses, setCourses] = useState<any | undefined>();

  const api = useApi();

  // useEffect(() => {
  //   const fetchData = async () => {
  //     const res = await api.get("/courses/");

  //     setCourses(res.data);
  //     setIsLoading(false);
  //   };
  //   fetchData();
  // }, []);

  const getCourses = async () => {
    setIsLoading(true);
    const res = await api.get("/courses/");

    setCourses(res.data);
    setIsLoading(false);
  };

  if (isLoading) return <h1>Loading Courses ......</h1>;

  return (
    <div>
      <div>{JSON.stringify(data)}</div>
      <div>{JSON.stringify(courses)}</div>
      <form action={signOutAction}>
        <Button type='submit'>Signout</Button>
      </form>
      <Button type='button' onClick={getCourses}>
        Get Courses
      </Button>
    </div>
  );
}
