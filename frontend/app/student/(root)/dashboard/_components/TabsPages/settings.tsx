"use client";
import React, { useEffect, useState, useRef } from "react";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { BirthDatePicker } from "@/components/date-picker";

import { Button } from "@/components/ui/button";
import { useForm } from "react-hook-form";
import { UserUpdate } from "@/types/user.types";
import {
  Form,
  FormField,
  FormItem,
  FormLabel,
  FormControl,
  FormMessage,
} from "@/components/ui/form";
import { getUserProfileData, updateUserProfileData } from "@/apiService/userService";
import { useMutation, useQuery } from "@tanstack/react-query";
import Loader from "@/components/Loader";
import { changePassword } from "@/actions/changePassword";
import { toast } from "sonner";

export default function SettingsSection() {
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const passwordFormRef = useRef<HTMLFormElement>(null);
  const { data: user, isLoading } = useQuery({
    queryKey: ["user"],
    queryFn: () => getUserProfileData(),
  });

  const form = useForm<UserUpdate>({
    defaultValues: {
      first_name: "",
      middle_name: "",
      last_name: "",
      email: "",
      birth_date: new Date(),
      age: 0,
      avatar: "",
    },
  });

  const { mutate: updateUser, isPending: isUpdatingUser } = useMutation({
    mutationFn: (data: UserUpdate) => updateUserProfileData(data),
    onSuccess: () => {
      toast.success("User updated successfully");
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });

  useEffect(() => {
    if (!isLoading && user) {
      form.reset({
        first_name: user.first_name,
        middle_name: user.middle_name,
        last_name: user.last_name,
        email: user.email,
        birth_date: user.birth_date,
        age: user.age,
        avatar: user.avatar,
      });
    }
  }, [user, form, isLoading]);

  if (isLoading) return <Loader />;

  const onSubmit = (data: UserUpdate) => {
    updateUser(data);
  };

  const handlePasswordChange = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsChangingPassword(true);

    const formData = new FormData(e.currentTarget);
    const oldPassword = formData.get("old_password") as string;
    const newPassword = formData.get("new_password") as string;
    const confirmPassword = formData.get("confirm_password") as string;

    try {
      const result = await changePassword({
        oldPassword,
        newPassword,
        confirmPassword,
      });

      if (result.success) {
        toast.success(result.message);
        if (passwordFormRef.current) {
          passwordFormRef.current.reset();
        }
      } else {
        if (result.errors) {
          Object.entries(result.errors).forEach(([field, message]) => {
            toast.error(`${field}: ${message}`);
          });
        } else {
          toast.error(result.message);
        }
      }
    } finally {
      setIsChangingPassword(false);
    }
  };

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
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className='space-y-3'>
              <div className='flex items-center justify-center gap-3 w-fulll'>
                <FormField
                  control={form.control}
                  name='first_name'
                  render={({ field }) => (
                    <FormItem className='w-full'>
                      <FormLabel>First Name</FormLabel>
                      <FormControl>
                        <Input id='first_name' placeholder='First Name' {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name='middle_name'
                  render={({ field }) => (
                    <FormItem className='w-full'>
                      <FormLabel>Middle Name</FormLabel>
                      <FormControl>
                        <Input id='middle_name' placeholder='Middle Name' {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name='last_name'
                  render={({ field }) => (
                    <FormItem className='w-full'>
                      <FormLabel>Last Name</FormLabel>
                      <FormControl>
                        <Input id='last_name' placeholder='Last Name' {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <div className='w-full flex items-center justify-center gap-3'>
                <FormField
                  control={form.control}
                  name='birth_date'
                  render={({ field }) => (
                    <FormItem className='w-full'>
                      <FormLabel>Birth Date</FormLabel>
                      <FormControl>
                        <BirthDatePicker
                          date={field.value || ""}
                          setDate={(value) => field.onChange(value as Date)}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name='age'
                  render={({ field }) => (
                    <FormItem className='w-full'>
                      <FormLabel>Age</FormLabel>
                      <FormControl>
                        <Input id='age' placeholder='Age' {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <FormField
                control={form.control}
                name='email'
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Email</FormLabel>
                    <FormControl>
                      <Input id='email' placeholder='Email' {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <Button type='submit' className='w-full mt-3' disabled={isUpdatingUser}>
                {isUpdatingUser ? "Saving..." : "Save Changes"}
              </Button>
            </form>
          </Form>
        </div>
      </div>

      <div className='pb-5'>
        <h1 className='text-xl font-bold mt-3'>Change Password</h1>
        <form ref={passwordFormRef} onSubmit={handlePasswordChange} className='space-y-3'>
          <div>
            <Label htmlFor='old_password'>Old Password</Label>
            <Input
              id='old_password'
              name='old_password'
              type='password'
              placeholder='Old Password'
              disabled={isChangingPassword}
              required
            />
          </div>

          <div>
            <Label htmlFor='new_password'>New Password</Label>
            <Input
              id='new_password'
              name='new_password'
              type='password'
              placeholder='New Password'
              disabled={isChangingPassword}
              required
            />
          </div>

          <div>
            <Label htmlFor='confirm_password'>Confirm Password</Label>
            <Input
              id='confirm_password'
              name='confirm_password'
              type='password'
              placeholder='Confirm Password'
              disabled={isChangingPassword}
              required
            />
          </div>

          <Button type='submit' className='w-full mt-3' disabled={isChangingPassword}>
            {isChangingPassword ? "Changing Password..." : "Change Password"}
          </Button>
        </form>
      </div>
    </div>
  );
}
