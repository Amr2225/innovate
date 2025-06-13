from AI.extract_json import extract_json
from AI.mcq_prompt import get_mcq_prompt
from AI.AI import AI
import logging
from AI.AIError import AIError


logger = logging.getLogger(__name__)


def generate_mcqs_from_text(text, number_of_questions=10, difficulty='3', num_options=4):
    logger.info(
        f"Generating {number_of_questions} MCQs from text with difficulty level {difficulty} and {num_options} options per question")
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
        logger.info(
            f"Generating {number_of_questions} MCQs from text with difficulty level {difficulty} and {num_options} options per question")

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
        # Increased from 5000 to match the limit in generate_mcqs_from_multiple_pdfs
        max_text_length = 35000
        if len(text) > max_text_length:
            logger.warning(
                f"Text length ({len(text)}) exceeds maximum ({max_text_length}). Truncating...")
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

        Based on the provided context, generate {number_of_questions} multiple-choice questions at {difficulty_desc} difficulty level. Your response must be strictly in the following JSON format:

        [{{"question": "<question text>",
          "options": ["<option 1>", "<option 2>", "<option 3>", "<option 4>", "<option 5>", "<option 6>"],
          "correct_answer": "<exact text of the correct option>"}}]

        CRITICAL REQUIREMENTS:
        1. Return ONLY the JSON array, no other text
        2. VERY IMPORTANT: Ensure that the response is in the JSON format.
        3. Double check that the response is in the JSON format.
        4. Ensure the number of questions is {number_of_questions} - no more, no less
        5. VERY IMPORTANT: Ensure the number of questions is {number_of_questions} - no more, no less
        6. Double check the number of questions is {number_of_questions} - no more, no less
        7. Each question MUST have EXACTLY {num_options} options - no more, no less
        8. Double check the number of options is {num_options} - no more, no less
        9. The correct_answer MUST match EXACTLY one of the options
        10. you MUST Double check the correct answer is in the options
        11. Each option MUST be a string
        12. The options array MUST contain EXACTLY {num_options} strings
        13. Do not include any explanations or additional text
        14. Ensure the JSON is valid and properly formatted
        15. Use double quotes for all strings
        16. Do not include any trailing commas
        17. Do not include any comments or markdown formatting
        18. IMPORTANT: You MUST generate EXACTLY {num_options} options for each question

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
        logger.debug(
            f"Making API call to generate MCQs with difficulty {difficulty_desc} and {num_options} options")

        # Make API call to generate MCQs with difficulty-adjusted parameters
        max_retries = 4
        max_tokens = 1000
        completion = AI(temperature, prompt, text,
                        max_tokens=max_tokens, max_retries=max_retries)

        logger.debug("Extracting JSON from AI response")
        for attempt in range(max_retries):
            try:
                mcq_data = extract_json(completion.choices[0].message.content)
                break
            except Exception as json_error:
                if attempt < max_retries - 1:
                    logger.warning(
                        f"Error extracting JSON from AI response: {str(json_error)}. Retrying...")
                    continue
                raise AIError()

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
                logger.warning(
                    f"Question has {len(mcq['options'])} options instead of {num_options}, adjusting...")
                # If too many options, truncate
                if len(mcq['options']) > num_options:
                    mcq['options'] = mcq['options'][:num_options]
                # If too few options, add more
                while len(mcq['options']) < num_options:
                    mcq['options'].append(
                        f"Option {chr(65 + len(mcq['options']))}")

        logger.info(
            f"Successfully generated {len(mcq_data)} MCQs at {difficulty_desc} difficulty with {num_options} options each")
        return mcq_data[:number_of_questions]

    except Exception as e:
        logger.error(f"MCQ generation error: {str(e)}")
        raise ValueError(f"Failed to generate MCQs: {str(e)}")
