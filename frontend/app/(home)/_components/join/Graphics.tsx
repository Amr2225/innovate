"use client";
import React from "react";
import Lottie from "lottie-react";
import animationData from "../../_assets/joinAnimation2.json";

export default function Graphics() {
  return <Lottie animationData={animationData} className='size-1/3' />;
}
