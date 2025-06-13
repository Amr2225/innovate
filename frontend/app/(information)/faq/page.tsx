"use client";
import React, { useState } from "react";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const categories = [
  "Nulla tempor odio ut fringilla",
  "Donec malesuada",
  "Quisque",
  "Toquam, in accumsan",
  "Ut sed orci",
  "Nullam non ante",
  "Phasellus",
  "Etiam eu libero elementum",
];

const faqs = [
  {
    question: "How can students log in after being registered?",
    answer:
      "Students can log in using your institution's access code and their respective national ID. This ensures secure and streamlined access for all students.",
    category: categories[0],
  },
  {
    question: "How do I reset my password?",
    answer:
      "Click on the 'Forgot Password' link on the login page and follow the instructions to reset your password via your registered email.",
    category: categories[1],
  },
  {
    question: "How can instructors add new courses?",
    answer:
      "Instructors can add new courses from the dashboard by clicking on 'Add Course' and filling in the required details.",
    category: categories[2],
  },
  {
    question: "How do I submit assignments?",
    answer:
      "Assignments can be submitted through the course page under the 'Assignments' section. Upload your file and click 'Submit'.",
    category: categories[3],
  },
  {
    question: "Can parents track student progress?",
    answer:
      "Yes, parents can track student progress through the parent portal, which provides real-time updates on grades and attendance.",
    category: categories[4],
  },
  {
    question: "What browsers are supported?",
    answer: "Our LMS supports all modern browsers including Chrome, Firefox, Safari, and Edge.",
    category: categories[5],
  },
  {
    question: "How do I contact support?",
    answer: "You can contact support via the 'Contact Us' page or by emailing support@yourlms.com.",
    category: categories[6],
  },
  {
    question: "How do I join a live class?",
    answer:
      "Live classes can be joined from the course dashboard at the scheduled time. Click the 'Join Live' button to enter the session.",
    category: categories[7],
  },
];

const userTypes = ["Students", "Instructors", "Parents", "Institutions"];

export default function FAQPage() {
  const [selectedCategory, setSelectedCategory] = useState(categories[0]);
  const [userType, setUserType] = useState(userTypes[0]);
  const [form, setForm] = useState({ subject: "", message: "" });

  const filteredFaqs = faqs.filter((faq) => faq.category === selectedCategory);

  return (
    <div className='bg-background min-h-screen py-8'>
      <div className='container mx-auto px-4'>
        <div className='mb-6 text-sm text-muted-foreground flex items-center gap-2'>
          <span>Home</span>
          <span className='mx-1'>/</span>
          <span className='font-semibold'>FAQs</span>
        </div>
        <h1 className='text-3xl font-bold mb-8'>Frequently asked questions</h1>
        <div className='grid grid-cols-1 md:grid-cols-12 gap-8'>
          {/* Categories */}
          <div className='md:col-span-2'>
            <div className='flex md:flex-col gap-2 md:gap-0'>
              {categories.map((cat) => (
                <button
                  key={cat}
                  className={`text-left px-4 py-2 border-l-4 md:border-l-4 md:rounded-none rounded-md w-full transition-colors text-sm font-medium ${
                    selectedCategory === cat
                      ? "bg-primary text-white md:bg-primary md:text-white border-primary"
                      : "bg-white text-black md:bg-transparent md:text-black border-transparent hover:bg-muted"
                  }`}
                  onClick={() => setSelectedCategory(cat)}
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>

          {/* FAQ Accordion */}
          <div className='md:col-span-7'>
            <Accordion type='multiple' className='space-y-4'>
              {filteredFaqs.map((faq) => (
                <AccordionItem
                  key={faq.question}
                  value={faq.question}
                  className='bg-white rounded-lg shadow-sm border'
                >
                  <AccordionTrigger className='px-6 py-4 text-base font-semibold hover:no-underline'>
                    {faq.question}
                  </AccordionTrigger>
                  <AccordionContent className='px-6 pb-6 pt-2 text-muted-foreground'>
                    {faq.answer}
                  </AccordionContent>
                </AccordionItem>
              ))}
            </Accordion>
          </div>

          {/* Ask a Question Form */}
          <div className='md:col-span-3'>
            <div className='bg-muted rounded-lg p-6'>
              <h2 className='text-lg font-semibold mb-2'>Don&apos;t find your answer?</h2>
              <p className='text-sm text-muted-foreground mb-4'>
                Don&apos;t worry, write your question here and our support team will help you.
              </p>
              <div className='mb-4'>
                <Label>User Type</Label>
                <Select value={userType} onValueChange={setUserType}>
                  <SelectTrigger className='w-full mt-1'>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {userTypes.map((type) => (
                      <SelectItem key={type} value={type}>
                        {type}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className='mb-2'>
                <Label>Subject</Label>
                <Input
                  value={form.subject}
                  onChange={(e) => setForm({ ...form, subject: e.target.value })}
                  placeholder='Subject'
                  className='mt-1'
                />
              </div>
              <div className='mb-4'>
                <Label>Message</Label>
                <Textarea
                  value={form.message}
                  onChange={(e) => setForm({ ...form, message: e.target.value })}
                  placeholder='Message'
                  className='mt-1 min-h-[80px]'
                />
              </div>
              <Button className='w-full bg-primary text-white hover:bg-primary/90'>
                Submit Question
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
