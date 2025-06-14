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
import { Upload } from "lucide-react";

export default function TeacherProfilePage() {
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
      toast.success("Profile updated successfully");
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
    <div className=' mx-auto p-6'>
      <h1 className='text-2xl font-bold mb-8'>Teacher Profile Settings</h1>

      <div className='grid grid-cols-1 md:grid-cols-3 gap-8'>
        {/* Left Column - Profile Image */}
        <div className='md:col-span-1'>
          <div className='relative group'>
            <div className='bg-primary/10 w-full aspect-square rounded-lg overflow-hidden border-2 border-dashed border-primary/20 hover:border-primary/40 transition-colors'>
              <div className='absolute inset-0 flex items-center justify-center'>
                <Upload className='w-8 h-8 text-primary/40 group-hover:text-primary/60 transition-colors' />
              </div>
            </div>
            <p className='text-sm text-muted-foreground mt-2 text-center'>
              Image size should be under 1MB and image ratio needs to be 1:1
            </p>
          </div>
        </div>

        {/* Right Column - Profile Form */}
        <div className='md:col-span-2'>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className='space-y-4'>
              <div className='grid grid-cols-1 md:grid-cols-3 gap-4'>
                <FormField
                  control={form.control}
                  name='first_name'
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>First Name</FormLabel>
                      <FormControl>
                        <Input placeholder='First Name' {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name='middle_name'
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Middle Name</FormLabel>
                      <FormControl>
                        <Input placeholder='Middle Name' {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name='last_name'
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Last Name</FormLabel>
                      <FormControl>
                        <Input placeholder='Last Name' {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <div className='grid grid-cols-1 md:grid-cols-2 gap-4'>
                <FormField
                  control={form.control}
                  name='birth_date'
                  render={({ field }) => (
                    <FormItem>
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
                    <FormItem>
                      <FormLabel>Age</FormLabel>
                      <FormControl>
                        <Input placeholder='Age' {...field} />
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
                      <Input placeholder='Email' {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <Button type='submit' className='w-full' disabled={isUpdatingUser}>
                {isUpdatingUser ? "Saving..." : "Save Changes"}
              </Button>
            </form>
          </Form>

          {/* Password Change Section */}
          <div className='mt-12'>
            <h2 className='text-xl font-semibold mb-4'>Change Password</h2>
            <form ref={passwordFormRef} onSubmit={handlePasswordChange} className='space-y-4'>
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

              <Button type='submit' className='w-full' disabled={isChangingPassword}>
                {isChangingPassword ? "Changing Password..." : "Change Password"}
              </Button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
