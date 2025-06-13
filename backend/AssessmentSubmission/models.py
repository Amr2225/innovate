from django.db import models
from assessment.models import Assessment
from enrollments.models import Enrollments
from Code_Questions.models import CodingQuestion
from django.core.exceptions import ValidationError
from django.conf import settings
from django.core.files import File
import os
import json
from Code_Questions.utils.piston import run_code, prepare_code_for_piston
import uuid


class AssessmentSubmission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='submissions')
    enrollment = models.ForeignKey(Enrollments, on_delete=models.CASCADE, related_name='assessment_submissions')
    mcq_answers = models.JSONField(default=dict, help_text="Dictionary of question_id: selected_answer")
    handwritten_answers = models.JSONField(default=dict, help_text="Dictionary of question_id: image_path")
    codequestions_answers = models.JSONField(default=dict, help_text="Dictionary of question_id: code_answer")
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_submitted = models.BooleanField(default=False)

    class Meta:
        app_label = 'AssessmentSubmission'
        unique_together = ('assessment', 'enrollment')
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.enrollment.user.email} - {self.assessment.title}"

    def save(self, *args, **kwargs):
        # First save the model
        super().save(*args, **kwargs)

        if self.is_submitted:
            try:
                # Validate all answers are present
                self.validate_answers()

                # Create MCQ scores
                self.create_mcq_scores()

                # Create Handwritten scores
                self.create_handwritten_scores()
                
                # Create Code scores
                self.create_code_scores()
                
                # Update assessment score
                self.update_assessment_score()
            except Exception as e:
                # If any error occurs during validation or score creation,
                # set is_submitted back to False and save again
                self.is_submitted = False
                super().save(*args, **kwargs)
                raise e

    def validate_answers(self):
        """Validate that all questions have been answered"""
        from mcqQuestion.models import McqQuestion
        from HandwrittenQuestion.models import HandwrittenQuestion
        from Code_Questions.models import CodingQuestion
        from DynamicMCQ.models import DynamicMCQQuestions

        # Get all questions for the assessment
        mcq_questions = McqQuestion.objects.filter(
            assessment=self.assessment,
            created_by=self.enrollment.user
        )
        dynamic_mcq_questions = DynamicMCQQuestions.objects.filter(
            dynamic_mcq__assessment=self.assessment,
            created_by=self.enrollment.user
        )
        handwritten_questions = HandwrittenQuestion.objects.filter(
            assessment=self.assessment
        )
        
        code_questions = CodingQuestion.objects.filter(
            assessment_Id=self.assessment
        )

        # Check if there are any questions
        if not mcq_questions.exists() and not handwritten_questions.exists() and not code_questions.exists():
            raise ValidationError("No questions found for this assessment")

        # Check MCQ answers
        for question in mcq_questions:
            if str(question.id) not in self.mcq_answers:
                raise ValidationError(
                    f"Missing answer for MCQ question {question.id}")
            if self.mcq_answers[str(question.id)] not in question.options:
                raise ValidationError(
                    f"Invalid answer for MCQ question {question.id}")

        # Check Dynamic MCQ answers
        for question in dynamic_mcq_questions:
            if str(question.id) not in self.mcq_answers:
                raise ValidationError(
                    f"Missing answer for Dynamic MCQ question {question.id}")
            if self.mcq_answers[str(question.id)] not in question.options:
                raise ValidationError(
                    f"Invalid answer for Dynamic MCQ question {question.id}")

        # Check Handwritten answers
        for question in handwritten_questions:
            if str(question.id) not in self.handwritten_answers:
                raise ValidationError(
                    f"Missing answer for Handwritten question {question.id}")
            if not self.handwritten_answers[str(question.id)]:
                raise ValidationError(
                    f"Invalid answer for Handwritten question {question.id}")
            
        for question in code_questions:
            answer = self.codequestions_answers.get(str(question.id), "")
            # process answer (may be blank)

    def create_mcq_scores(self):
        """Create MCQQuestionScore records for each answer"""
        from MCQQuestionScore.models import MCQQuestionScore
        from mcqQuestion.models import McqQuestion
        from DynamicMCQ.models import DynamicMCQQuestions

        for question_id, selected_answer in self.mcq_answers.items():
            try:
                # Try to get regular MCQ question first
                try:
                    question = McqQuestion.objects.get(id=question_id)
                    is_dynamic = False
                except McqQuestion.DoesNotExist:
                    # If not found, try to get dynamic MCQ question
                    question = DynamicMCQQuestions.objects.get(
                        id=question_id,
                        dynamic_mcq__assessment=self.assessment,
                        created_by=self.enrollment.user
                    )
                    is_dynamic = True

                # Create or update score
                score_data = {
                    'enrollment': self.enrollment,
                    'selected_answer': selected_answer,
                    'is_correct': selected_answer == question.answer_key,
                    'score': question.question_grade if selected_answer == question.answer_key else 0
                }

                if is_dynamic:
                    score_data['dynamic_question'] = question
                else:
                    score_data['question'] = question

                MCQQuestionScore.objects.update_or_create(
                    question=question if not is_dynamic else None,
                    dynamic_question=question if is_dynamic else None,
                    enrollment=self.enrollment,
                    defaults=score_data
                )
            except (McqQuestion.DoesNotExist, DynamicMCQQuestions.DoesNotExist):
                raise ValidationError(f"Question {question_id} does not exist")
            except Exception as e:
                raise ValidationError(
                    f"Error creating score for question {question_id}: {str(e)}")

    def create_handwritten_scores(self):
        """Create HandwrittenQuestionScore records for each answer"""
        from HandwrittenQuestion.models import HandwrittenQuestionScore, HandwrittenQuestion
        from AI.evaluate_handwritten_answer import evaluate_handwritten_answer

        for question_id, file_path in self.handwritten_answers.items():
            question = HandwrittenQuestion.objects.get(id=question_id)

            try:
                # Get the full path to the file
                full_path = os.path.join(settings.MEDIA_ROOT, file_path)

                # Open the file
                with open(full_path, 'rb') as file_obj:
                    # Evaluate the answer using AI
                    print("Evaluating answer using AI")
                    score, feedback, extracted_text = evaluate_handwritten_answer(
                        question=question.question_text,
                        answer_key=question.answer_key,
                        student_answer_image=file_obj,
                        max_grade=float(question.max_grade)
                    )

                    print("Creating or updating score")
                    # Create or update score
                    score_obj, _ = HandwrittenQuestionScore.objects.update_or_create(
                        question=question,
                        enrollment=self.enrollment,
                        defaults={
                            'score': score,
                            'feedback': feedback,
                            'extracted_text': extracted_text
                        }
                    )

                    print("Saving the file using Django's file handling")
                    # Save the file using Django's file handling
                    with open(full_path, 'rb') as f:
                        score_obj.answer_image.save(
                            os.path.basename(file_path),
                            File(f),
                            save=True
                        )
                if os.path.exists(full_path):
                    os.remove(full_path)
                    print(f"Deleted temporary file: {full_path}")

                    # Delete empty parent directory
                    dir_path = os.path.dirname(full_path)
                    if os.path.exists(dir_path) and not os.listdir(dir_path):
                        os.rmdir(dir_path)
                        print(f"Deleted empty directory: {dir_path}")

            except Exception as e:
                raise ValidationError(
                    f"Error evaluating handwritten answer: {str(e)}")

    def create_code_scores(self):
        """Create CodingQuestionScore records for each code answer"""
        from Code_Questions.models import CodingQuestion, CodingQuestionScore, CodingScoreTestInteractions
        from Code_Questions.utils.piston import run_code, prepare_code_for_piston
        from enrollments.models import Enrollments

        for question_id, code_answer in self.codequestions_answers.items():
            try:
                question = CodingQuestion.objects.get(id=question_id)
                
                results = []
                total_cases = question.test_cases.count()
                passed_cases = 0

                # Prepare the code with wrapper
                wrapped_code = prepare_code_for_piston(code_answer)

                for case in question.test_cases.all():
                    result = run_code(
                        source_code=wrapped_code,
                        stdin=case.input_data,
                        language=question.language_id
                    )

                    output = (result.get("stdout") or "").strip()
                    expected = case.expected_output.strip()

                    # Handle any JSON structure
                    try:
                        # Try to parse the output and expected as JSON
                        output_data = json.loads(output)
                        expected_data = json.loads(expected)
                        
                        # Deep comparison of JSON structures
                        def compare_json_structures(data1, data2):
                            if type(data1) != type(data2):
                                return False
                            
                            if isinstance(data1, dict):
                                if set(data1.keys()) != set(data2.keys()):
                                    return False
                                return all(compare_json_structures(data1[k], data2[k]) for k in data1)
                            
                            if isinstance(data1, list):
                                if len(data1) != len(data2):
                                    return False
                                return all(compare_json_structures(x, y) for x, y in zip(data1, data2))
                            
                            return data1 == data2

                        passed = compare_json_structures(output_data, expected_data)
                    except json.JSONDecodeError:
                        # If JSON parsing fails, do regular string comparison
                        passed = output == expected

                    if passed:
                        passed_cases += 1

                    results.append({
                        "test_case_id": str(case.id),
                        "input": case.input_data,
                        "expected_output": expected,
                        "actual_output": output,
                        "passed": passed,
                        "error": result.get("stderr")
                    })
                print(results)
                # Calculate proportional score
                if total_cases > 0:
                    score = int((passed_cases / total_cases) * question.max_grade)
                else:
                    score = 0

                # Save or update the score in CodingQuestionScore
                score, created = CodingQuestionScore.objects.update_or_create(
                    question=question,
                    enrollment_id=self.enrollment,
                    student_answer=code_answer,
                    defaults={"score": score}
                )

                # Record individual test case results
                for result in results:
                    CodingScoreTestInteractions.objects.create(
                        questionScore=score,
                        testCase_id=result["test_case_id"],
                        passed=result["passed"]
                    )

            except CodingQuestion.DoesNotExist:
                raise ValidationError(f"Invalid coding question ID: {question_id}")
            except Exception as e:
                raise ValidationError(f"Error evaluating code answer: {str(e)}")

    def update_assessment_score(self):
        """Update the AssessmentScore with total score"""
        from assessment.models import AssessmentScore

        assessment_score, created = AssessmentScore.objects.get_or_create(
            enrollment=self.enrollment,
            assessment=self.assessment,
            defaults={'total_score': 0}
        )

        # The AssessmentScore's save method will automatically calculate the total score
        assessment_score.save()

    @classmethod
    def get_or_create_submission(cls, assessment, enrollment):
        """Get existing submission or create a new one"""
        submission, created = cls.objects.get_or_create(
            assessment=assessment,
            enrollment=enrollment,
            defaults={
                'mcq_answers': {},
                'handwritten_answers': {},
                'codequestions_answers': {},
                'is_submitted': False
            }
        )
        return submission
