from huggingface_hub import InferenceClient
from django.conf import settings
import json
import re
import json5
import logging
import PyPDF2
import io

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
