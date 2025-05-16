import base64
from huggingface_hub import InferenceClient
from django.conf import settings
import json
import re
import json5

client = InferenceClient(
    provider=settings.AI_PROVIDER,
    api_key=settings.AI_API_KEY,
)


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


image = [
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": """
                    What is written in this image give me only what is written
                    Generate output in JSON format. Follow these rules:
                    1. Only use double quotes
                    2. No trailing commas
                    3. No comments
                    4. NEVER Wrap in ```json delimiters


                    Example:
                    {{
                        "text": [
                            <What is written in the image>
                        ]
                    }}
                """
            },
            {
                "type": "image_url",
                "image_url": {
                    # "url": "https://cdn.britannica.com/61/93061-050-99147DCE/Statue-of-Liberty-Island-New-York-Bay.jpg"
                    "url": f"data:image/jpeg;base64,{encode_image('handwrite.jpg')}"
                    # "url": f"data:image/jpeg;base64,{encode_image(images[0])}"
                }
            }
        ]
    }
]

completion = client.chat.completions.create(
    model=settings.AI_MODEL,
    messages=image,
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
