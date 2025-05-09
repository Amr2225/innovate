"use client";
import React, { useEffect } from "react";

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
  setCurrentStep?: (step: number) => void;
  setIsPending: (isPending: boolean) => void;
}) {
  const { addCreds } = store();

  const form = useForm({
    resolver: zodResolver(InstitutionRegisterSchema),
    defaultValues: {
      name: store.getState().name,
      email: store.getState().email,
      password: store.getState().password,
      confirm_password: store.getState().confirm_password,
      logo: null,
    },
  });

  const { mutate: sendEmail, isPending } = useMutation({
    mutationFn: (email: string) => institutionVerificationService.resendVerificationEmail(email),
    onSuccess: (message) => {
      toast.success(message as string);
      // setCurrentStep(2);
      addCreds(
        form.getValues("name"),
        form.getValues("email"),
        form.getValues("password"),
        form.getValues("confirm_password")
      );
    },
  });

  useEffect(() => {
    setIsPending(isPending);
    return () => setIsPending(false);
  }, [isPending, setIsPending]);

  const handleNext = (data: InstitutionRegisterSchemaType) => {
    //TODO: Save the data in the persistant storage
    // addCreds(data.name, data.email, data.password, data.confirm_password);
    // console.log(data);
    sendEmail(data.email);
  };

  return (
    <Form {...form}>
      <form
        onSubmit={form.handleSubmit(handleNext)}
        className='space-y-4'
        id='institution-registration-form'
      >
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
        {/* <Button type='submit' className='w-full'>
          Next
        </Button> */}
      </form>
    </Form>
  );
}
