"use client";
import React from "react";
import Lottie from "lottie-react";

import handWrittenAnimationData from "../../_assets/handwrittenAnimation.json";
import codingAnimationData from "../../_assets/codingAnimation.json";
import mcqAnimationData from "../../_assets/mcqAnimation.json";

export function HandwrittenGraphics() {
  return <Lottie animationData={handWrittenAnimationData} />;
}

export function CodingGraphics() {
  return <Lottie animationData={codingAnimationData} />;
}

export function MCQGrahpics() {
  return <Lottie animationData={mcqAnimationData} />;
}
