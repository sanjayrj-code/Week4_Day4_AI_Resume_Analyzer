
import fitz
from pathlib import Path

resume_folder = Path("data/resumes")

for i in range(1, 5):
    txt_file = resume_folder / f"resume_0{i}.txt"
    pdf_file = resume_folder / f"resume_0{i + 4}.pdf"

    # Read the existing text resume
    text = txt_file.read_text(encoding="utf-8")

    # Create PDF
    doc = fitz.open()
    page = doc.new_page()

    page.insert_textbox(
        fitz.Rect(50, 50, 545, 790),
        text,
        fontsize=11,
        fontname="helv",
        lineheight=1.5
    )

    doc.save(pdf_file)
    doc.close()

    print(f"Created: {pdf_file}")

print("\nAll 4 PDF resumes created successfully!")
