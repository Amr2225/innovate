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
from django.core.exceptions import ValidationError

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


def get_mcq_prompt():
    """Get a fresh copy of the MCQ prompt template"""
    return [
        {
            "role": "system",
            "content": "You are an assistant who generates multiple-choice questions (MCQs) based on a given context. Focus on creating questions that test key details and understanding of the topic. Each question should have one correct answer and three incorrect options that are plausible but distinct. Ensure clarity and relevance in both the questions and answer choices. the correct answer the numebr of correct question, don't repeat the correct answer number 2 times in a row"
        },
        {
            "role": "user",
            "content": ""  # This will be populated with the actual context
        }
    ]


def generate_mcqs_from_pdf(pdf_file, num_questions=10, seed=None, difficulty='3'):
    """
    Extract text from PDF and generate MCQs using AI
    Args:
        pdf_file: InMemoryUploadedFile or path to PDF file
        num_questions (int): Number of questions to generate
        seed (int): Optional seed for randomization
        difficulty (str): Difficulty level ('1'=Very Easy, '2'=Easy, '3'=Medium, '4'=Hard, '5'=Very Hard)
    Returns:
        list: List of MCQ dictionaries
    """
    try:
        # First extract text from the PDF
        text = extract_text_from_pdf(pdf_file)

        # Then generate MCQs from the extracted text
        return generate_mcqs_from_text(text, num_questions, seed, difficulty)

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
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()  # Remove leading/trailing whitespace

        if not text:
            raise ValueError("No text could be extracted from the PDF")

        return text

    except Exception as e:
        logger.error(f"PDF extraction error: {str(e)}")
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")


def generate_mcqs_from_text(text, num_questions=10, seed=None, difficulty='3', num_options=4):
    """
    Generate MCQs from text using AI
    Args:
        text (str): Input text to generate questions from
        num_questions (int): Number of questions to generate
        seed (int): Optional seed for randomization to ensure different questions per student
        difficulty (str): Difficulty level ('1'=Very Easy, '2'=Easy, '3'=Medium, '4'=Hard, '5'=Very Hard)
        num_options (int): Number of options per question (2-4, default=4)
    Returns:
        list: List of MCQ dictionaries
    """
    try:
        logger.info(f"Generating {num_questions} MCQs from text with difficulty level {difficulty} and {num_options} options per question")

        # Map difficulty level to description
        difficulty_map = {
            '1': 'Very Easy',
            '2': 'Easy',
            '3': 'Medium',
            '4': 'Hard',
            '5': 'Very Hard'
        }
        difficulty_desc = difficulty_map.get(difficulty, 'Medium')

        # Check if text is too large and truncate if necessary
        max_text_length = 35000  # Increased from 5000 to match the limit in generate_mcqs_from_multiple_pdfs
        if len(text) > max_text_length:
            logger.warning(f"Text length ({len(text)}) exceeds maximum ({max_text_length}). Truncating...")
            text = text[:max_text_length]

        # Prepare difficulty requirements based on level
        difficulty_requirements = {
            'Very Easy': '- Focus on basic facts and definitions\n- Use simple, direct language\n- Make correct answer obvious\n- Avoid complex concepts',
            'Easy': '- Include some basic application questions\n- Use clear, straightforward language\n- Make correct answer fairly obvious\n- Include some simple concept questions',
            'Medium': '- Mix factual recall with understanding\n- Include some application questions\n- Use moderately complex language\n- Make distractors plausible',
            'Hard': '- Focus on deeper understanding\n- Include analysis and application\n- Use more complex language\n- Make distractors very plausible',
            'Very Hard': '- Focus on complex analysis and synthesis\n- Include higher-order thinking\n- Use sophisticated language\n- Make all options very plausible'
        }

        # Get a fresh copy of the prompt template
        prompt = get_mcq_prompt()

        # Update the prompt with the text and add variability instructions
        prompt[1]['content'] = f"""
        context: {text}

        Based on the provided context, generate {num_questions} multiple-choice questions at {difficulty_desc} difficulty level from the context only. Your response must be strictly in the following JSON format:

        [{{"question": "<question text>",
          "options": ["<option 1>", "<option 2>", "<option 3>", "<option 4>", "<option 5>", "<option 6>"],
          "correct_answer": "<exact text of the correct option>"}}]

        CRITICAL REQUIREMENTS:
        1. Return ONLY the JSON array, no other text
        2. Each question MUST have EXACTLY {num_options} options - no more, no less
        3. The correct_answer MUST match EXACTLY one of the options
        4. Each option MUST be a string
        5. The options array MUST contain EXACTLY {num_options} strings
        6. Do not include any explanations or additional text
        7. Ensure the JSON is valid and properly formatted if not try to generate the question again
        8. Use double quotes for all strings
        9. Do not include any trailing commas
        10. Do not include any comments or markdown formatting
        11. IMPORTANT: You MUST generate EXACTLY {num_options} options for each question

        DIFFICULTY REQUIREMENTS:
        For {difficulty_desc} level questions:
        {difficulty_requirements[difficulty_desc]}

        VARIABILITY REQUIREMENTS:
        1. Generate questions that test different aspects of the content
        2. Use various question types (definition, application, analysis, etc.)
        3. Vary the complexity and depth of questions
        4. Ensure distractors are plausible but clearly incorrect
        5. Avoid similar question structures or patterns
        6. Mix both direct and indirect questions
        7. Include questions that test both factual recall and understanding

        Example of valid response with {num_options} options:
        [
            {{
                "question": "What is the capital of France?",
                "options": ["London", "Berlin", "Paris", "Madrid", "Rome", "Vienna"][:num_options],
                "correct_answer": "Paris"
            }}
        ]
        """

        # Adjust temperature based on difficulty
        temperature_map = {
            '1': 0.75,  # Lower temperature for more consistent, easier questions
            '2': 0.8,
            '3': 0.85,
            '4': 0.9,
            '5': 0.95   # Higher temperature for more creative, harder questions
        }
        temperature = temperature_map.get(difficulty, 0.8)

        # Make API call to generate MCQs with difficulty-adjusted parameters
        logger.debug(f"Making API call to generate MCQs with difficulty {difficulty_desc} and {num_options} options")

        try:
            # Add timeout and retry logic for API calls
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    completion = client.chat.completions.create(
                        model=settings.AI_MODEL,
                        messages=prompt,
                        temperature=temperature,
                        max_tokens=1000,
                        seed=seed if seed is not None else None,
                    )
                    break  # Success, exit retry loop
                except Exception as api_error:
                    if "Bad request" in str(api_error) and attempt < max_retries - 1:
                        # If it's a "Bad request" error and not the last attempt, try with shorter context
                        logger.warning(f"Bad request error on attempt {attempt+1}, truncating context and retrying...")
                        text = text[:len(text)//2]  # Cut text in half
                        prompt[1]['content'] = prompt[1]['content'].replace(f"context: {text}", f"context: {text}")
                        continue
                    else:
                        # On last attempt or different error, re-raise
                        raise
        except Exception as api_error:
            logger.error(f"API error when generating MCQs: {str(api_error)}")
            # Return default questions as fallback for API errors
            return [
                {
                    "question": "This is a sample question due to API limitations. Please try again later.",
                    "options": ["Option A", "Option B", "Option C", "Option D", "Option E", "Option F"][:num_options],
                    "correct_answer": "Option A"
                }
            ]

        # Extract and validate JSON from response
        logger.debug("Extracting JSON from AI response")
        try:
            mcq_data = extract_json(completion.choices[0].message.content)
        except Exception as json_error:
            logger.error(f"Error extracting JSON from response: {str(json_error)}")
            # Return default questions as fallback for JSON parsing errors
            return [
                {
                    "question": "This is a sample question due to response format issues. Please try again.",
                    "options": ["Option A", "Option B", "Option C", "Option D", "Option E", "Option F"][:num_options],
                    "correct_answer": "Option A"
                }
            ]

        if not isinstance(mcq_data, list):
            logger.error("Invalid response format: not a list")
            # Return default questions as fallback for invalid format
            return [
                {
                    "question": "This is a sample question due to response format issues. Please try again.",
                    "options": ["Option A", "Option B", "Option C", "Option D", "Option E", "Option F"][:num_options],
                    "correct_answer": "Option A"
                }
            ]

        # Validate number of options in each question
        for mcq in mcq_data:
            if len(mcq['options']) != num_options:
                logger.warning(f"Question has {len(mcq['options'])} options instead of {num_options}, adjusting...")
                # If too many options, truncate
                if len(mcq['options']) > num_options:
                    mcq['options'] = mcq['options'][:num_options]
                # If too few options, add more
                while len(mcq['options']) < num_options:
                    mcq['options'].append(f"Option {chr(65 + len(mcq['options']))}")

        logger.info(f"Successfully generated {len(mcq_data)} MCQs at {difficulty_desc} difficulty with {num_options} options each")
        return mcq_data[:num_questions]

    except Exception as e:
        logger.error(f"MCQ generation error: {str(e)}")
        raise ValueError(f"Failed to generate MCQs: {str(e)}")


def extract_json(llm_output):
    """Extract and validate JSON from LLM output"""
    try:
        logger.info("Starting JSON extraction from AI response")
        logger.debug(f"Raw AI output: {llm_output}")

        # Clean the output string
        cleaned_output = llm_output.strip()

        # Remove any markdown code block markers
        cleaned_output = re.sub(r'```json\s*|\s*```', '', cleaned_output)

        # Find the JSON array or object
        json_match = re.search(r'(\[.*\]|\{.*\})', cleaned_output, re.DOTALL)
        if not json_match:
            logger.error("No JSON structure found in the output")
            raise ValueError("No JSON structure found in the output")

        json_str = json_match.group(1)

        # Clean the JSON string
        json_str = re.sub(r',\s*]', ']', json_str)  # Remove trailing commas
        # Remove trailing commas in objects
        json_str = re.sub(r',\s*}', '}', json_str)
        # Fix missing commas between objects
        json_str = re.sub(r'}\s*{', '},{', json_str)
        # Fix missing commas between arrays
        json_str = re.sub(r']\s*\[', '],[', json_str)

        # Try standard JSON first
        try:
            logger.debug("Attempting standard JSON parsing")
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.warning(f"Standard JSON parsing failed: {str(e)}")
            logger.debug("Attempting json5 parsing")

            # Try json5 which is more lenient
            try:
                return json5.loads(json_str)
            except Exception as json5_error:
                logger.error(f"JSON5 parsing failed: {str(json5_error)}")

                # Last resort: try to fix common JSON issues
                try:
                    # Fix missing quotes around keys
                    json_str = re.sub(
                        r'([{,])\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', json_str)
                    # Fix missing quotes around string values
                    json_str = re.sub(
                        r':\s*([a-zA-Z_][a-zA-Z0-9_]*)([,}])', r':"\1"\2', json_str)
                    # Fix missing commas between array elements
                    json_str = re.sub(r'"\s*"', '","', json_str)
                    # Fix missing commas between object properties
                    json_str = re.sub(r'"\s*"', '","', json_str)
                    # Fix missing commas between objects in array
                    json_str = re.sub(r'}\s*{', '},{', json_str)
                    # Fix missing commas between arrays
                    json_str = re.sub(r']\s*\[', '],[', json_str)
                    # Fix trailing commas
                    json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)

                    # Try parsing again
                    try:
                        return json.loads(json_str)
                    except json.JSONDecodeError:
                        # If still fails, try to extract just the array part
                        array_match = re.search(
                            r'\[(.*)\]', json_str, re.DOTALL)
                        if array_match:
                            array_content = array_match.group(1)
                            # Split by object boundaries and parse each object
                            objects = re.findall(r'\{[^{}]*\}', array_content)
                            parsed_objects = []
                            for obj in objects:
                                try:
                                    parsed_obj = json.loads(obj)
                                    if all(key in parsed_obj for key in ['question', 'options', 'correct_answer']):
                                        parsed_objects.append(parsed_obj)
                                except json.JSONDecodeError:
                                    continue
                            if parsed_objects:
                                return parsed_objects

                    raise ValueError(
                        f"Failed to parse JSON after fixing: {str(e)}")
                except Exception as fix_error:
                    logger.error(f"JSON fixing failed: {str(fix_error)}")
                    raise ValueError(f"Failed to parse AI response: {str(e)}")

    except Exception as e:
        logger.error(f"Failed to extract JSON from AI output: {str(e)}")
        logger.debug(f"Raw AI output: {llm_output}")
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
            text_lines = [line for line in lines if not any(
                x in line.lower() for x in ['base64', 'data:', 'image', 'jpeg', 'png'])]
            extracted_text = '\n'.join(text_lines)

        if not extracted_text:
            raise ValueError("No text could be extracted from the image")

        # Clean up the extracted text
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', extracted_text)
        text = text.strip()  # Remove leading/trailing whitespace

        return text

    except Exception as e:
        logger.error(f"Image text extraction error: {str(e)}")
        raise ValueError(f"Failed to extract text from image: {str(e)}")


def generate_mcq_questions(context, num_questions, difficulty='3'):
    """
    Generate MCQ questions from the given context using AI

    Args:
        context (str): The text context to generate questions from
        num_questions (int): Number of questions to generate
        difficulty (str): Difficulty level ('1'=Very Easy, '2'=Easy, '3'=Medium, '4'=Hard, '5'=Very Hard)

    Returns:
        list: List of dictionaries containing questions, options, and correct answers
    """
    try:
        # Map difficulty level to description
        difficulty_map = {
            '1': 'Very Easy',
            '2': 'Easy',
            '3': 'Medium',
            '4': 'Hard',
            '5': 'Very Hard'
        }
        difficulty_desc = difficulty_map.get(difficulty, 'Medium')

        # Prepare the prompt for the AI
        messages = [
            {
                "role": "system",
                "content": """You are an expert at generating multiple-choice questions. Your task is to create clear, relevant, and well-structured questions based on the given context.
                You must respond with a valid JSON array containing the questions. Do not include any other text or explanation."""
            },
            {
                "role": "user",
                "content": f"""
                Generate {num_questions} multiple-choice questions from the following context.
                Difficulty level: {difficulty_desc}
                
                Context:
                {context}
                
                For each question, provide:
                1. A clear and concise question
                2. Four options (A, B, C, D)
                3. The correct answer
                
                Your response must be a valid JSON array with this exact structure:
                [
                    {{
                        "question": "Question text",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "correct_answer": "Option A"
                    }}
                ]
                
                Make sure the questions:
                - Are relevant to the context
                - Have one and only one correct answer
                - Have plausible distractors
                - Match the specified difficulty level ({difficulty_desc})
                
                Return ONLY the JSON array, nothing else.
                """
            }
        ]

        # Call the AI model
        completion = client.chat.completions.create(
            model=settings.AI_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=1000,
        )

        # Get the response and clean it
        response_text = completion.choices[0].message.content.strip()

        # Try to extract JSON from the response
        try:
            # First try direct JSON parsing
            questions = json.loads(response_text)
        except json.JSONDecodeError:
            # If that fails, try to extract JSON using regex
            json_match = re.search(r'(\[.*\])', response_text, re.DOTALL)
            if not json_match:
                raise ValueError("Could not find valid JSON in the response")
            questions = json.loads(json_match.group(1))

        # Validate the response
        if not isinstance(questions, list):
            raise ValueError("Response is not a list")

        if len(questions) != num_questions:
            raise ValueError(
                f"Expected {num_questions} questions, got {len(questions)}")

        for q in questions:
            if not isinstance(q, dict):
                raise ValueError("Question is not a dictionary")

            if not all(k in q for k in ['question', 'options', 'correct_answer']):
                raise ValueError("Question missing required fields")

            if not isinstance(q['options'], list) or len(q['options']) != 4:
                raise ValueError("Question must have exactly 4 options")

            if q['correct_answer'] not in q['options']:
                raise ValueError("Correct answer must be one of the options")

        return questions

    except Exception as e:
        logger.error(f"Error generating MCQ questions: {str(e)}")
        raise ValidationError(f"Error generating questions: {str(e)}")


def generate_mcqs_from_multiple_pdfs(pdf_files, num_questions_per_pdf=10, difficulty='3', num_options=4):
    """
    Generate MCQs from multiple PDF files.

    Args:
        pdf_files: List of PDF files (can be File objects or file paths)
        num_questions_per_pdf: Number of questions to generate per PDF
        difficulty (str): Difficulty level ('1'=Very Easy, '2'=Easy, '3'=Medium, '4'=Hard, '5'=Very Hard)
        num_options (int): Number of options per question (2-4, default=4)

    Returns:
        List of dictionaries containing MCQ data
    """
    all_mcqs = []
    error_pdfs = []

    for pdf_file in pdf_files:
        try:
            # Get PDF name for logging
            pdf_name = pdf_file.name if hasattr(pdf_file, 'name') else str(pdf_file)
            logger.info(f"Processing PDF: {pdf_name}")

            # Extract text from PDF
            text = extract_text_from_pdf(pdf_file)
            if not text:
                logger.warning(f"No text extracted from PDF: {pdf_name}")
                error_pdfs.append(f"{pdf_name} (no text extracted)")
                continue

            # Check if text is too long or too short for AI processing
            if len(text) < 100:
                logger.warning(f"Text too short from PDF: {pdf_name}")
                error_pdfs.append(f"{pdf_name} (insufficient content)")
                continue

            # Limit text size to prevent API errors (some APIs have token limits)
            if len(text) > 35000:
                logger.warning(f"Text too long from PDF {pdf_name}, truncating...")
                text = text[:35000]

            # Generate MCQs from text with specified difficulty and number of options
            try:
                logger.info(f"Generating {num_questions_per_pdf} questions from PDF: {pdf_name}")
                mcqs = generate_mcqs_from_text(text, num_questions_per_pdf, difficulty=difficulty, num_options=num_options)
                if mcqs:
                    all_mcqs.extend(mcqs)
            except Exception as e:
                logger.error(f"Error generating MCQs from PDF {pdf_name}: {str(e)}")
                error_pdfs.append(f"{pdf_name} ({str(e)})")
                continue

        except Exception as e:
            pdf_name = pdf_file.name if hasattr(pdf_file, 'name') else str(pdf_file)
            logger.error(f"Error processing PDF {pdf_name}: {str(e)}")
            error_pdfs.append(f"{pdf_name} ({str(e)})")
            continue

    # Check if we were able to generate any questions
    if not all_mcqs:
        error_msg = f"Failed to generate MCQs from all PDFs: {', '.join(error_pdfs)}"
        logger.error(error_msg)

        # Return generic/sample questions as fallback if no questions were generated
        return [
            {
                "question": "This is a sample question as a fallback. Please check PDF content and try again.",
                "options": ["Option A", "Option B", "Option C", "Option D"][:num_options],
                "correct_answer": "Option A"
            }
        ]

    # Log any PDFs that had errors but we still generated some questions
    if error_pdfs:
        logger.warning(f"Some PDFs had errors: {', '.join(error_pdfs)}")

    return all_mcqs


def extract_text_from_pdf(pdf_file):
    """
    Extract text from a PDF file.

    Args:
        pdf_file: PDF file (can be File object or file path)

    Returns:
        Extracted text as string
    """
    try:
        # If it's a File object, get the path
        if hasattr(pdf_file, 'path'):
            pdf_path = pdf_file.path
        else:
            pdf_path = pdf_file

        # Extract text using PyPDF2
        text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"

        return text.strip()

    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        return None
