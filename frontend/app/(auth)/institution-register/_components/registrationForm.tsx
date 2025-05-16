"use client";
import React, { useEffect, useCallback, useRef } from "react";

// Hooks
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";

// Components
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";

// Schemas
import {
  InstitutionRegisterSchema,
  InstitutionRegisterSchemaType,
} from "@/schema/institutionRegisterSchema";

// Services & Store
import { institutionVerificationService } from "@/apiService/services";
import { useInstitutionRegistrationStore as store } from "@/store/institutionRegistrationStore";

export default function RegistrationForm({
  setIsPending,
}: {
  setIsPending: (isPending: boolean) => void;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const { addCreds, setFile } = store();

  const form = useForm<InstitutionRegisterSchemaType>({
    resolver: zodResolver(InstitutionRegisterSchema),
    defaultValues: {
      name: store.getState().name,
      email: store.getState().email,
      password: store.getState().password,
      confirm_password: store.getState().confirm_password,
      logo: null,
    },
    mode: "onChange",
  });

  // Handle file input state persistence
  // useEffect(() => {
  //   const storedLogo = store.getState().logo;
  //   if (storedLogo && inputRef.current) {
  //     if (typeof storedLogo === "string") {
  //       // If it's a string (URL), we don't need to set the file input
  //       return;
  //     }

  //     try {
  //       const dataTransfer = new DataTransfer();
  //       dataTransfer.items.add(storedLogo as File);
  //       inputRef.current.files = dataTransfer.files;
  //     } catch (error) {
  //       console.error("Error setting file input:", error);
  //     }
  //   }
  // }, []);

  const { mutate: sendEmail, isPending } = useMutation({
    mutationFn: ({ email, name }: { email: string; name: string }) =>
      institutionVerificationService.resendVerificationEmail(email, name),
    onSuccess: (message) => {
      toast.success(message as string);
      const formValues = form.getValues();
      addCreds(formValues.name, formValues.email, formValues.password, formValues.confirm_password);
      if (formValues.logo) {
        setFile(formValues.logo);
      }
    },
    onError: (error: Error) => {
      toast.error(error.message);
    },
  });

  useEffect(() => {
    setIsPending(isPending);
    return () => setIsPending(false);
  }, [isPending, setIsPending]);

  const handleNext = useCallback(
    (data: InstitutionRegisterSchemaType) => {
      sendEmail({ email: data.email, name: data.name });
    },
    [sendEmail]
  );

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleNext)} className='space-y-4' id='registration-form'>
        <FormField
          control={form.control}
          name='name'
          render={({ field }) => (
            <FormItem>
              <FormLabel>Institution Name</FormLabel>
              <FormControl>
                <Input placeholder='Enter your institution name' {...field} />
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
                <Input placeholder='Enter your email' {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name='password'
          render={({ field }) => (
            <FormItem>
              <FormLabel>Password</FormLabel>
              <FormControl>
                <Input type='password' placeholder='Enter your password' {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name='confirm_password'
          render={({ field }) => (
            <FormItem>
              <FormLabel>Confirm Password</FormLabel>
              <FormControl>
                <Input type='password' placeholder='Confirm your password' {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name='logo'
          render={({ field: { onChange, onBlur, name, disabled } }) => (
            <FormItem>
              <FormLabel>Institution Logo</FormLabel>
              <FormControl>
                <Input
                  type='file'
                  accept='image/*'
                  name={name}
                  disabled={disabled}
                  ref={inputRef}
                  onChange={(e) => {
                    const file = e.target.files?.[0];
                    if (file) {
                      // Validate file size (max 5MB)
                      if (file.size > 5 * 1024 * 1024) {
                        form.setError("logo", {
                          type: "manual",
                          message: "File size must be less than 5MB",
                        });
                        return;
                      }
                      // Validate file type
                      if (!file.type.startsWith("image/")) {
                        form.setError("logo", {
                          type: "manual",
                          message: "File must be an image",
                        });
                        return;
                      }
                      onChange(file);
                    } else {
                      onChange(null);
                    }
                  }}
                  onBlur={onBlur}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
      </form>
    </Form>
  );
}
