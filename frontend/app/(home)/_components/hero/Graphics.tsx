"use client";

import React from "react";

import Lottie from "lottie-react";
import animationData from "../../_assets/heroAnimation.json";

export default function Graphics() {
  return <Lottie animationData={animationData} />;
}
