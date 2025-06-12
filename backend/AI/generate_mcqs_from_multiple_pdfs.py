from AI.extract_text_from_pdf import extract_text_from_pdf
from AI.generate_mcq_from_text import generate_mcqs_from_text
import logging

logger = logging.getLogger(__name__)


def generate_mcqs_from_multiple_pdfs(pdf_files, number_of_questions=10, difficulty='3', num_options=4):
    """
    Generate MCQs from multiple PDF files.

    Args:
        pdf_files: List of PDF files (can be File objects or file paths)
        number_of_questions: Number of questions to generate
        difficulty (str): Difficulty level ('1'=Very Easy, '2'=Easy, '3'=Medium, '4'=Hard, '5'=Very Hard)
        num_options (int): Number of options per question (2-4, default=4)

    Returns:
        List of dictionaries containing MCQ data
    """
    print("Generating MCQs from multiple PDFs")
    all_mcqs = []
    error_pdfs = []

    for pdf_file in pdf_files:
        try:
            # Get PDF name for logging
            pdf_name = pdf_file.name if hasattr(
                pdf_file, 'name') else str(pdf_file)
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
                logger.warning(
                    f"Text too long from PDF {pdf_name}, truncating...")
                text = text[:35000]

            # Generate MCQs from text with specified difficulty and number of options
            try:
                logger.info(
                    f"Generating {number_of_questions} questions from PDF: {pdf_name}")
                mcqs = generate_mcqs_from_text(
                    text, number_of_questions, difficulty=difficulty, num_options=num_options)
                if mcqs:
                    all_mcqs.extend(mcqs)
            except Exception as e:
                logger.error(
                    f"Error generating MCQs from PDF {pdf_name}: {str(e)}")
                error_pdfs.append(f"{pdf_name} ({str(e)})")
                continue

        except Exception as e:
            pdf_name = pdf_file.name if hasattr(
                pdf_file, 'name') else str(pdf_file)
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
