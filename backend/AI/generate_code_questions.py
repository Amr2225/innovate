# from main.settings import AI_MODEL
import json
import re
import json5
import logging
import PyPDF2
import io
import base64
from PIL import Image
from django.conf import settings
from huggingface_hub import InferenceClient

logger = logging.getLogger(__name__)


def generate_coding_questions_from_pdf(pdf_file, num_questions=5, difficulty='3', language_id='python3'):
    """
    Extract text from PDF and generate coding questions using AI
    Args:
        pdf_file: InMemoryUploadedFile or path to PDF file
        num_questions (int): Number of questions to generate
        difficulty (str): Difficulty level ('1'=Very Easy, '2'=Easy, '3'=Medium, '4'=Hard, '5'=Very Hard)
        language_id (str): Programming language ID (default: 'python3')
    Returns:
        list: List of coding question dictionaries with test cases
    """
    try:
        # First extract text from the PDF
        text = extract_text_from_pdf(pdf_file)
        
        # Then generate coding questions from the extracted text
        return generate_coding_questions_from_text(text, num_questions, difficulty, language_id)
        
    except Exception as e:
        logger.error(f"Failed to generate coding questions from PDF: {str(e)}")
        raise ValueError(f"Failed to generate coding questions from PDF: {str(e)}")

def generate_coding_questions_from_text(text, num_questions=5, difficulty='3', language_id='python3'):
    """
    Generate coding questions from text using AI
    Args:
        text (str): Input text to generate questions from
        num_questions (int): Number of questions to generate
        difficulty (str): Difficulty level ('1'=Very Easy, '2'=Easy, '3'=Medium, '4'=Hard, '5'=Very Hard)
        language_id (str): Programming language ID (default: 'python3')
    Returns:
        list: List of coding question dictionaries with test cases
    """
    try:
        logger.info(f"Generating {num_questions} coding questions from text with difficulty level {difficulty}")
        
        # Map difficulty level to description
        difficulty_map = {
            '1': 'Very Easy',
            '2': 'Easy',
            '3': 'Medium',
            '4': 'Hard',
            '5': 'Very Hard'
        }
        difficulty_desc = difficulty_map.get(difficulty, 'Medium')
        
        # Map language ID to name
        language_map = {
            'python3': 'Python 3',
            'java': 'Java',
            'c': 'C',
            'cpp': 'C++',
            'csharp': 'C#',
            'javascript': 'JavaScript',
            'typescript': 'TypeScript',
            'php': 'PHP'
        }
        language_name = language_map.get(language_id, 'Python 3')
        
        # Prepare the prompt for coding questions
        prompt = [
            {
                "role": "system",
                "content": """You are an expert programming instructor who creates coding questions. 
                Your task is to generate clear, well-structured coding questions with appropriate test cases.
                Each question should include:
                1. A clear title
                2. A detailed description of the problem
                3. A function signature that students need to implement
                4. At least 3 test cases (mix of public and private)
                
                The questions should be appropriate for the specified difficulty level and programming language.
                You MUST return ONLY a valid JSON array, nothing else."""
            },
            {
                "role": "user",
                "content": f"""
                Based on the following context, generate {num_questions} coding questions in {language_name}.
                Difficulty level: {difficulty_desc}
                
                Context:
                {text}
                
                You MUST return ONLY a valid JSON array in this exact format:
                [
                    {{
                        "title": "Question title",
                        "description": "Detailed problem description",
                        "function_signature": "def function_name(param1, param2):",
                        "test_cases": [
                            {{
                                "input_data": [\"input1\"],  # Can be any length array
                                "expected_output": "output1",
                                "is_public": true
                            }},
                            {{
                                "input_data": [\"input1\", \"input2\", \"input3\"],  # Example with 3 inputs
                                "expected_output": "output2",
                                "is_public": false
                            }},
                            {{
                                "input_data": [\"input1\", \"input2\"],  # Example with 2 inputs
                                "expected_output": "output3",
                                "is_public": true
                            }}
                        ]
                    }}
                ]
                
                Requirements:
                1. Questions must be relevant to the context
                2. Function signatures must be valid for {language_name}
                3. Test cases must cover edge cases and normal scenarios
                4. At least one test case should be public (is_public: true)
                5. Questions should match the {difficulty_desc} difficulty level
                6. Return ONLY the JSON array, no other text or explanation
                7. Ensure all JSON is properly formatted with double quotes
                8. Do not include any markdown formatting or code blocks
                9. input_data array can have any number of elements (1 or more)
                10. Make sure test cases have consistent input_data array lengths for each question
                """
            }
        ]
        
        # Adjust temperature based on difficulty
        temperature_map = {
            '1': 0.7,  # Lower temperature for more consistent, easier questions
            '2': 0.75,
            '3': 0.8,
            '4': 0.85,
            '5': 0.9   # Higher temperature for more creative, harder questions
        }
        temperature = temperature_map.get(difficulty, 0.5)

        # Make API call to generate coding questions
        logger.debug(f"Making API call to generate coding questions with difficulty {difficulty_desc}")
        completion = client.chat.completions.create(
            model=settings.AI_MODEL,
            messages=prompt,
            temperature=temperature,
            max_tokens=1000,
        )

        # Get the response content
        response_content = completion.choices[0].message.content.strip()
        
        # Clean the response content
        cleaned_content = response_content
        # Remove any markdown code block markers
        cleaned_content = re.sub(r'```json\s*|\s*```', '', cleaned_content)
        # Remove any leading/trailing whitespace
        cleaned_content = cleaned_content.strip()
        
        # Try to parse JSON
        try:
            questions_data = json.loads(cleaned_content)
        except json.JSONDecodeError as e:
            logger.error(f"Initial JSON parsing failed: {str(e)}")
            # Try to extract JSON array using regex
            json_match = re.search(r'(\[.*\])', cleaned_content, re.DOTALL)
            if json_match:
                try:
                    questions_data = json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    # Try json5 as last resort
                    try:
                        questions_data = json5.loads(json_match.group(1))
                    except Exception as json5_error:
                        logger.error(f"JSON5 parsing failed: {str(json5_error)}")
                        raise ValueError("Failed to parse AI response as JSON")
            else:
                raise ValueError("No valid JSON array found in response")
        
        if not isinstance(questions_data, list):
            logger.error("Invalid response format: not a list")
            raise ValueError("Invalid response format from AI")
            
        # Validate each question
        logger.debug("Validating coding question data")
        for i, q in enumerate(questions_data):
            if not isinstance(q, dict):
                logger.error(f"Invalid question format at index {i}")
                raise ValueError("Invalid question format in AI response")
                
            required_fields = ['title', 'description', 'function_signature', 'test_cases']
            if not all(key in q for key in required_fields):
                logger.error(f"Missing required fields in question at index {i}")
                raise ValueError("Missing required fields in AI response")
                
            if not isinstance(q['test_cases'], list) or len(q['test_cases']) < 3:
                logger.error(f"Invalid test cases format in question at index {i}")
                raise ValueError("Each question must have at least 3 test cases")
                
            for tc in q['test_cases']:
                if not all(key in tc for key in ['input_data', 'expected_output', 'is_public']):
                    logger.error(f"Invalid test case format in question at index {i}")
                    raise ValueError("Invalid test case format in AI response")

        logger.info(f"Successfully generated {len(questions_data)} coding questions at {difficulty_desc} difficulty")
        return questions_data[:num_questions]

    except Exception as e:
        logger.error(f"Coding question generation error: {str(e)}")
        raise ValueError(f"Failed to generate coding questions: {str(e)}")
