import re
from pathlib import Path

# Lista de líneas de cabecera que aparecen en cada página
REPEATED_HEADERS = {
    "Sistema Normativo de Información Laboral",
    "Dirección de Capacitación y Difusión Laboral"
}

def clean_text(raw: str) -> str:
    """
    Limpia el texto extraído de un PDF:
    1) Elimina líneas vacías o solo dígitos (números de página).
    2) Descarta separadores largos de guiones o guiones bajos.
    3) Elimina repeticiones de cabeceras definidas en REPEATED_HEADERS.
    4) Junta líneas partidas en párrafos.
    5) Colapsa saltos de línea múltiples y normaliza espacios.
    """
    lines = raw.splitlines()
    cleaned_lines = []
    seen_headers = set()

    for line in lines:
        s = line.strip()
        # 1) Saltar líneas vacías o de solo dígitos (números de página).
        if not s or re.fullmatch(r"\d+", s):
            continue
        # 2) Saltar separadores (_______, ------, etc.)
        if re.fullmatch(r"[_─\-=]{3,}", s):
            continue
        # 3) Saltar cabeceras repetidas
        if s in REPEATED_HEADERS:
            # registra la primera aparición, ignora las siguientes
            if s in seen_headers:
                continue
            seen_headers.add(s)
        cleaned_lines.append(s)

    # 4) Unir líneas partidas en párrafos si la línea previa no acaba en . ? ! :
    text = ""
    for line in cleaned_lines:
        if text and not re.search(r"[\.?!:]$", text):
            text = text.rstrip() + " " + line.lstrip()
        else:
            text += "\n" + line

    # 5) Colapsar saltos de línea múltiples y espacios
    text = re.sub(r"\n{2,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)

    return text.strip()
def save_clean_text(input_txt: Path, output_txt: Path):
    """
    Lee un .txt “raw”, lo limpia y guarda en output_txt.
    """
    raw = input_txt.read_text(encoding="utf-8")
    cleaned = clean_text(raw)
    output_txt.parent.mkdir(parents=True, exist_ok=True)
    output_txt.write_text(cleaned, encoding="utf-8")
    print(f"Saved cleaned text to {output_txt}")

def main():
    project_root = Path.cwd()
    processed_dir = project_root/"data"/"processed"
    clean_dir = project_root/"data"/"cleaned"
    clean_dir.mkdir(parents=True, exist_ok=True)

    txt_files = list(processed_dir.glob("*.txt"))
    if not txt_files:
        print("No TXTs found in 'data/processed'.")
        return

    for txt_file in txt_files:
        out_file = clean_dir/txt_file.name
        print(f"Cleaning {txt_file.name}...")
        save_clean_text(txt_file, out_file)

if __name__ == "__main__":
    main()
