

import json
import os
import time
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from resume_parser import read_resume

# Load API key
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found. Check your .env file.")

client = Groq(api_key=api_key)

# Load prompt and schema
prompt_path = Path("prompts/system_prompt_v1.txt")
schema_path = Path("prompts/resume_schema.json")

prompt = prompt_path.read_text(encoding="utf-8")
schema = json.loads(schema_path.read_text(encoding="utf-8"))

# Folders
resume_folder = Path("data/resumes")
output_folder = Path("outputs")
output_folder.mkdir(exist_ok=True)

MODEL_NAME = "openai/gpt-oss-20b"
TEMPERATURE = 0
MAX_RETRIES = 3


def extract_resume_data(resume_text):
    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {
                        "role": "system",
                        "content": prompt
                    },
                    {
                        "role": "user",
                        "content": (
                            "Extract information from this resume. "
                            "Follow the required JSON schema.\n\n"
                            + resume_text
                        )
                    }
                ],
                temperature=TEMPERATURE,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "resume_extraction",
                        "strict": True,
                        "schema": schema
                    }
                }
            )

            result = response.choices[0].message.content
            return json.loads(result)

        except Exception as error:
            error_message = str(error)

            if any(code in error_message for code in ["429", "500", "502", "503", "504"]):
                print(f"Temporary API error. Attempt {attempt + 1}/{MAX_RETRIES}")

                if attempt < MAX_RETRIES - 1:
                    wait_time = 10 * (attempt + 1)
                    print(f"Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print("Maximum retries reached.")
            else:
                print(f"API error: {error}")
                return None

    return None


# Find the eight sample resumes
resume_files = sorted([
    file for file in resume_folder.iterdir()
    if file.suffix.lower() in [".pdf", ".txt"]
    and file.name.startswith("resume_")
])

print(f"Total resumes found: {len(resume_files)}")

successful = 0
failed = 0

for resume_path in resume_files:
    print("\n" + "=" * 50)
    print(f"Processing: {resume_path.name}")

    resume_text = read_resume(resume_path)

    if not resume_text:
        print("Skipped: Resume has no readable text.")
        failed += 1
        continue

    extracted_data = extract_resume_data(resume_text)

    if extracted_data is None:
        print(f"Failed: {resume_path.name}")
        failed += 1
        continue

    output_file = output_folder / (resume_path.stem + ".json")

    output_file.write_text(
        json.dumps(extracted_data, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )

    print(f"Successfully saved: {output_file}")
    print(json.dumps(extracted_data, indent=4, ensure_ascii=False))

    successful += 1

print("\n" + "=" * 50)
print("RESUME EXTRACTION SUMMARY")
print("=" * 50)
print(f"Total resumes: {len(resume_files)}")
print(f"Successful: {successful}")
print(f"Failed: {failed}")
print(f"Model: {MODEL_NAME}")
print(f"Temperature: {TEMPERATURE}")
print("JSON Schema mode: Enabled")
print(f"Output folder: {output_folder}")

print("\nResume extraction completed!")
