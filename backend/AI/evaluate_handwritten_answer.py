from PIL import Image
from AI.baseAIClient import client
from main.settings import AI_MODEL
from AI.extract_json import extract_json
import io
import base64
import logging

logger = logging.getLogger(__name__)


def evaluate_handwritten_answer(question, answer_key, student_answer_image, max_grade):
    """
    Evaluate a handwritten answer using AI
    Args:
        question (str): The question text
        answer_key (str): The expected answer/key points (can be None)
        student_answer_image: The student's handwritten answer image file
        max_grade (float): Maximum possible grade for this question
    Returns:
        tuple: (score, feedback, extracted_text)
    """
    try:
        # Validate image file
        if not student_answer_image:
            raise ValueError("No image file provided")

        # Process image
        try:
            # Open image
            if hasattr(student_answer_image, 'read'):
                # If it's a file object, read it directly
                image = Image.open(student_answer_image)
                # Reset file pointer to beginning
                student_answer_image.seek(0)
            else:
                # If it's a path, open it
                image = Image.open(student_answer_image.path)

            # Validate image format
            if image.format not in ['JPEG', 'PNG', 'GIF', 'BMP']:
                raise ValueError(
                    "Unsupported image format. Please upload a JPEG, PNG, GIF, or BMP file")

            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Resize if too large (optional)
            max_size = (1200, 1200)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)

            # Convert to base64
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG", quality=95)
            buffered.seek(0)
            img_str = base64.b64encode(buffered.getvalue()).decode()

            # Reset file pointer
            if hasattr(student_answer_image, 'seek'):
                student_answer_image.seek(0)

        except (IOError, OSError) as e:
            raise ValueError(
                "Invalid or corrupted image file. Please upload a valid image file")
        except Exception as e:
            raise ValueError(f"Failed to process image: {str(e)}")

        # Prepare the combined prompt for solution generation, OCR, and evaluation
        combined_prompt = [
            {
                "role": "system",
                "content": """You are an expert teacher evaluating a student's handwritten answer. 
                Your task is to:
                1. First, determine if there is actually any handwritten text in the image
                2. If no text is present, explicitly state this and assign a score of 0
                3. If text is present, read and understand the handwritten answer even if the student writing is not clear
                4. Compare it with the answer key
                5. Provide a score based on accuracy, completeness, and clarity
                6. Give detailed feedback explaining:
                   - What was done well
                   - What could be improved
                   - Specific suggestions for better understanding

                When reading the image:
                - The image contains a student's handwritten answer to the question
                - Look for the actual answer text, not the question
                - The answer might be in any format (paragraphs, bullet points, etc.)
                - Read every word carefully, even if the handwriting is not perfect
                - Pay attention to any diagrams, equations, or special symbols
                
                Your response must be in this exact JSON format:
                {
                    "answer_key": "<the solution/answer key>",
                    "extracted_text": "<the student's handwritten answer as it appears in the image>",
                    "score": <float between 0 and max_grade>,
                    "feedback": "<detailed feedback explaining the score and suggesting improvements>"
                }"""
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""I have an image containing a student's handwritten answer to this question: "{question}"

                        The image shows the student's answer written by hand. Please:
                        1. Read and transcribe the student's handwritten answer from the image
                        2. Just read the image text don't make any assumptions.
                        3. If the extracted text is not clear, just say "The text is not clear" and assign a score of 0
                        4. Compare it with this answer key: {answer_key if answer_key else 'No answer key provided. Please solve the question first.'}
                        5. Evaluate the answer and provide feedback

                        The maximum grade for this question is {max_grade}.

                        Please transcribe exactly what the student has written in their answer.
                        """
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{img_str}"
                        }
                    }
                ]
            }
        ]

        # Get combined solution, OCR, and evaluation from AI
        completion = client.chat.completions.create(
            model=AI_MODEL,
            messages=combined_prompt,
            temperature=0.05,  # Lower temperature for more accurate transcription
            max_tokens=500
        )

        # Extract evaluation
        evaluation_data = extract_json(completion.choices[0].message.content)
        if not isinstance(evaluation_data, dict):
            raise ValueError("Invalid evaluation response format")

        if not all(key in evaluation_data for key in ['answer_key', 'extracted_text', 'score', 'feedback']):
            raise ValueError("Missing required fields in evaluation response")

        # Ensure score is within valid range
        score = float(evaluation_data['score'])
        score = max(0, min(score, max_grade))  # Clamp between 0 and max_grade

        return score, evaluation_data['feedback'], evaluation_data['extracted_text']

    except Exception as e:
        logger.error(f"Failed to evaluate handwritten answer: {str(e)}")
        raise ValueError(f"Failed to evaluate handwritten answer: {str(e)}")
