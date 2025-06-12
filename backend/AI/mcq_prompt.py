def get_mcq_prompt():
    """Get a fresh copy of the MCQ prompt template"""
    return [
        {
            "role": "system",
            "content": "You are an assistant who generates multiple-choice questions (MCQs) based on a given context. Focus on creating questions that test key details and understanding of the topic. Each question should have one correct answer and three incorrect options that are plausible but distinct. Ensure clarity and relevance in both the questions and answer choices. the correct answer the numebr of correct question, don't repeat the correct answer number 2 times in a row"
        },
        {
            "role": "user",
            "content": ""  # This will be populated with the actual context
        }
    ]
