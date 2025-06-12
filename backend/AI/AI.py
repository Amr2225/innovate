from AI.AIError import AIError
from AI.baseAIClient import client
from main.settings import AI_MODEL
import logging
import re

logger = logging.getLogger(__name__)


def AI(temperature, prompt, text, max_tokens=1000, max_retries=4):
    # Add timeout and retry logic for API calls
    for attempt in range(max_retries):
        try:
            completion = client.chat.completions.create(
                model=AI_MODEL,
                messages=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            break  # Success, exit retry loop
        except Exception as api_error:
            if "Bad request" in str(api_error) and attempt < max_retries - 1:
                # If it's a "Bad request" error and not the last attempt, try with shorter context
                logger.warning(
                    f"Bad request error on attempt {attempt+1}, reducing context size and retrying...")

                # Split the text into sentences
                sentences = re.split(r'(?<=[.!?])\s+', text)

                # Calculate a reduced size based on the attempt number
                # Each retry will use fewer sentences
                # 1/2, 1/3, 1/4 of original sentences
                reduction_factor = 1.0 / (attempt + 2)

                # Calculate how many sentences to keep
                keep_count = max(
                    10, int(len(sentences) * reduction_factor))

                if len(sentences) <= keep_count:
                    # Not enough sentences to sample, just use a smaller portion
                    text = text[:int(len(text) * reduction_factor)]
                else:
                    # Take evenly distributed sentences
                    step = max(1, len(sentences) // keep_count)

                    # Always include some sentences from the beginning, middle and end
                    beginning = sentences[:min(5, len(sentences)//10)]

                    # Sample sentences from the rest of the document at regular intervals
                    sampled = sentences[min(
                        5, len(sentences)//10):len(sentences)-min(5, len(sentences)//10):step]

                    # Add some sentences from the end
                    ending = sentences[-min(5, len(sentences)//10):]

                    # Combine the samples
                    sampled_sentences = beginning + sampled + ending

                    # Join the sampled sentences back into text
                    text = ' '.join(sampled_sentences)

                logger.info(
                    f"Reduced text from {len(text)} to {len(text)} characters")

                # Update the prompt with the new text
                prompt[1]['content'] = prompt[1]['content'].replace(
                    f"context: {text}", f"context: {text}")
                continue
            else:
                # On last attempt or different error, re-raise
                raise AIError()
    return completion
