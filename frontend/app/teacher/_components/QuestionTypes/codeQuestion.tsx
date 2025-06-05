import { Question } from "@/types/assessment.type";

export default function CodeQuestion({ question }: { question: Question }) {
  console.log(question);
  return <h1>Code Question</h1>;
}
