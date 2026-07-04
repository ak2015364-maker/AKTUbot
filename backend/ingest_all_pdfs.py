import uuid
from pathlib import Path

from services.vector_store import add_document
from utils.pdf_utils import extract_text_from_pdf
from utils.text_splitter import split_text


def ingest_all_pdfs():

    # Path to backend folder
    BASE_DIR = Path(__file__).resolve().parent

    # Path to AKTU_data folder
    BASE_FOLDER = BASE_DIR / "AKTU_data"

    print(f"\nSearching PDFs in: {BASE_FOLDER}")

    if not BASE_FOLDER.exists():
        raise FileNotFoundError(
            f"AKTU_data folder not found at {BASE_FOLDER}"
        )

    total_pdfs = 0
    total_chunks = 0

    for semester in BASE_FOLDER.iterdir():

        if not semester.is_dir():
            continue

        for subject in semester.iterdir():

            if not subject.is_dir():
                continue

            for doc_type in subject.iterdir():

                if not doc_type.is_dir():
                    continue

                for pdf_file in doc_type.iterdir():

                    if pdf_file.suffix.lower() != ".pdf":
                        continue

                    print(f"\nProcessing: {pdf_file.name}")

                    try:

                        text = extract_text_from_pdf(str(pdf_file))

                        if not text.strip():
                            print("No text extracted")
                            continue

                        chunks = split_text(text)

                        for chunk in chunks:

                            add_document(
                                doc_id=str(uuid.uuid4()),
                                text=chunk,
                                metadata={
                                    "semester": semester.name,
                                    "subject": subject.name,
                                    "type": doc_type.name,
                                    "filename": pdf_file.name
                                }
                            )

                        total_pdfs += 1
                        total_chunks += len(chunks)

                        print(f"Stored {len(chunks)} chunks")

                    except Exception as e:

                        print(
                            f"Error processing {pdf_file.name}: {e}"
                        )

    print("\n==============================")
    print("PDF Ingestion Completed")
    print("==============================")
    print(f"PDFs Processed : {total_pdfs}")
    print(f"Chunks Stored  : {total_chunks}")


if __name__ == "__main__":
    ingest_all_pdfs()