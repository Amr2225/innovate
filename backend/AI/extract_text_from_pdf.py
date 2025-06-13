import PyPDF2
import logging

logger = logging.getLogger(__name__)


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
