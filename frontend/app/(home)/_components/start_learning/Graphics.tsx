"use client";
import React from "react";

import Lottie from "lottie-react";
import animationData from "../../_assets/learningAnimation.json";

export default function Graphics() {
  return <Lottie animationData={animationData} />;
}
