"use client";

import React from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Mail, Phone, MapPin } from "lucide-react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import * as z from "zod";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";

const formSchema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters."),
  email: z.string().email("Please enter a valid email address."),
  subject: z.string().min(5, "Subject must be at least 5 characters."),
  message: z.string().min(10, "Message must be at least 10 characters."),
});

export default function Contact() {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: "",
      email: "",
      subject: "",
      message: "",
    },
  });

  function onSubmit(values: z.infer<typeof formSchema>) {
    // Handle form submission
    console.log(values);
  }

  return (
    <div className='min-h-screen'>
      {/* Hero Section */}
      <section className='relative bg-gradient-to-b from-primary/5 to-background py-20'>
        <div className='container mx-auto px-4'>
          <div className='max-w-3xl mx-auto text-center'>
            <h1 className='text-4xl md:text-6xl font-bold tracking-tight mb-6'>Get in Touch</h1>
            <p className='text-xl text-muted-foreground mb-8'>
              Have questions? We&apos;re here to help. Reach out to us and we&apos;ll get back to
              you as soon as possible.
            </p>
          </div>
        </div>
      </section>

      {/* Contact Form and Info Section */}
      <section className='py-20'>
        <div className='container mx-auto px-4'>
          <div className='grid grid-cols-1 lg:grid-cols-2 gap-12'>
            {/* Contact Form */}
            <div className='bg-card p-8 rounded-lg border'>
              <h2 className='text-2xl font-bold mb-6'>Send us a Message</h2>
              <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className='space-y-6'>
                  <FormField
                    control={form.control}
                    name='name'
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Name</FormLabel>
                        <FormControl>
                          <Input placeholder='Your name' {...field} />
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
                          <Input placeholder='your.email@example.com' {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name='subject'
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Subject</FormLabel>
                        <FormControl>
                          <Input placeholder='What is this regarding?' {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name='message'
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Message</FormLabel>
                        <FormControl>
                          <Textarea
                            placeholder='Your message here...'
                            className='min-h-[150px]'
                            {...field}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <Button type='submit' className='w-full'>
                    Send Message
                  </Button>
                </form>
              </Form>
            </div>

            {/* Contact Information */}
            <div className='space-y-8'>
              <div className='bg-card p-8 rounded-lg border'>
                <h2 className='text-2xl font-bold mb-6'>Contact Information</h2>
                <div className='space-y-4'>
                  <div className='flex items-start gap-4'>
                    <Mail className='h-6 w-6 text-primary mt-1' />
                    <div>
                      <h3 className='font-semibold'>Email</h3>
                      <p className='text-muted-foreground'>support@yourlms.com</p>
                    </div>
                  </div>
                  <div className='flex items-start gap-4'>
                    <Phone className='h-6 w-6 text-primary mt-1' />
                    <div>
                      <h3 className='font-semibold'>Phone</h3>
                      <p className='text-muted-foreground'>+1 (555) 123-4567</p>
                    </div>
                  </div>
                  <div className='flex items-start gap-4'>
                    <MapPin className='h-6 w-6 text-primary mt-1' />
                    <div>
                      <h3 className='font-semibold'>Address</h3>
                      <p className='text-muted-foreground'>
                        123 Education Street
                        <br />
                        Tech City, TC 12345
                        <br />
                        United States
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Google Maps */}
              <div className='bg-card p-8 rounded-lg border'>
                <h2 className='text-2xl font-bold mb-6'>Our Location</h2>
                <div className='aspect-video w-full overflow-hidden rounded-lg'>
                  <iframe
                    src='https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d387193.30591910525!2d-74.25986432970718!3d40.697149422113014!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x89c24fa5d33f083b%3A0xc80b8f06e177fe62!2sNew%20York%2C%20NY%2C%20USA!5e0!3m2!1sen!2s!4v1647043087964!5m2!1sen!2s'
                    width='100%'
                    height='100%'
                    style={{ border: 0 }}
                    allowFullScreen
                    loading='lazy'
                    referrerPolicy='no-referrer-when-downgrade'
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
