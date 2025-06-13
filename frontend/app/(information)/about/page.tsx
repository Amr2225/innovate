import React from "react";
import { Button } from "@/components/ui/button";
import { ArrowRight, BookOpen, GraduationCap, Users, Clock, Shield } from "lucide-react";
import Link from "next/link";

export default function About() {
  return (
    <div className='min-h-screen'>
      {/* Hero Section */}
      <section className='relative bg-gradient-to-b from-primary/5 to-background py-20'>
        <div className='container mx-auto px-4'>
          <div className='max-w-3xl mx-auto text-center'>
            <h1 className='text-4xl md:text-6xl font-bold tracking-tight mb-6'>
              Transforming Education Through Technology
            </h1>
            <p className='text-xl text-muted-foreground mb-8'>
              We&apos;re building the future of learning with our innovative Learning Management
              System, connecting students, educators, and institutions in a seamless digital
              ecosystem.
            </p>
            <div className='flex gap-4 justify-center'>
              <Button size='lg' asChild>
                <Link href='/contact'>
                  Get Started <ArrowRight className='ml-2 h-4 w-4' />
                </Link>
              </Button>
              <Button size='lg' variant='outline' asChild>
                <Link href='/demo'>Request Demo</Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className='py-20 bg-background'>
        <div className='container mx-auto px-4'>
          <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8'>
            <div className='p-6 rounded-lg border bg-card'>
              <BookOpen className='h-12 w-12 text-primary mb-4' />
              <h3 className='text-xl font-semibold mb-2'>Comprehensive Learning</h3>
              <p className='text-muted-foreground'>
                Access course materials, assignments, and resources all in one place. Our platform
                supports various content types and learning styles.
              </p>
            </div>
            <div className='p-6 rounded-lg border bg-card'>
              <GraduationCap className='h-12 w-12 text-primary mb-4' />
              <h3 className='text-xl font-semibold mb-2'>Expert-Led Education</h3>
              <p className='text-muted-foreground'>
                Learn from experienced educators and industry professionals. Our platform connects
                students with top-tier instructors.
              </p>
            </div>
            <div className='p-6 rounded-lg border bg-card'>
              <Users className='h-12 w-12 text-primary mb-4' />
              <h3 className='text-xl font-semibold mb-2'>Collaborative Learning</h3>
              <p className='text-muted-foreground'>
                Engage with peers through discussion forums, group projects, and real-time
                collaboration tools.
              </p>
            </div>
            <div className='p-6 rounded-lg border bg-card'>
              <Clock className='h-12 w-12 text-primary mb-4' />
              <h3 className='text-xl font-semibold mb-2'>Flexible Learning</h3>
              <p className='text-muted-foreground'>
                Learn at your own pace with 24/7 access to course materials and recorded lectures.
              </p>
            </div>
            <div className='p-6 rounded-lg border bg-card'>
              <Shield className='h-12 w-12 text-primary mb-4' />
              <h3 className='text-xl font-semibold mb-2'>Secure Platform</h3>
              <p className='text-muted-foreground'>
                Your data is protected with enterprise-grade security measures and regular backups.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* About Us Section */}
      <section className='py-20 bg-primary/5'>
        <div className='container mx-auto px-4'>
          <div className='max-w-3xl mx-auto text-center'>
            <h2 className='text-3xl font-bold mb-6'>About Us</h2>
            <p className='text-lg text-muted-foreground mb-8'>
              We are a team of educators, technologists, and innovators passionate about making
              quality education accessible to everyone. Our Learning Management System is designed
              to empower both students and educators with the tools they need to succeed in the
              digital age.
            </p>
            <div className='grid grid-cols-1 md:grid-cols-3 gap-8 mt-12'>
              <div>
                <h3 className='text-2xl font-bold text-primary mb-2'>1000+</h3>
                <p className='text-muted-foreground'>Active Students</p>
              </div>
              <div>
                <h3 className='text-2xl font-bold text-primary mb-2'>50+</h3>
                <p className='text-muted-foreground'>Expert Instructors</p>
              </div>
              <div>
                <h3 className='text-2xl font-bold text-primary mb-2'>100+</h3>
                <p className='text-muted-foreground'>Courses Available</p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
