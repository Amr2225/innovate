import requests
import time

JUDGE0_URL = "https://judge0-ce.p.rapidapi.com/submissions"
HEADERS = {
    "x-rapidapi-host": "judge0-ce.p.rapidapi.com",
    "x-rapidapi-key": "4d2588f7c0msh11d6e530ad01272p1c497djsn010c093327ce",
    "content-type": "application/json"
}

def run_code(source_code, stdin, language_id):
    # 1. Submit the code
    submission = {
        "source_code": source_code,
        "stdin": stdin,
        "language_id": language_id
    }

    res = requests.post(JUDGE0_URL, json=submission, headers=HEADERS)
    token = res.json().get("token")

    if not token:
        return {"error": "Submission failed"}

    # 2. Poll the result
    result_url = f"{JUDGE0_URL}/{token}"
    while True:
        result = requests.get(result_url, headers=HEADERS, params={"base64_encoded": "false"}).json()
        if result.get("status", {}).get("description") in ["Accepted", "Wrong Answer", "Compilation Error", "Runtime Error (NZEC)"]:
            break
        time.sleep(1)  # Wait a bit before polling again

    return result

