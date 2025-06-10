import fitz  # PyMuPDF
from pathlib import Path

def extract_text(pdf_path: Path) -> str:
    """
    Extrae texto bruto de un PDF usando PyMuPDF.
    """
    doc = fitz.open(pdf_path)
    pages = [page.get_text() for page in doc]
    return "\n".join(pages)

def save_raw_text(input_pdf: Path, output_txt: Path):
    """
    Extrae el texto de input_pdf y lo guarda en output_txt.
    """
    raw = extract_text(input_pdf)
    output_txt.parent.mkdir(parents=True, exist_ok=True)
    with open(output_txt, "w", encoding="utf-8") as f:
        f.write(raw)
    print(f"Saved raw text to {output_txt}")

def main():
    project_root = Path.cwd()
    print(project_root)

    raw_dir = project_root/"data/raw"
    processed_dir = project_root/"data"/"processed"

    pdf_files = list(raw_dir.glob("*.pdf"))
    if not pdf_files:
        print("No PDFs found in 'data/raw'.")
        return

    for pdf_file in pdf_files:
        output_txt = processed_dir / f"{pdf_file.stem}.txt"
        print(f"Processing {pdf_file.name}...")
        save_raw_text(pdf_file, output_txt)

if __name__ == "__main__":
    main()