"use client";
import React, { useEffect, useState, useRef } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
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
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Loader from "@/components/Loader";
import { changePassword } from "@/actions/changePassword";
import { toast } from "sonner";
import { Upload } from "lucide-react";
import Image from "next/image";

export default function InstitutionProfilePage() {
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const passwordFormRef = useRef<HTMLFormElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const queryClient = useQueryClient();

  const { data: user, isLoading } = useQuery({
    queryKey: ["user"],
    queryFn: () => getUserProfileData(),
  });

  const form = useForm<UserUpdate>({
    defaultValues: {
      name: "",
      email: "",
      logo: "",
    },
  });

  const { mutate: updateUser, isPending: isUpdatingUser } = useMutation({
    mutationFn: (data: UserUpdate | FormData) => updateUserProfileData(data),
    onSuccess: () => {
      toast.success("Profile updated successfully");
      queryClient.invalidateQueries({ queryKey: ["user"] });
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });

  useEffect(() => {
    if (!isLoading && user) {
      form.reset({
        name: user.name,
        email: user.email,
        logo: user.logo,
      });
    }
  }, [user, form, isLoading]);

  if (isLoading) return <Loader />;

  const onSubmit = (data: UserUpdate) => {
    updateUser(data);
  };

  const handleLogoClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) {
      toast.error("No file selected");
      return;
    }

    // Check file size (5MB limit)
    if (file.size > 5 * 1024 * 1024) {
      toast.error("File size should be under 1MB");
      return;
    }

    // Check if it's an image
    if (!file.type.startsWith("image/")) {
      toast.error("Please upload an image file");
      return;
    }

    setIsUploading(true);
    try {
      console.log(file);
      const formData = new FormData();
      formData.append("logo", file);
      console.log(formData);
      updateUser(formData);
    } catch {
      toast.error("Failed to upload logo");
    } finally {
      setIsUploading(false);
    }
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
    <div className='mx-auto p-6 max-w-4xl'>
      <h1 className='text-2xl font-bold mb-8'>Institution Profile Settings</h1>

      <div className='grid grid-cols-1 md:grid-cols-3 gap-8'>
        {/* Left Column - Logo Upload */}
        <div className='md:col-span-1'>
          <div className='relative'>
            <div
              className='relative group bg-orange-50 w-full aspect-square rounded-lg overflow-hidden border-2 border-dashed border-orange-200 hover:border-orange-400 transition-colors cursor-pointer'
              onClick={handleLogoClick}
            >
              {user?.logo && (
                <Image
                  src={user.logo}
                  alt='Institution Logo'
                  className='w-full h-full object-cover'
                  width={100}
                  height={100}
                />
              )}
              <div className='absolute inset-0 flex items-center justify-center bg-orange-500/50 opacity-0 group-hover:opacity-100 transition-opacity'>
                <Upload className='w-8 h-8 text-white' />
              </div>
            </div>
            <input
              type='file'
              ref={fileInputRef}
              onChange={handleFileChange}
              accept='image/*'
              className='hidden'
            />
            <p className='text-sm text-orange-600/70 mt-2 text-center'>
              Logo size should be under 5MB and image ratio needs to be 1:1
            </p>
          </div>
        </div>

        {/* Right Column - Profile Form */}
        <div className='md:col-span-2'>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className='space-y-6'>
              <FormField
                control={form.control}
                name='name'
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Institution Name</FormLabel>
                    <FormControl>
                      <Input placeholder='Enter institution name' {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name='email'
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Email</FormLabel>
                    <FormControl>
                      <Input placeholder='Enter email address' {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <Button
                type='submit'
                className='w-full bg-orange-500 hover:bg-orange-600 text-white'
                disabled={isUpdatingUser || isUploading}
              >
                {isUpdatingUser ? "Saving..." : "Save Changes"}
              </Button>
            </form>
          </Form>

          {/* Password Change Section */}
          <div className='mt-12 border-t border-orange-200 pt-8'>
            <h2 className='text-xl font-semibold mb-6 text-orange-900'>Change Password</h2>
            <form ref={passwordFormRef} onSubmit={handlePasswordChange} className='space-y-4'>
              <div>
                <Label htmlFor='old_password'>Old Password</Label>
                <Input
                  id='old_password'
                  name='old_password'
                  type='password'
                  placeholder='Enter old password'
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
                  placeholder='Enter new password'
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
                  placeholder='Confirm new password'
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
