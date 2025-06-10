# setup_project_structure.py

import os

folders = [
    "data",
    "src/ingestion",
    "src/embeddings",
    "src/vector_store",
    "src/llm",
    "src/ui",
    "scripts"
]

files = [
    "README.md",
    ".env",
    "src/config.py",
    "scripts/build_index.py",
    "scripts/run_app.sh",
    "pyproject.toml"
]

def create_structure():
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"✔ Created folder: {folder}")

    for file in files:
        if not os.path.exists(file):
            with open(file, "w") as f:
                f.write("")
            print(f"✔ Created file: {file}")

if __name__ == "__main__":
    create_structure()
