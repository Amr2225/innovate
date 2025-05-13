from huggingface_hub import InferenceClient
from django.conf import settings
import json
import re
import json5


client = InferenceClient(
    provider=settings.AI_PROVIDER,
    api_key=settings.AI_API_KEY,
)

dmcq = [
    {
        "role": "system",
        "content": "You are an assistant who generates multiple-choice questions (MCQs) based on a given context. Focus on creating questions that test key details and understanding of the topic. Each question should have one correct answer and three incorrect options that are plausible but distinct. Ensure clarity and relevance in both the questions and answer choices. For the correct_answer field, provide the actual text of the correct option, not just its index number."
    },
    {
        "role": "user",
        "content": """
        context: FTP (File Transfer Protocol) is a standard network protocol used for transferring files between a client and a server over a network. FTP operates on a client-server model, where the client can upload or download files from the server. It typically uses Port 21 for control commands and Port 20 for data transfer. FTP is considered insecure because it transmits data in plain text, making alternatives like SFTP (Secure FTP) or FTPS (FTP Secure) preferable for sensitive data.

        Based on the provided context, generate 10 multiple-choice questions. Your response must be strictly in the following JSON format:

        [{
            "question": "<question text>",
            "options": ["<option 1>", "<option 2>", "<option 3>", "<option 4>"],
            "correct_answer": "<exact text of the correct option>"
        }]
        """
    }
]

completion = client.chat.completions.create(
    model=settings.AI_MODEL,
    messages=dmcq,
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
