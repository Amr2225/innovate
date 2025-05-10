from huggingface_hub import InferenceClient
from django.conf import settings
import json
import re
import json5

client = InferenceClient(
    provider=settings.AI_PROVIDER,
    api_key=settings.AI_API_KEY,
)

Evaluate = [
    {
        "role": "system",
        "content": "You are a grading assistant who compares a student's answer to a key answer. Focus on content correctness and the structure of the student's answer. Ignore grammar, punctuation, or small differences in wording unless they change the meaning. If the student's answer is a numbered list, do not penalize for sentence structure. If the student's answer is unstructured, incoherent, or contains invalid information, provide appropriate feedback and adjust the score accordingly. Prioritize understanding, but ensure the student's answer follows a clear and correct structure."
    },
    {
        "role": "user",
        "content": """
        question: What is an algorithm?
        Student Answer: Set of rules to follow for solving a problem or performing a task.

        Compare the student's answer with the key answer, ignoring grammar and small differences in wording. If the student's answer is a numbered list, ignore sentence structure. Ensure the student's answer contains valid programming languages and is structured properly. If the answer is unstructured, incoherent, or contains invalid entries, give an appropriate score and provide feedback explaining why. Your response must be strictly in the following JSON format:

        {{
            "score": 10,
            "feedback": "<specific feedback about the student's answer>"
        }}
        """
    }
]

completion = client.chat.completions.create(
    model=settings.AI_MODEL,
    messages=Evaluate,
    temperature=1,
    max_tokens=500,
)


def extract_json(llm_output):
    # Match first JSON object/array in string
    json_match = re.search(r'({.*}|\[.*\])', llm_output, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    raise ValueError("No valid JSON found")


print(completion.choices[0].message)
print(completion.choices[0].message.content)

try:
    print(json.loads(completion.choices[0].message.content))
except:
    print("Error loading json")


data = completion.choices[0].message.content

try:
    json3 = json5.loads(data)
    print("json3", json3)
    print("extract json", extract_json(data))
    match = re.search(r"\{([\s\S]*?)\}", data)

    if match:
        # Remove leading/trailing spaces
        extracted_content = match.group(1).strip()
        print("match", extracted_content)
    # Splitting into separate steps using newlines and removing empty items
    steps = [re.sub(r"^\d+\s*[-.]\s*", "", step.strip())
             for step in data["text"].split("\n") if step.strip()]

    # Structuring the JSON
    structured_data = {"steps": steps}

    # Convert to JSON string
    json_output = json.dumps(structured_data, indent=2)
except:
    print("REGEX failed")
