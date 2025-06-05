"use client";
import React, { useState } from "react";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { BirthDatePicker } from "@/components/date-picker";

import { Button } from "@/components/ui/button";
import moment from "moment";

export default function SettingsSection() {
  const [date, setDate] = useState<Date>(moment().toDate());

  return (
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
                <BirthDatePicker date={date} setDate={(value) => setDate(value as Date)} />
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

        {/* <Calendar
          //   selected={field.value}
          //   onSelect={field.onChange}
          disabled={(date) => date > new Date() || date < new Date("1900-01-01")}
          captionLayout='dropdown'
          toYear={2010}
          fromYear={1900}
          classNames={{
            day_hidden: "invisible",
            dropdown:
              "px-2 py-1.5 rounded-md bg-popover text-popover-foreground text-sm  focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 ring-offset-background",
            caption_dropdowns: "flex gap-3",
            vhidden: "hidden",
            caption_label: "hidden",
          }}
        /> */}
      </div>
    </div>
  );
}
