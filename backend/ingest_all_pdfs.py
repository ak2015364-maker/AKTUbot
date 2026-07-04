import os
import uuid

from services.vector_store import add_document
from utils.pdf_utils import extract_text_from_pdf
from utils.text_splitter import split_text

BASE_FOLDER = r"C:\Users\kumar\OneDrive\Desktop\AKTU_Data"

for semester in os.listdir(BASE_FOLDER):

    semester_path = os.path.join(BASE_FOLDER, semester)

    if not os.path.isdir(semester_path):
        continue

    for subject in os.listdir(semester_path):

        subject_path = os.path.join(semester_path, subject)

        if not os.path.isdir(subject_path):
            continue

        for doc_type in os.listdir(subject_path):

            doc_type_path = os.path.join(subject_path, doc_type)

            if not os.path.isdir(doc_type_path):
                continue

            for filename in os.listdir(doc_type_path):

                if not filename.lower().endswith(".pdf"):
                    continue

                pdf_path = os.path.join(doc_type_path, filename)

                print(f"\nProcessing: {filename}")

                try:
                    text = extract_text_from_pdf(pdf_path)

                    if not text.strip():
                        print("No text extracted")
                        continue

                    chunks = split_text(text)

                    for chunk in chunks:

                        add_document(
                            doc_id=str(uuid.uuid4()),
                            text=chunk,
                            metadata={
                                "semester": semester,
                                "subject": subject,
                                "type": doc_type,
                                "filename": filename
                            }
                        )

                    print(f"Stored {len(chunks)} chunks")

                except Exception as e:
                    print(f"Error: {e}")

print("\nFinished Ingestion")