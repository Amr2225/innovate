"use client";
import React, { useState } from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Label } from "@radix-ui/react-label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useMutation } from "@tanstack/react-query";
import axios from "axios";
import { BASE_URL } from "@/apiService/api";

export default function Credits() {
  const [credits, setCredits] = useState<number>(0);

  const { mutate: purchaseCredits } = useMutation({
    mutationFn: async () => {
      const response = await axios.post(`${BASE_URL}/institution/payment/`, {});
      return response.data;
    },
    onSuccess: (url) => {
      window.location.href = url;
    },
  });

  return (
    <div className=' grid place-content-center'>
      <Card className='md:w-[500px] w-[350px]'>
        <CardHeader>
          <CardTitle>Credits</CardTitle>
          <CardDescription>Enter the amount of credits you want to purchase</CardDescription>
        </CardHeader>
        <CardContent>
          <Label htmlFor='credits'>Credits</Label>
          <Input
            type='text'
            id='credits'
            value={credits || ""}
            onChange={(e) => setCredits(+e.target.value)}
            className='[appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none'
          />
        </CardContent>
        <Button type='button' onClick={() => purchaseCredits()}>
          Purchase
        </Button>
      </Card>
    </div>
  );
}
