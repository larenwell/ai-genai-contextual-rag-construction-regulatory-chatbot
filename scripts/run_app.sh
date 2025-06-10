#!/usr/bin/env bash
set -euo pipefail

# 1) Activa el virtualenv
source .venv/bin/activate

# 2) Asegúrate de que Qdrant (docker) esté corriendo
#    docker start qdrant_local || true

# 3) Lanza la UI de Chainlit (o Streamlit si prefieres)
chainlit run src/ui/app.py

s