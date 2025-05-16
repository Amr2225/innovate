from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from .models import CodingQuestion, CodingQuestionScore
from .serializers import CodingQuestionSerializer, CodingQuestionScoreSerializer
from .utils.judge0 import run_code


class CodingQuestionListView(generics.ListCreateAPIView):
    queryset = CodingQuestion.objects.all()
    serializer_class = CodingQuestionSerializer

class CodingQuestionDetailView(generics.RetrieveAPIView):
    queryset = CodingQuestion.objects.all()
    serializer_class = CodingQuestionSerializer

class CodeSubmissionView(APIView):
    def post(self, request, question_id):
        try:
            question = CodingQuestion.objects.get(id=question_id)
        except CodingQuestion.DoesNotExist:
            return Response({"error": "Question not found"}, status=404)

        code = request.data.get('code')
        if not code:
            return Response({"error": "Code is required"}, status=400)

        results = []
        for case in question.test_cases.all():
            result = run_code(
                source_code=code,
                stdin=case.input_data,
                language_id=question.language_id
            )

            output = (result.get("stdout") or "").strip()
            expected = case.expected_output.strip()

            passed = output == expected
            results.append({
                "input": case.input_data,
                "expected_output": expected,
                "actual_output": output,
                "passed": passed,
                "error": result.get("stderr")
            })
        return Response({
            "results": results,
            "score": sum(1 for r in results if r["passed"]),
            "total": len(results)
        })

class CodequestionScoreListView(generics.ListAPIView):
    queryset = CodingQuestionScore.objects.all()
    serializer_class = CodingQuestionScoreSerializer