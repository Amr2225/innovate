import logging
from huggingface_hub import InferenceClient
from main.settings import AI_PROVIDER, AI_API_KEY

# Set up logging
logger = logging.getLogger(__name__)

try:
    client = InferenceClient(
        provider=AI_PROVIDER,
        api_key=AI_API_KEY,
    )
except Exception as e:
    logger.error(f"Failed to initialize AI client: {str(e)}")
    raise
