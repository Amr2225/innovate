"use client";
import React from "react";
import Lottie from "lottie-react";
import animationData from "../../_assets/joinAnimation.json";

export default function Graphics() {
  return <Lottie animationData={animationData} className='md:size-1/3' />;
}
