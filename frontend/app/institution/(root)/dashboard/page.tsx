import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import React from "react";

export default function InstitutionDashboard() {
  return (
    <div className='grid grid-cols-1 md:grid-cols-6 gap-4'>
      <Card className='col-span-2'>
        <CardHeader>
          <CardTitle>Total Credits</CardTitle>
        </CardHeader>
      </Card>

      <Card className='col-span-2 h-[150px]'>
        <CardHeader>
          <CardTitle>Total Credits</CardTitle>
        </CardHeader>
      </Card>

      <Card className='col-span-2'>
        <CardHeader>
          <CardTitle>Total Credits</CardTitle>
        </CardHeader>
      </Card>

      <Card className='col-span-3 h-[200px]'>
        <CardHeader>
          <CardTitle>Total Credits</CardTitle>
        </CardHeader>
      </Card>

      <Card className='col-span-3'>
        <CardHeader>
          <CardTitle>Total Credits</CardTitle>
        </CardHeader>
      </Card>

      <Card className='col-span-6 h-[200px]'>
        <CardHeader>
          <CardTitle>Total Credits</CardTitle>
          <CardDescription>Description</CardDescription>
        </CardHeader>
      </Card>
    </div>
  );
}
