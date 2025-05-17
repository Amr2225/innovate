from huggingface_hub import InferenceClient
from django.conf import settings
import json
import re
import json5
import logging
import PyPDF2
import io
import base64
from PIL import Image

# Set up logging
logger = logging.getLogger(__name__)

try:
    client = InferenceClient(
        provider=settings.AI_PROVIDER,
        api_key=settings.AI_API_KEY,
    )
except Exception as e:
    logger.error(f"Failed to initialize AI client: {str(e)}")
    raise

dmcq = [
    {
        "role": "system",
        "content": "You are an assistant who generates multiple-choice questions (MCQs) based on a given context. Focus on creating questions that test key details and understanding of the topic. Each question should have one correct answer and three incorrect options that are plausible but distinct. Ensure clarity and relevance in both the questions and answer choices. the correct answer the numebr of correct question, don't repeat the correct answer number 2 times in a row"
    },
    {
        "role": "user",
        "content": ""  # This will be populated with the actual context
    }
]
def generate_mcqs_from_pdf(pdf_file, num_questions=10):
    """
    Extract text from PDF and generate MCQs using AI
    Args:
        pdf_file: InMemoryUploadedFile or path to PDF file
        num_questions (int): Number of questions to generate
    Returns:
        list: List of MCQ dictionaries
    """
    try:
        # First extract text from the PDF
        text = extract_text_from_pdf(pdf_file)
        
        # Then generate MCQs from the extracted text
        return generate_mcqs_from_text(text, num_questions)
        
    except Exception as e:
        logger.error(f"Failed to generate MCQs from PDF: {str(e)}")
        raise ValueError(f"Failed to generate MCQs from PDF: {str(e)}")

def extract_text_from_pdf(pdf_file):
    """
    Extract text from a PDF file
    Args:
        pdf_file: InMemoryUploadedFile or path to PDF file
    Returns:
        str: Extracted text from PDF
    """
    try:
        # If pdf_file is a file object (from request.FILES)
        if hasattr(pdf_file, 'read'):
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file.read()))
        else:
            # If pdf_file is a file path
            pdf_reader = PyPDF2.PdfReader(pdf_file)

        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"

        # Clean up the extracted text
        text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with single space
        text = text.strip()  # Remove leading/trailing whitespace

        if not text:
            raise ValueError("No text could be extracted from the PDF")

        return text

    except Exception as e:
        logger.error(f"PDF extraction error: {str(e)}")
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")

def generate_mcqs_from_text(text, num_questions=10):
    """
    Generate MCQs from text using AI
    Args:
        text (str): Input text to generate questions from
        num_questions (int): Number of questions to generate
    Returns:
        list: List of MCQ dictionaries
    """
    try:
        # Update the prompt with the text
        dmcq[1]['content'] = f"""
        context: {text}

        Based on the provided context, generate {num_questions} multiple-choice questions. Your response must be strictly in the following JSON format:

        [{{"question": "<question text>",
          "options": ["<option 1>", "<option 2>", "<option 3>", "<option 4>"],
          "correct_answer": "<exact text of the correct option>"}}]
        """

        # Make API call to generate MCQs
        completion = client.chat.completions.create(
            model=settings.AI_MODEL,
            messages=dmcq,
            temperature=0.9,
            max_tokens=1000,
        )

        # Extract and validate JSON from response
        mcq_data = extract_json(completion.choices[0].message.content)
        
        if not isinstance(mcq_data, list):
            raise ValueError("Invalid response format from AI")
            
        # Validate each question
        for q in mcq_data:
            if not isinstance(q, dict):
                raise ValueError("Invalid question format in AI response")
            if not all(key in q for key in ['question', 'options', 'correct_answer']):
                raise ValueError("Missing required fields in AI response")
            if not isinstance(q['options'], list) or len(q['options']) != 4:
                raise ValueError("Invalid options format in AI response")

        return mcq_data[:num_questions]

    except Exception as e:
        logger.error(f"MCQ generation error: {str(e)}")
        raise ValueError(f"Failed to generate MCQs: {str(e)}")

def extract_json(llm_output):
    """Extract and validate JSON from LLM output"""
    try:
        # Match first JSON object/array in string
        json_match = re.search(r'(\[.*\]|\{.*\})', llm_output, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON structure found in the output")
            
        json_str = json_match.group(1)
        
        # Try standard JSON first
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # If standard JSON fails, try json5 which is more lenient
            return json5.loads(json_str)
            
    except Exception as e:
        logger.error(f"Failed to extract JSON from LLM output: {str(e)}")
        logger.debug(f"Raw LLM output: {llm_output}")
        raise ValueError(f"Failed to parse AI response: {str(e)}")

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
                raise ValueError("Unsupported image format. Please upload a JPEG, PNG, GIF, or BMP file")
                
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
            raise ValueError("Invalid or corrupted image file. Please upload a valid image file")
        except Exception as e:
            raise ValueError(f"Failed to process image: {str(e)}")

        # Prepare the combined prompt for solution generation, OCR, and evaluation
        combined_prompt = [
            {
                "role": "system",
                "content": """You are an expert teacher evaluating a student's handwritten answer. 
                Your task is to:
                1. Read and understand the handwritten answer even if the student writing is not clear
                2. Compare it with the answer key
                3. Provide a score based on accuracy, completeness, and clarity
                4. Give detailed feedback explaining:
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
2. Compare it with this answer key: {answer_key if answer_key else 'No answer key provided. Please solve the question first.'}
3. Evaluate the answer and provide feedback

The maximum grade for this question is {max_grade}.

Please transcribe exactly what the student has written in their answer."""
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
            model=settings.AI_MODEL,
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

def extract_text_from_image(image_file):
    """
    Extract text from an image using Hugging Face's OCR model
    Args:
        image_file: The image file (can be file object or path)
    Returns:
        str: Extracted text from the image
    """
    try:
        # Open and preprocess the image
        if hasattr(image_file, 'read'):
            image = Image.open(image_file)
        else:
            image = Image.open(image_file.path)
            
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
            
        # Resize if too large (optional)
        max_size = (1200, 1200)
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Convert to base64
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        # Prepare the prompt for OCR
        ocr_prompt = [
            {
                "role": "system",
                "content": """You are an expert at reading and transcribing text from images. 
                Your task is to:
                1. Read all text in the image
                2. Return ONLY the text content, nothing else
                3. Do not include any base64 data or image information
                4. If there are mathematical equations or symbols, transcribe them accurately
                5. Preserve the original formatting and structure of the text"""
            },
            {
                "role": "user",
                "content": f"Read and transcribe all text from this image. Return ONLY the text content: {img_str}"
            }
        ]

        # Get OCR result from AI
        ocr_completion = client.chat.completions.create(
            model=settings.AI_MODEL,
            messages=ocr_prompt,
            temperature=0.3,  # Lower temperature for more accurate transcription
            max_tokens=1000
        )

        # Get the extracted text directly from the response
        extracted_text = ocr_completion.choices[0].message.content.strip()
        
        # Remove any potential base64 data that might have been included
        if "base64" in extracted_text.lower():
            # Try to extract only the actual text content
            lines = extracted_text.split('\n')
            text_lines = [line for line in lines if not any(x in line.lower() for x in ['base64', 'data:', 'image', 'jpeg', 'png'])]
            extracted_text = '\n'.join(text_lines)
        
        if not extracted_text:
            raise ValueError("No text could be extracted from the image")
            
        # Clean up the extracted text
        text = re.sub(r'\s+', ' ', extracted_text)  # Replace multiple spaces with single space
        text = text.strip()  # Remove leading/trailing whitespace
        
        return text
        
    except Exception as e:
        logger.error(f"Image text extraction error: {str(e)}")
        raise ValueError(f"Failed to extract text from image: {str(e)}")
