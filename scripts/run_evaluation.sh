#!/usr/bin/env bash
set -euo pipefail

# Si usas virtualenv creado con uv/venv:
source .venv/bin/activate

echo "🔎 Iniciando evaluación RAG…"
python src/evaluation/evaluate_rag.py
