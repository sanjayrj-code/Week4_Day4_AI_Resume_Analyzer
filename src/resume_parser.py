
import fitz
import re
from pathlib import Path
import tiktoken


def clean_text(text):
    # Remove extra spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Remove standalone page numbers
    text = re.sub(r"(?m)^\s*Page\s+\d+\s*$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"(?m)^\s*\d+\s*$", "", text)

    # Remove excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def read_resume(path):
    path = Path(path)

    try:
        if path.suffix.lower() == ".pdf":
            doc = fitz.open(path)

            text = ""
            for page in doc:
                text += page.get_text() + "\n"

            doc.close()

            if not text.strip():
                print(f"{path.name}: Error - no text found (scanned or empty PDF)")
                return None

        elif path.suffix.lower() == ".txt":
            text = path.read_text(encoding="utf-8")

        else:
            print(f"{path.name}: Error - unsupported file format")
            return None

        text = clean_text(text)

        if not text:
            print(f"{path.name}: Error - empty resume")
            return None

        return text

    except Exception as e:
        print(f"{path.name}: Error - {e}")
        return None


def count_tokens(text):
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


# Process all resumes
resume_folder = Path("data/resumes")

for resume_path in sorted(resume_folder.iterdir()):
    if resume_path.suffix.lower() in [".pdf", ".txt"]:

        resume_text = read_resume(resume_path)

        if resume_text:
            characters = len(resume_text)
            tokens = count_tokens(resume_text)

            print(
                f"{resume_path.name}: "
                f"{characters} characters, {tokens} tokens"
            )
