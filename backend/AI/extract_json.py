import re
import json
import json5
import logging

logger = logging.getLogger(__name__)


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
